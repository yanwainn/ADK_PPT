"""
Main processing pipeline for PDF to presentation conversion.
Supports both Azure OpenAI and direct OpenAI APIs.
"""
import asyncio
import streamlit as st
from modules.agents import extract_key_sections, create_visual_prompt, extract_key_bullet_points
from modules.helpers import extract_text_from_pdf, generate_image_from_prompt, save_image_locally, load_image_info_from_pil
from modules.slide_generator import create_html_slide

async def process_pdf_to_presentation(uploaded_file):
    """
    Main processing function to convert PDF to presentation.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    """
    try:
        # Step 1: Extract text from PDF
        st.write("📄 Extracting text from PDF...")
        pdf_text = extract_text_from_pdf(uploaded_file)
        
        if not pdf_text:
            st.error("Failed to extract text from PDF")
            return
        
        st.session_state.pdf_content = pdf_text
        st.success(f"✅ Extracted {len(pdf_text)} characters from PDF")
        
        # Step 2: Extract key sections using AI
        st.write("🤖 Analyzing content and extracting key sections...")
        extraction_result = await extract_key_sections(pdf_text)
        st.session_state.key_sections = extraction_result
        
        st.success(f"✅ Identified {len(extraction_result.key_sections)} key sections")
        
        # Step 3: Generate visual prompts for each section
        st.write("🎨 Creating visual prompts for images...")
        visual_prompts = []
        
        for i, section in enumerate(extraction_result.key_sections):
            st.write(f"Creating prompt for section {i+1}: {section.title}")
            prompt = await create_visual_prompt(section, extraction_result.document_title)
            visual_prompts.append(prompt)
        
        st.session_state.image_prompts = visual_prompts
        st.success(f"✅ Created {len(visual_prompts)} visual prompts")
        
        # Step 4: Generate images in parallel
        st.write("🖼️ Generating images with AI...")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        async def generate_single_image(i, prompt):
            """Generate a single image with progress tracking."""
            try:
                status_text.text(f"Generating image {i+1}/{len(visual_prompts)}: {prompt.section_title}")
                
                # Generate image
                image_result = await generate_image_from_prompt(prompt.prompt)
                
                # Save image locally
                save_result = save_image_locally(
                    image_result["image"], 
                    prompt.section_title, 
                    i, 
                    st.session_state.images_folder
                )
                
                # Create ImageInfo
                if save_result["success"]:
                    image_info = load_image_info_from_pil(
                        image_result["image"],
                        save_result["filename"],
                        save_result["filepath"]
                    )
                else:
                    # Create ImageInfo even if save failed
                    image_info = load_image_info_from_pil(
                        image_result["image"],
                        f"temp_image_{i}.png",
                        f"temp_path_{i}"
                    )
                
                # Update progress
                progress = (i + 1) / len(visual_prompts)
                progress_bar.progress(progress)
                
                return {
                    "index": i,
                    "image_result": image_result,
                    "image_info": image_info,
                    "save_result": save_result
                }
                
            except Exception as e:
                st.error(f"Error generating image {i+1}: {str(e)}")
                return {
                    "index": i,
                    "error": str(e)
                }
        
        # Generate all images in parallel
        image_tasks = [
            generate_single_image(i, prompt) 
            for i, prompt in enumerate(visual_prompts)
        ]
        
        image_results = await asyncio.gather(*image_tasks, return_exceptions=True)
        
        # Process results
        generated_images = []
        for result in image_results:
            if isinstance(result, Exception):
                st.error(f"Image generation failed: {str(result)}")
                generated_images.append(None)
            elif "error" in result:
                st.error(f"Image generation failed: {result['error']}")
                generated_images.append(None)
            else:
                generated_images.append(result["image_info"])
        
        st.session_state.generated_images = generated_images
        successful_images = len([img for img in generated_images if img is not None])
        st.success(f"✅ Generated {successful_images}/{len(visual_prompts)} images")
        
        # Step 5: Generate HTML slides
        st.write("📊 Creating presentation slides...")
        html_slides = []
        
        for i, section in enumerate(extraction_result.key_sections):
            st.write(f"Creating slide {i+1}: {section.title}")
            
            # Extract bullet points for this section
            bullet_points = await extract_key_bullet_points(section, extraction_result.document_title)
            
            # Get corresponding image
            image_info = generated_images[i] if i < len(generated_images) else None
            
            # Generate HTML slide
            html_slide = await create_html_slide(
                section=section,
                image_info=image_info,
                document_title=extraction_result.document_title
            )
            
            html_slides.append(html_slide)
        
        st.session_state.slides_html = html_slides
        st.success(f"✅ Created {len(html_slides)} presentation slides")
        
        # Mark process as complete
        st.session_state.process_complete = True
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Presentation generation complete!")
        
    except Exception as e:
        st.error(f"Error in processing pipeline: {str(e)}")
        st.session_state.process_complete = False
