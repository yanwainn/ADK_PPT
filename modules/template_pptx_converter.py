"""
Template-based PowerPoint converter module.
This module provides template-based PowerPoint generation functionality.
"""

import io
from typing import List, Dict, Any, Optional
from modules.pptx_converter import create_powerpoint_from_template as base_create_powerpoint_from_template
from modules.models import HTMLSlide, ContentExtractionResult

def create_powerpoint_from_template(slides: List[HTMLSlide], extraction_result: ContentExtractionResult, 
                                  template_file: Optional[str] = None, template_stream: Optional[io.BytesIO] = None) -> io.BytesIO:
    """
    Create a PowerPoint presentation using a template.
    This is a wrapper function that maintains compatibility with app.py imports.
    
    Args:
        slides: List of HTMLSlide objects
        extraction_result: ContentExtractionResult with document metadata
        template_file: Path to template PPTX file
        template_stream: BytesIO stream containing template PPTX
        
    Returns:
        BytesIO buffer containing the PowerPoint file
    """
    return base_create_powerpoint_from_template(slides, extraction_result, template_file, template_stream) 