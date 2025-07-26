"""
Tencent Agent for handling Tencent Cloud workflow integration.
Uses Tencent's remote workflow with session management and SSE event collection.
"""
import os
import json
from typing import Dict, Any, Optional
import requests
import sseclient
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lke.v20231130 import lke_client, models

from app.core.logging import get_logger

logger = get_logger(__name__)


class TencentAgent:
    """Agent for interacting with Tencent Cloud LKE workflow."""

    def __init__(self):
        """Initialize Tencent Agent with credentials from environment variables."""
        self.secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        # self.secret_id = ""
        self.secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        # self.bot_app_key = ""
        self.sse_endpoint = "https://wss.lke.cloud.tencent.com/v1/qbot/chat/sse"

        if not self.secret_id or not self.secret_key:
            raise ValueError("TENCENTCLOUD_SECRET_ID and TENCENTCLOUD_SECRET_KEY must be set in environment variables")

        self._init_client()

    def _init_client(self):
        """Initialize Tencent Cloud client."""
        try:
            # Create credential object
            cred = credential.Credential(self.secret_id, self.secret_key)

            # Configure HTTP profile
            http_profile = HttpProfile()
            http_profile.endpoint = "lke.tencentcloudapi.com"

            # Configure client profile
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile

            # Create LKE client
            self.client = lke_client.LkeClient(cred, "ap-guangzhou", client_profile)
            logger.info("Tencent Cloud client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Tencent Cloud client: {e}")
            raise

    def get_session(self) -> Dict[str, Any]:
        """
        Obtain a session token from Tencent Cloud.

        Returns:
            Dict containing session information including session_id
        """
        try:
            # Create request object
            req = models.GetWsTokenRequest()
            params = {
                "Type": 5,
                "BotAppKey": self.bot_app_key
            }
            req.from_json_string(json.dumps(params))

            # Get response
            resp = self.client.GetWsToken(req)
            result = json.loads(resp.to_json_string())

            logger.info(f"Session response: {json.dumps(result, indent=2)}")

            # The session ID might be in a different field
            session_id = result.get('Token')
            logger.info(f"Successfully obtained session: {session_id}")

            # Return the full result with SessionId field normalized
            if session_id and 'SessionId' not in result:
                result['SessionId'] = session_id

            return result

        except TencentCloudSDKException as e:
            logger.exception(f"Tencent Cloud SDK error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Failed to get session: {e}")
            raise

    def query_workflow(
        self,
        session_id: str,
        query: str,
        visitor_biz_id: str,
        img_content: Optional[str] = None,
        custom_variables: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Query the Tencent workflow using SSE endpoint.

        Args:
            session_id: Session ID from get_session()
            query: User query text
            visitor_biz_id: Visitor business ID
            img_content: Optional image content
            custom_variables: Optional custom variables dict

        Returns:
            Collected response from SSE events
        """
        # Prepare request payload
        payload = {
            "session_id": session_id,
            "bot_app_key": self.bot_app_key,
            "visitor_biz_id": visitor_biz_id,
            "content": query,
            "incremental": True,
            "streaming_throttle": 10,
            "visitor_labels": [],
            "custom_variables": {
                "imgContent": img_content or "1",
                "SercertId": self.secret_id,
                "SercertKey": self.secret_key,
                "FetchContent": "false"
            },
            "search_network": "enable",
            "stream": "disable",
            "workflow_status": "enable",
            "tcadp_user_id": ""
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        # Log the payload for debugging
        logger.info(f"SSE request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        try:
            # Make SSE request
            response = requests.post(
                self.sse_endpoint,
                json=payload,
                headers=headers,
                stream=True,
                timeout=30
            )
            response.raise_for_status()

            # Collect SSE events
            collected_response = ""
            client = sseclient.SSEClient(response)

            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        # Extract content based on the response structure
                        if "payload" in data:
                            if "content" in data["payload"]:
                                collected_response += data["payload"]["content"]
                            elif "message" in data["payload"]:
                                collected_response += data["payload"]["message"]
                        logger.debug(f"Received SSE event: {event.data}")
                    except json.JSONDecodeError:
                        # If not JSON, append raw data
                        collected_response += event.data

            logger.info("Successfully collected workflow response")
            return collected_response

        except requests.exceptions.RequestException as e:
            logger.exception(f"Request error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Failed to query workflow: {e}")
            raise

    def process_query(self, query: str, visitor_biz_id: Optional[str] = None, **kwargs) -> str:
        """
        Process a query through the complete workflow.

        Args:
            query: User query text
            visitor_biz_id: Optional visitor ID, will be generated if not provided
            **kwargs: Additional arguments for query_workflow

        Returns:
            Workflow response
        """
        try:
            # Generate visitor_biz_id if not provided
            if not visitor_biz_id:
                import uuid
                visitor_biz_id = str(uuid.uuid4())[:18]

            # Get session
            session_id = None
            try:
                session_info = self.get_session()
                session_id = session_info.get("SessionId")
            except Exception as e:
                logger.exception(f"Failed to get session: {e}")

            if not session_id:
                raise ValueError("Failed to obtain session ID")

            # Query workflow
            response = self.query_workflow(
                session_id=session_id,
                query=query,
                visitor_biz_id=visitor_biz_id,
                **kwargs
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise


# Create singleton instance
tencent_agent = TencentAgent()
