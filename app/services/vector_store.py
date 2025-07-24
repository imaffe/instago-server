from typing import List, Optional

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorService:
    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.dimension = 1536  # OpenAI embedding dimension
        self.connected = False
        self.collection = None

        # Only connect if Milvus host is properly configured
        milvus_host = settings.MILVUS_HOST
        if milvus_host and isinstance(milvus_host, str):
            try:
                self._connect()
                self._create_collection()
                self.connected = True
            except Exception as e:
                logger.error(f"Milvus connection failed, vector search will be disabled: {e}")
                logger.exception("Full stack trace for Milvus connection failure:")
                self.connected = False
        else:
            logger.warning("Milvus host not configured, vector search will be disabled")

    def _connect(self):
        try:
            connections.connect(
                alias="default",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            logger.info("Connected to Milvus")
        except Exception as e:
            logger.exception(f"Failed to connect to Milvus: {e}")
            raise

    def _create_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="entity_id", dtype=DataType.VARCHAR, max_length=100),  # screenshot_id or query_id
                FieldSchema(name="entity_type", dtype=DataType.VARCHAR, max_length=20),  # "screenshot" or "query"
                FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]

            schema = CollectionSchema(
                fields=fields,
                description="Embeddings for screenshots and queries"
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
        return self.add_entity(screenshot_id, "screenshot", embedding, user_id)

    def add_query(self, query_id: str, embedding: List[float], user_id: str) -> str:
        return self.add_entity(query_id, "query", embedding, user_id)

    def add_entity(self, entity_id: str, entity_type: str, embedding: List[float], user_id: str = None) -> str:
        if not self.connected:
            logger.warning("Milvus not connected, skipping vector storage")
            return "not-stored"

        try:
            import uuid
            vector_id = str(uuid.uuid4())

            data = [
                [vector_id],
                [entity_id],
                [entity_type],
                [user_id or ""],
                [embedding]
            ]

            self.collection.insert(data)
            self.collection.flush()

            logger.info(f"Added vector for {entity_type} {entity_id}")
            return vector_id

        except Exception as e:
            logger.error(f"Error adding {entity_type} to vector store: {e}")
            raise

    def search_screenshots(
        self,
        query_embedding: List[float],
        user_ids: List[str],
        limit: int = 20
    ) -> List[dict]:
        if not self.connected:
            logger.warning("Milvus not connected, returning empty results")
            return []

        try:
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }

            user_expr = f"user_id in {user_ids}" if len(user_ids) > 1 else f'user_id == "{user_ids[0]}"'
            expr = f'({user_expr}) and (entity_type == "screenshot")'

            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=["entity_id", "user_id"]
            )

            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "screenshot_id": hit.entity.get("entity_id"),
                        "user_id": hit.entity.get("user_id"),
                        "score": hit.score
                    })

            return search_results

        except Exception as e:
            logger.error(f"Error searching screenshots: {e}")
            return []

    def delete_screenshot(self, vector_id: str):
        if not self.connected:
            logger.warning("Milvus not connected, skipping deletion")
            return

        try:
            self.collection.delete(f'id == "{vector_id}"')
            self.collection.flush()
            logger.info(f"Deleted vector {vector_id}")
        except Exception as e:
            logger.error(f"Error deleting screenshot from vector store: {e}")


vector_service = VectorService()
