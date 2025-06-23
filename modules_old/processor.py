"""
Document processor for Streamlit app integration.
Bridges Streamlit UI with sequential agents workflow.
"""

import streamlit as st
import PyPDF2
import io
import logging
from typing import List, Dict, Any
from datetime import datetime

from modules.sequential_agents import SequentialWorkflowCoordinator
from modules.html_presentation_generator import HTMLPresentationGenerator
from modules.models import ContentExtractionResult, KeySection, HTMLSlide

logger = logging.getLogger(__name__)

async def process_pdf_to_presentation(uploaded_file):
    """
    Main processing function for Streamlit app.
    Processes uploaded file and generates presentation using sequential agents.
    """
    try:
        st.info("🔍 Extracting text from uploaded document...")
        
        # Extract text based on file type
        document_text = extract_text_from_file(uploaded_file)
        
        if not document_text.strip():
            st.error("❌ No text could be extracted from the file")
            return
        
        st.info(f"📄 Extracted {len(document_text)} characters from document")
        
        # Initialize workflow coordinator
        st.info("🤖 Initializing AI-powered presentation workflow...")
        coordinator = SequentialWorkflowCoordinator()
        
        # Execute sequential workflow with progress updates
        with st.spinner("🎨 AI agents are creating your presentation..."):
            result = coordinator.execute_full_workflow(document_text)
        
        if result.get("status") != "success":
            st.error(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return
        
        # Generate HTML presentation
        st.info("🎨 Generating HTML presentation...")
        html_generator = HTMLPresentationGenerator()
        html_result = html_generator.generate_html_presentation(document_text)
        
        if html_result.get("status") != "success":
            st.error(f"❌ HTML generation failed: {html_result.get('error', 'Unknown error')}")
            return
        
        # Update session state with results
        update_session_state(result, html_result, uploaded_file.name)
        
        st.success("✅ Presentation generated successfully!")
        st.balloons()
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        st.error(f"❌ Processing failed: {str(e)}")
        st.session_state.process_complete = False

def extract_text_from_file(uploaded_file) -> str:
    """Extract text from uploaded file based on file type."""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return extract_pdf_text(uploaded_file)
    elif file_extension in ['txt', 'md']:
        return uploaded_file.getvalue().decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def extract_pdf_text(pdf_file) -> str:
    """Extract text from PDF file using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n\n"
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                continue
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        return text.strip()
        
    except Exception as e:
        raise ValueError(f"Failed to process PDF file: {str(e)}")

def update_session_state(workflow_result: Dict[str, Any], html_result: Dict[str, Any], filename: str):
    """Update Streamlit session state with results to match app.py expectations."""
    
    # Get title from workflow slides
    slides = workflow_result.get("slides", [])
    title = slides[0].get("title", filename.replace('.pdf', '').replace('.txt', '').replace('.md', '')) if slides else filename
    
    # Create ContentExtractionResult object
    extraction_result = ContentExtractionResult(
        document_title=title,
        summary="AI-powered presentation generated successfully",
        overall_themes=["AI Generated", "Professional"],
        key_sections=create_key_sections_from_slides(slides)
    )
    
    # Create HTML slides from the HTML result
    html_slides = create_html_slides_from_result(html_result, workflow_result)
    
    # Update session state
    st.session_state.key_sections = extraction_result
    st.session_state.slides_html = html_slides
    st.session_state.process_complete = True
    st.session_state.image_prompts = []  # Not used in current workflow
    st.session_state.generated_images = []  # Not used in current workflow

def create_key_sections_from_slides(slides: List[Dict[str, Any]]) -> List[KeySection]:
    """Create KeySection objects from workflow slides."""
    sections = []
    
    for i, slide in enumerate(slides):
        # Skip title slide for sections
        if slide.get("type") == "title":
            continue
            
        key_section = KeySection(
            title=slide.get("title", f"Section {i}"),
            content=slide.get("content_text", ""),
            importance=7,  # Default importance
            themes=[slide.get("type", "content")],
            visual_elements=[]
        )
        sections.append(key_section)
    
    return sections

def create_html_slides_from_result(html_result: Dict[str, Any], workflow_result: Dict[str, Any]) -> List[HTMLSlide]:
    """Create HTMLSlide objects from HTML generation results."""
    slides = []
    
    # Get slides from HTML result
    html_slides_data = html_result.get("slides", [])
    
    # Get slides directly from workflow result
    workflow_slides = workflow_result.get("slides", [])
    
    for i, slide_data in enumerate(html_slides_data):
        # Get corresponding workflow slide data
        workflow_slide = workflow_slides[i] if i < len(workflow_slides) else {}
        
        html_slide = HTMLSlide(
            html_content=generate_slide_html(slide_data, i, len(html_slides_data)),
            title=slide_data.get("title", workflow_slide.get("title", f"Slide {i+1}")),
            section_title=slide_data.get("title", ""),
            section_content=slide_data.get("content", workflow_slide.get("content_text", ""))
        )
        slides.append(html_slide)
    
    return slides

def generate_slide_html(slide_data: Dict[str, Any], slide_num: int, total_slides: int) -> str:
    """Generate HTML content for a single slide."""
    
    slide_type = slide_data.get("type", "content")
    title = slide_data.get("title", f"Slide {slide_num + 1}")
    
    # Base HTML structure
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .slide {{
                background: white;
                border-radius: 15px;
                padding: 60px;
                max-width: 900px;
                width: 100%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                position: relative;
            }}
            .slide-header {{
                border-bottom: 3px solid #667eea;
                padding-bottom: 20px;
                margin-bottom: 40px;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 2.5em;
                margin: 0;
                font-weight: 700;
            }}
            h2 {{
                color: #34495e;
                font-size: 1.8em;
                margin-bottom: 20px;
            }}
            .content {{
                line-height: 1.8;
                font-size: 1.1em;
                color: #444;
            }}
            ul {{
                list-style: none;
                padding: 0;
            }}
            li {{
                margin: 15px 0;
                padding-left: 30px;
                position: relative;
            }}
            li:before {{
                content: "▶";
                color: #667eea;
                font-weight: bold;
                position: absolute;
                left: 0;
            }}
            .slide-number {{
                position: absolute;
                top: 20px;
                right: 30px;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="slide">
            <div class="slide-number">{slide_num + 1} / {total_slides}</div>
            <div class="slide-header">
                <h1>{title}</h1>
            </div>
            <div class="content">
    """
    
    # Add slide-specific content
    if slide_type == "title":
        subtitle = slide_data.get("subtitle", "")
        highlights = slide_data.get("highlights", [])
        
        html += f"""
                <h2>{subtitle}</h2>
                <ul>
        """
        for highlight in highlights:
            html += f"<li>{highlight}</li>"
        html += "</ul>"
        
    elif slide_type == "conclusion":
        takeaways = slide_data.get("takeaways", [])
        next_steps = slide_data.get("next_steps", [])
        closing_statement = slide_data.get("closing_statement", "")
        
        if takeaways:
            html += "<h2>Key Takeaways</h2><ul>"
            for takeaway in takeaways:
                html += f"<li>{takeaway}</li>"
            html += "</ul>"
        
        if next_steps:
            html += "<h2>Next Steps</h2><ul>"
            for step in next_steps:
                html += f"<li>{step}</li>"
            html += "</ul>"
        
        if closing_statement:
            html += f"<p><strong>{closing_statement}</strong></p>"
    
    else:  # content slide
        bullet_points = slide_data.get("bullet_points", [])
        key_message = slide_data.get("key_message", "")
        
        if bullet_points:
            html += "<ul>"
            for point in bullet_points:
                html += f"<li>{point}</li>"
            html += "</ul>"
        
        if key_message:
            html += f"<p><strong>Key Insight:</strong> {key_message}</p>"
    
    # Close HTML
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html 