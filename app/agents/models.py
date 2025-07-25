"""
Pydantic models for Claude agent structured outputs
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ScreenshotSourceAnalysis(BaseModel):
    """Model for unified screenshot analysis and source finding"""
    # Analysis fields
    analysis_summary: str = Field(description="Brief summary of what the screenshot contains")
    key_entities: List[str] = Field(description="Key entities found (usernames, websites, product names, etc)")
    content_type: str = Field(description="Type of content: 'social_media', 'article', 'documentation', 'chat', 'code', 'other'")
    
    # Source finding fields
    original_source: Optional[str] = Field(description="The URL of the original source, or None if not found")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    verification: bool = Field(description="Whether the source was verified by viewing the webpage")
    reasoning: str = Field(description="Detailed explanation of how the source was found and why this confidence level")
    alternative_sources: List[str] = Field(description="List of alternative possible sources if main source is uncertain")


class ScreenshotAutomationAnalysis(BaseModel):
    """Model for screenshot automation analysis and task generation"""
    # Content analysis
    content_summary: str = Field(description="Summary of what was detected in the screenshot")
    detected_type: str = Field(description="Type of content: 'code', 'commands', 'config', 'documentation', 'ui', 'data', 'mixed'")
    extracted_data: Dict[str, List[str]] = Field(
        description="Extracted actionable data organized by type (commands, urls, code_snippets, packages, settings, etc)"
    )
    
    # Automation proposals
    automation_tasks: List[Dict[str, str]] = Field(
        description="List of proposed automation tasks with 'task', 'description', and 'risk_level' (low/medium/high)"
    )
    recommended_sequence: List[int] = Field(
        description="Recommended order of task execution (list of task indices)"
    )
    
    # Execution details
    can_automate: bool = Field(description="Whether any automations can be performed")
    requires_confirmation: List[str] = Field(description="List of actions that require explicit user confirmation")
    warnings: List[str] = Field(description="Any warnings or cautions about the proposed automations")