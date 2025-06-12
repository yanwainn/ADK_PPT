"""
Data models for the PDF to Presentation application.
"""
from pydantic import BaseModel
from typing import List, Optional

# Bosch color scheme constants
BOSCH_COLORS = {
    "primary": "#E20015",    # Bosch Red
    "secondary": "#007BC0",  # Bosch Blue
    "accent": "#00884A",     # Bosch Green
    "text": "#333333",       # Dark Gray
    "light_text": "#7D7D7D", # Medium Gray
    "background": "#FFFFFF", # White
}

class KeySection(BaseModel):
    """Model for a key section extracted from the PDF."""
    title: str
    content: str
    importance: int  # 1-10 scale
    themes: List[str]
    visual_elements: List[str]

class ContentExtractionResult(BaseModel):
    """Model for the complete content extraction result."""
    document_title: str
    summary: str
    overall_themes: List[str]
    key_sections: List[KeySection]

class VisualPrompt(BaseModel):
    """Model for a visual prompt for DALL-E."""
    section_title: str
    prompt: str
    style_guidance: str
    elements_to_avoid: List[str]

class ImageInfo(BaseModel):
    """Model for image information."""
    file_path: str
    file_name: str
    base64_data: str
    width: int
    height: int

class HTMLSlide(BaseModel):
    """Model for an HTML slide."""
    html_content: str
    title: str
    section_title: str
    section_content: str
