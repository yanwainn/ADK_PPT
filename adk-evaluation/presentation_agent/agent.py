"""
ADK Presentation Agent - Enhanced document processing and presentation generation.

This agent provides comprehensive document analysis and presentation creation capabilities
using Google's ADK framework with advanced tool integration.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from google.adk.agents import Agent


def extract_document_content(document_text: str) -> Dict[str, Any]:
    """
    Extract key sections and content from a document.
    
    Args:
        document_text: Raw text content from the document
        
    Returns:
        Dictionary containing extracted sections and metadata
    """
    try:
        # Simulate document processing
        # In a real implementation, this would use NLP libraries or APIs
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in document_text.split('\n\n') if p.strip()]
        
        # Extract potential titles (lines that are short and capitalized)
        titles = []
        content_sections = []
        
        for para in paragraphs[:10]:  # Limit to first 10 paragraphs for demo
            if len(para) < 100 and para.isupper():
                titles.append(para)
            elif len(para) > 50:
                content_sections.append(para)
        
        # Create sections
        sections = []
        for i, content in enumerate(content_sections[:5]):  # Limit to 5 sections
            section = {
                "title": titles[i] if i < len(titles) else f"Section {i+1}",
                "content": content[:300] + "..." if len(content) > 300 else content,
                "importance": min(10, max(1, len(content) // 50)),  # Simple importance scoring
                "themes": extract_themes(content),
                "visual_elements": extract_visual_elements(content)
            }
            sections.append(section)
        
        return {
            "status": "success",
            "document_title": titles[0] if titles else "Untitled Document",
            "document_summary": f"Document contains {len(paragraphs)} paragraphs with {len(sections)} key sections.",
            "overall_themes": list(set([theme for section in sections for theme in section["themes"]])),
            "sections": sections
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to extract content: {str(e)}"
        }


def extract_themes(text: str) -> List[str]:
    """Extract key themes from text content."""
    # Simple keyword-based theme extraction
    themes = []
    
    # Business themes
    if any(word in text.lower() for word in ['business', 'market', 'strategy', 'revenue']):
        themes.append('Business Strategy')
    
    # Technology themes
    if any(word in text.lower() for word in ['technology', 'digital', 'software', 'ai', 'data']):
        themes.append('Technology')
    
    # Process themes
    if any(word in text.lower() for word in ['process', 'workflow', 'procedure', 'method']):
        themes.append('Process Improvement')
    
    # Research themes
    if any(word in text.lower() for word in ['research', 'study', 'analysis', 'findings']):
        themes.append('Research & Analysis')
    
    return themes[:3]  # Limit to 3 themes


def extract_visual_elements(text: str) -> List[str]:
    """Extract potential visual elements from text content."""
    visual_elements = []
    
    # Look for numerical data
    if re.search(r'\d+%|\d+\.\d+|\$\d+', text):
        visual_elements.append('Charts and graphs')
    
    # Look for process indicators
    if any(word in text.lower() for word in ['step', 'phase', 'stage', 'process']):
        visual_elements.append('Process diagrams')
    
    # Look for comparison indicators
    if any(word in text.lower() for word in ['compare', 'versus', 'vs', 'difference']):
        visual_elements.append('Comparison charts')
    
    # Look for timeline indicators
    if any(word in text.lower() for word in ['timeline', 'schedule', 'roadmap', 'year', 'month']):
        visual_elements.append('Timeline graphics')
    
    # Default visual elements
    if not visual_elements:
        visual_elements = ['Professional imagery', 'Icon illustrations', 'Background graphics']
    
    return visual_elements[:4]  # Limit to 4 elements


def generate_visual_prompt(section_title: str, content: str, themes: List[str]) -> Dict[str, Any]:
    """
    Generate a DALL-E prompt for visual content.
    
    Args:
        section_title: Title of the section
        content: Content of the section
        themes: List of themes for the section
        
    Returns:
        Dictionary containing the visual prompt and metadata
    """
    try:
        # Create a professional visual prompt
        base_prompt = f"Create a professional, photorealistic image for a business presentation slide titled '{section_title}'. "
        
        # Add theme-specific elements
        if 'Technology' in themes:
            base_prompt += "Include modern technology elements, clean interfaces, and digital aesthetics. "
        elif 'Business Strategy' in themes:
            base_prompt += "Include business professional elements, corporate aesthetics, and strategic imagery. "
        elif 'Research & Analysis' in themes:
            base_prompt += "Include analytical elements, data visualization concepts, and research imagery. "
        else:
            base_prompt += "Include professional business elements with clean, modern aesthetics. "
        
        # Add style requirements
        base_prompt += "Use professional lighting, high-quality composition, and corporate color scheme. "
        base_prompt += "Avoid any text, numbers, or written content in the image. "
        base_prompt += "Focus on visual metaphors and symbolic representations."
        
        return {
            "status": "success",
            "prompt": base_prompt,
            "style_guidance": "Professional photography with corporate aesthetics",
            "elements_to_avoid": ["text", "numbers", "written content", "cartoons", "low quality"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to generate visual prompt: {str(e)}"
        }


def create_slide_structure(sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a structured slide layout plan.
    
    Args:
        sections: List of document sections
        
    Returns:
        Dictionary containing slide structure recommendations
    """
    try:
        slides = []
        
        for i, section in enumerate(sections):
            # Create bullet points (simplified)
            bullet_points = []
            content_sentences = section['content'].split('. ')
            
            for sentence in content_sentences[:4]:  # Max 4 bullet points
                if len(sentence.strip()) > 10:
                    # Simplify sentence to bullet point
                    bullet = sentence.strip()[:60] + "..." if len(sentence) > 60 else sentence.strip()
                    bullet_points.append(bullet)
            
            # Determine slide layout
            layout_type = "balanced"
            if section['importance'] >= 8:
                layout_type = "image_focus"
            elif len(bullet_points) >= 4:
                layout_type = "text_focus"
            
            slide = {
                "slide_number": i + 1,
                "title": section['title'],
                "layout_type": layout_type,
                "bullet_points": bullet_points,
                "themes": section['themes'],
                "visual_elements": section['visual_elements'],
                "importance": section['importance']
            }
            slides.append(slide)
        
        return {
            "status": "success",
            "total_slides": len(slides),
            "slides": slides,
            "recommended_duration": f"{len(slides) * 2}-{len(slides) * 3} minutes"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create slide structure: {str(e)}"
        }


def analyze_presentation_requirements(document_title: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the presentation requirements and provide recommendations.
    
    Args:
        document_title: Title of the document
        sections: List of document sections
        
    Returns:
        Dictionary containing presentation analysis and recommendations
    """
    try:
        # Calculate presentation metrics
        total_content = sum(len(section['content']) for section in sections)
        avg_importance = sum(section['importance'] for section in sections) / len(sections)
        all_themes = list(set([theme for section in sections for theme in section['themes']]))
        
        # Determine presentation type
        if avg_importance >= 7:
            presentation_type = "Executive Summary"
        elif len(sections) >= 6:
            presentation_type = "Detailed Analysis"
        else:
            presentation_type = "Standard Presentation"
        
        # Create recommendations
        recommendations = []
        
        if len(sections) > 8:
            recommendations.append("Consider splitting into multiple presentations")
        
        if avg_importance < 5:
            recommendations.append("Focus on higher-impact content")
        
        if len(all_themes) > 5:
            recommendations.append("Consider grouping related themes")
        
        recommendations.append("Include visual elements for better engagement")
        recommendations.append("Add interactive elements where appropriate")
        
        return {
            "status": "success",
            "presentation_type": presentation_type,
            "total_content_length": total_content,
            "average_importance": round(avg_importance, 1),
            "key_themes": all_themes,
            "recommendations": recommendations,
            "estimated_slides": len(sections),
            "estimated_duration": f"{len(sections) * 2}-{len(sections) * 3} minutes"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to analyze presentation requirements: {str(e)}"
        }


# Define the root agent
root_agent = Agent(
    name="presentation_agent",
    model="gemini-2.0-flash",
    description="Expert presentation agent that helps users create professional presentations from documents.",
    instruction="""You are an expert presentation agent that helps users create professional presentations from documents.

You can:
1. Extract key content and sections from documents
2. Generate visual prompts for presentation images
3. Create structured slide layouts
4. Analyze presentation requirements and provide recommendations

When users provide document content, analyze it thoroughly and offer comprehensive presentation planning assistance.

Always provide helpful, professional advice for creating engaging presentations.""",
    tools=[
        extract_document_content,
        generate_visual_prompt,
        create_slide_structure,
        analyze_presentation_requirements
    ]
) 