"""
Screenshot processing service
Handles the complete workflow of processing screenshots including storage, AI analysis, and database updates
"""
import asyncio
import base64
import json
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.models import Screenshot
from app.models.schemas import ScreenshotCreate
from app.services.storage import storage_service
from app.services.vector_store import vector_service
from app.services.embedding import embedding_service
from app.llm_calls.gemini_ocr_llm import GeminiOCRLLM
from app.agents.claude_agent import ClaudeAgent
from app.llm_calls import structure_output_llm

logger = get_logger(__name__)


class ScreenshotProcessingService:
    """Service for processing screenshots through the complete pipeline"""

    def __init__(self):
        self.ocr_agent = GeminiOCRLLM()
        self.claude_agent = ClaudeAgent()

    def process_screenshot_async(self, user_id: str, screenshot_data: ScreenshotCreate) -> None:
        """
        Main entry point for async screenshot processing
        This method orchestrates the entire screenshot processing pipeline
        """
        db = None
        try:
            # Step 1: Initialize database session
            db = SessionLocal()

            # Step 2: Upload to storage and create database record
            screenshot = self._create_screenshot_record(db, user_id, screenshot_data)
            screenshot_id = str(screenshot.id)
            logger.info(f"Created screenshot record {screenshot_id} for user {user_id}")

            # Step 3: Run OCR to extract text and structure
            try:
                ocr_result = self._run_ocr_analysis(screenshot_data.screenshotFileBlob)
            except Exception as e:
                logger.error(f"Error in OCR analysis: {e}")
                self._mark_screenshot_error(db, screenshot)
                return

            # Step 4: Find sources and enrich with Claude
            try:
                # For testing: use Tencent agent instead of Claude
                # markdown_output = self._find_sources_with_claude(ocr_result)
                markdown_output = self._find_sources_with_tencent(ocr_result)
            except Exception as e:
                logger.error(f"Error finding sources with agent: {e}")
                self._mark_screenshot_error(db, screenshot)
                return

            # Step 5: Extract structured data from markdown
            try:
                structured_data = self._extract_structured_data(markdown_output)
            except Exception as e:
                logger.error(f"Error extracting structured data: {e}")
                self._mark_screenshot_error(db, screenshot)
                return

            # Step 6: Process and prepare metadata
            metadata = self._prepare_metadata(ocr_result, structured_data)

            # Step 7: Generate embeddings for search
            vector_id = self._generate_and_store_embeddings(
                screenshot_id,
                user_id,
                metadata['title'],
                metadata['description'],
                metadata['tags'],
                markdown_output
            )

            # Step 8: Update screenshot record with processed data
            self._update_screenshot_record(
                db,
                screenshot,
                metadata,
                markdown_output,
                vector_id,
                structured_data
            )

            logger.info(f"Successfully processed screenshot {screenshot_id}")

        except Exception as e:
            logger.exception(f"Error processing screenshot: {e}")
            # If we have a screenshot record, mark it as error
            if db and screenshot:
                try:
                    screenshot.process_status = "error"
                    db.commit()
                except Exception as update_error:
                    logger.error(f"Failed to update error status: {update_error}")
        finally:
            if db:
                db.close()

    def _mark_screenshot_error(self, db: Session, screenshot: Screenshot) -> None:
        """Mark screenshot as error in database"""
        try:
            screenshot.process_status = "error"
            db.commit()
            logger.info(f"Marked screenshot {screenshot.id} as error")
        except Exception as e:
            logger.error(f"Failed to mark screenshot as error: {e}")

    def _create_screenshot_record(self, db: Session, user_id: str, screenshot_data: ScreenshotCreate) -> Screenshot:
        """
        Step 2: Upload screenshot to storage and create database record
        """
        # Decode base64 content
        content = base64.b64decode(screenshot_data.screenshotFileBlob)
        content_type = "image/png"

        # Use asyncio to run the async upload function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Upload to storage and get URLs
        image_url, thumbnail_url, metadata = loop.run_until_complete(
            storage_service.upload_screenshot(content, user_id, content_type)
        )

        # Convert Unix timestamp to datetime
        screenshot_time = datetime.fromtimestamp(screenshot_data.screenshotTimestamp, tz=timezone.utc)

        # Create screenshot record
        screenshot = Screenshot(
            user_id=user_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            width=metadata["width"],
            height=metadata["height"],
            file_size=metadata["file_size"],
            user_note=f"{screenshot_data.screenshotAppName}: {screenshot_data.screenshotTags}",
            created_at=screenshot_time,
            process_status="pending"
        )

        db.add(screenshot)
        db.commit()
        db.refresh(screenshot)

        return screenshot

    def _run_ocr_analysis(self, base64_content: str) -> Dict:
        """
        Step 3: Run OCR analysis using Gemini
        """
        logger.info("Running OCR analysis with Gemini")
        result = self.ocr_agent.process_screenshot(base64_content)
        logger.info(f"OCR agent result: {json.dumps(result, indent=2)}")
        return result

    def _find_sources_with_claude(self, ocr_result: Dict) -> str:
        """
        Step 4: Use Claude to find sources and generate enriched markdown
        """
        logger.info("Finding sources with Claude agent")
        markdown_output = self.claude_agent.find_screenshot_source_sync(ocr_result)
        return markdown_output

    def _find_sources_with_tencent(self, ocr_result: Dict) -> str:
        """
        Alternative method: Use Tencent agent to find sources and generate enriched markdown
        """
        logger.info("Finding sources with Tencent agent")
        from app.agents.tencent_agent import tencent_agent

        try:
            # Pass OCR result as img_content to Tencent workflow
            query = "图片出处"  # Query for image source
            ocr_content = json.dumps(ocr_result, ensure_ascii=False)

            response = tencent_agent.process_query(
                query=query,
                img_content=ocr_content
            )

            # Parse the JSON list response and get first item
            response_list = json.loads(response)
            first_result = response_list[0]

            # Convert first result to string for extraction
            markdown_output = json.dumps(first_result, ensure_ascii=False)
            logger.info(f"Selected first search result")
            return markdown_output

        except Exception as e:
            logger.error(f"Tencent agent error: {e}")
            # Fallback to a simple markdown format
            return f"# {ocr_result.get('application', 'Screenshot')}\n\n{ocr_result.get('text_content', '')}"

    def _extract_structured_data(self, markdown_output: str) -> Dict:
        """
        Step 5: Extract structured data (title, quick_link, error) from markdown
        """
        logger.info("Extracting structured data from markdown")
        return structure_output_llm.extract_structured_data(markdown_output)

    def _prepare_metadata(self, ocr_result: Dict, structured_data: Dict) -> Dict:
        """
        Step 6: Prepare metadata from OCR results and structured data
        """
        # Extract title
        title = structured_data.get('title', ocr_result.get('application', 'Screenshot'))

        # Extract description
        description = ocr_result.get('general_description', '')

        # Extract tags from parts data
        tags = []
        for part in ocr_result.get('parts', []):
            for content in part.get('contents', []):
                key = content.get('key', '').lower()
                if 'tag' in key or 'category' in key or 'type' in key:
                    tags.append(content.get('value', ''))

        # If no tags found, use application as a tag
        if not tags and ocr_result.get('application'):
            tags = [ocr_result['application']]

        return {
            'title': title,
            'description': description,
            'tags': tags,
            'has_error': structured_data.get('error', False)
        }

    def _generate_and_store_embeddings(
        self,
        screenshot_id: str,
        user_id: str,
        title: str,
        description: str,
        tags: list,
        markdown: str
    ) -> str:
        """
        Step 7: Generate embeddings and store in vector database
        """
        logger.info(f"Generating embeddings for screenshot {screenshot_id}")

        embedding = embedding_service.generate_embedding_from_screenshot_data(
            title=title,
            description=description,
            tags=tags,
            markdown=markdown
        )

        vector_id = vector_service.add_screenshot(screenshot_id, embedding, user_id)
        return vector_id

    def _update_screenshot_record(
        self,
        db: Session,
        screenshot: Screenshot,
        metadata: Dict,
        markdown_output: str,
        vector_id: str,
        structured_data: Dict
    ) -> None:
        """
        Step 8: Update screenshot record with all processed data
        """
        screenshot.ai_title = metadata['title']
        screenshot.ai_description = metadata['description']
        screenshot.ai_tags = json.dumps(metadata['tags'])
        screenshot.markdown_content = markdown_output
        screenshot.vector_id = vector_id
        screenshot.quick_link = structured_data.get('quick_link', {})

        # Set process_status based on whether there was an error
        if metadata['has_error']:
            screenshot.process_status = "error"
            logger.warning(f"Screenshot {screenshot.id} processed with errors")
        else:
            screenshot.process_status = "processed"

        db.commit()


# Create a singleton instance
screenshot_processing_service = ScreenshotProcessingService()
