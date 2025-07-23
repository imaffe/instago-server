from typing import List, Optional

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorService:
    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.dimension = 1536  # OpenAI embedding dimension
        self._connect()
        self._create_collection()
    
    def _connect(self):
        try:
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT
            )
            logger.info("Connected to Milvus")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _create_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="screenshot_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="Screenshot embeddings for semantic search"
            )
            
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )
            
            index_params = {
                "metric_type": "IP",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info(f"Created new collection: {self.collection_name}")
        
        self.collection.load()
    
    def add_screenshot(self, screenshot_id: str, embedding: List[float], user_id: str = None) -> str:
        try:
            import uuid
            vector_id = str(uuid.uuid4())
            
            data = [
                [vector_id],
                [screenshot_id],
                [user_id or ""],
                [embedding]
            ]
            
            self.collection.insert(data)
            self.collection.flush()
            
            logger.info(f"Added vector for screenshot {screenshot_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding screenshot to vector store: {e}")
            raise
    
    def search_screenshots(
        self, 
        query_embedding: List[float], 
        user_ids: List[str],
        limit: int = 20
    ) -> List[dict]:
        try:
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            expr = f"user_id in {user_ids}" if len(user_ids) > 1 else f'user_id == "{user_ids[0]}"'
            
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=["screenshot_id", "user_id"]
            )
            
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "screenshot_id": hit.entity.get("screenshot_id"),
                        "user_id": hit.entity.get("user_id"),
                        "score": hit.score
                    })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching screenshots: {e}")
            return []
    
    def delete_screenshot(self, vector_id: str):
        try:
            self.collection.delete(f'id == "{vector_id}"')
            self.collection.flush()
            logger.info(f"Deleted vector {vector_id}")
        except Exception as e:
            logger.error(f"Error deleting screenshot from vector store: {e}")


vector_service = VectorService()