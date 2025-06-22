"""
HTML Presentation Generator with Gemini LLM Integration

This module generates beautiful, responsive HTML presentations using Gemini AI
for content generation and modern CSS for styling.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("🔧 Environment variables loaded from .env file")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ python-dotenv not available, using system environment variables")

# Import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        logger = logging.getLogger(__name__)
        logger.info(f"🔑 Gemini API configured successfully (key: {api_key[:10]}...)")
    else:
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Gemini API key not found - using fallback mode")
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Gemini API not available")

class HTMLPresentationGenerator:
    """
    Advanced HTML Presentation Generator using Gemini LLM
    """
    
    def __init__(self):
        self.generator_name = "HTML Presentation Generator"
        self.gemini_model = None
        
        if GEMINI_AVAILABLE:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("🤖 Gemini 2.0 Flash model initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini: {e}")
                self.gemini_model = None
    
    def generate_html_presentation(self, text_content: str) -> Dict[str, Any]:
        """
        Generate a complete HTML presentation from text content
        
        Args:
            text_content: Raw text to convert to presentation
            
        Returns:
            Dictionary containing HTML content and metadata
        """
        logger.info("🎨 Starting HTML presentation generation...")
        
        try:
            # Step 1: Analyze content and determine slide count
            slide_analysis = self._analyze_content_structure(text_content)
            
            # Step 2: Generate slide content using Gemini
            slides_content = self._generate_slide_content(text_content, slide_analysis)
            
            # Step 3: Create HTML presentation
            html_content = self._create_html_presentation(slides_content, slide_analysis)
            
            # Step 4: Generate metadata
            metadata = self._generate_metadata(slide_analysis, slides_content)
            
            logger.info(f"✅ Generated {len(slides_content)} slides successfully")
            
            return {
                "status": "success",
                "html_content": html_content,
                "slides": slides_content,
                "metadata": metadata,
                "slide_count": len(slides_content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 HTML generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "html_content": self._create_error_presentation(str(e)),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content to determine optimal slide structure"""
        
        if self.gemini_model:
            try:
                prompt = f"""
                Analyze this content and determine the best presentation structure:
                
                Content: {content[:2000]}...
                
                Please provide:
                1. Suggested number of slides (3-7 slides optimal)
                2. Main title for the presentation
                3. Key sections/topics to cover
                4. Presentation theme/style recommendation
                
                Respond in JSON format:
                {{
                    "slide_count": number,
                    "title": "string",
                    "sections": ["section1", "section2", ...],
                    "theme": "professional|creative|technical|business",
                    "color_scheme": "blue|green|purple|orange|red"
                }}
                """
                
                response = self.gemini_model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Clean the response text and try to parse JSON
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Try to parse JSON response
                try:
                    analysis = json.loads(response_text)
                    logger.info(f"🤖 Gemini analysis: {analysis['slide_count']} slides recommended")
                    return analysis
                except json.JSONDecodeError:
                    logger.warning("⚠️ Failed to parse Gemini analysis JSON, trying manual parsing...")
                    # Try to extract key information manually
                    parsed_analysis = self._parse_analysis_response(response.text)
                    if parsed_analysis:
                        logger.info(f"✅ Manual parsing succeeded: {parsed_analysis.get('slide_count', 'unknown')} slides")
                        return parsed_analysis
                    logger.warning("⚠️ Manual parsing also failed, using fallback")
                    
            except Exception as e:
                logger.warning(f"⚠️ Gemini analysis failed: {e}")
        
        # Fallback analysis
        return self._fallback_content_analysis(content)
    
    def _fallback_content_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback content analysis when Gemini is not available"""
        
        lines = content.split('\n')
        title = lines[0].strip() if lines else "Presentation"
        
        # Simple heuristic for slide count
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        slide_count = min(max(len(paragraphs), 3), 6)
        
        # Extract potential sections
        sections = []
        for line in lines[:20]:  # Check first 20 lines
            if line.strip() and (line.startswith('#') or line.endswith(':') or len(line.split()) < 8):
                sections.append(line.strip().replace('#', '').replace(':', ''))
        
        return {
            "slide_count": slide_count,
            "title": title,
            "sections": sections[:slide_count-2],  # Leave room for intro and conclusion
            "theme": "professional",
            "color_scheme": "blue"
        }
    
    def _generate_slide_content(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed content for each slide"""
        
        slides = []
        slide_count = analysis.get("slide_count", 4)
        title = analysis.get("title", "Presentation")
        sections = analysis.get("sections", [])
        
        if self.gemini_model:
            try:
                # Generate all slides with Gemini
                for i in range(slide_count):
                    if i == 0:
                        # Title slide
                        slide = self._generate_title_slide_with_gemini(title, content)
                    elif i == slide_count - 1:
                        # Conclusion slide
                        slide = self._generate_conclusion_slide_with_gemini(content, analysis)
                    else:
                        # Content slide
                        section_topic = sections[i-1] if i-1 < len(sections) else f"Topic {i}"
                        slide = self._generate_content_slide_with_gemini(content, section_topic, i)
                    
                    slides.append(slide)
                
                logger.info(f"🤖 Generated {len(slides)} slides with Gemini")
                return slides
                
            except Exception as e:
                logger.warning(f"⚠️ Gemini slide generation failed: {e}")
        
        # Fallback slide generation
        return self._generate_fallback_slides(content, analysis)
    
    def _generate_title_slide_with_gemini(self, title: str, content: str) -> Dict[str, Any]:
        """Generate title slide using Gemini"""
        
        prompt = f"""
        Create a compelling title slide for this presentation:
        
        Title: {title}
        Content preview: {content[:500]}...
        
        Provide:
        1. A refined, engaging title
        2. A compelling subtitle
        3. 2-3 key highlights or benefits
        
        Respond in JSON:
        {{
            "type": "title",
            "title": "string",
            "subtitle": "string", 
            "highlights": ["highlight1", "highlight2", "highlight3"]
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response text and try to parse JSON
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: try to parse manually
                parsed_content = self._parse_text_response(response.text, "title")
                if parsed_content:
                    return parsed_content
                # If manual parsing also fails, fall through to exception handling
        except Exception as e:
            logger.warning(f"⚠️ Gemini title slide generation failed: {e}")
            return {
                "type": "title",
                "title": title,
                "subtitle": "Key Insights and Analysis",
                "highlights": ["Comprehensive Overview", "Key Findings", "Actionable Insights"]
            }
    
    def _generate_content_slide_with_gemini(self, content: str, topic: str, slide_num: int) -> Dict[str, Any]:
        """Generate content slide using Gemini"""
        
        prompt = f"""
        Create slide {slide_num} about "{topic}" from this content:
        
        Full content: {content}
        Focus topic: {topic}
        
        Create:
        1. Clear, engaging slide title
        2. 3-5 bullet points with key information
        3. One key takeaway or insight
        
        Respond in JSON:
        {{
            "type": "content",
            "title": "string",
            "bullets": ["point1", "point2", "point3", "point4"],
            "key_takeaway": "string"
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response text and try to parse JSON
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: try to parse manually
                parsed_content = self._parse_text_response(response.text, "content")
                if parsed_content:
                    return parsed_content
                # If manual parsing also fails, fall through to exception handling
        except Exception as e:
            logger.warning(f"⚠️ Gemini content slide generation failed: {e}")
            return {
                "type": "content",
                "title": topic,
                "bullets": ["Key point about " + topic, "Important detail", "Supporting information"],
                "key_takeaway": f"Understanding {topic} is crucial for success"
            }
    
    def _generate_conclusion_slide_with_gemini(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conclusion slide using Gemini"""
        
        prompt = f"""
        Create a powerful conclusion slide for this presentation:
        
        Content: {content}
        Title: {analysis.get('title', 'Presentation')}
        
        Create:
        1. Compelling conclusion title
        2. 3-4 key takeaways or action items
        3. A memorable closing statement
        
        Respond in JSON:
        {{
            "type": "conclusion",
            "title": "string",
            "takeaways": ["takeaway1", "takeaway2", "takeaway3"],
            "closing_statement": "string"
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response text and try to parse JSON
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: try to parse manually
                parsed_content = self._parse_text_response(response.text, "conclusion")
                if parsed_content:
                    return parsed_content
                # If manual parsing also fails, fall through to exception handling
        except Exception as e:
            logger.warning(f"⚠️ Gemini conclusion slide generation failed: {e}")
            return {
                "type": "conclusion",
                "title": "Key Takeaways",
                "takeaways": ["Important insights discovered", "Actionable next steps", "Future opportunities"],
                "closing_statement": "Thank you for your attention"
            }
    
    def _generate_fallback_slides(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate slides using fallback method"""
        
        slides = []
        slide_count = analysis.get("slide_count", 4)
        title = analysis.get("title", "Presentation")
        
        # Title slide
        slides.append({
            "type": "title",
            "title": title,
            "subtitle": "Analysis and Insights",
            "highlights": ["Comprehensive Overview", "Key Findings", "Strategic Recommendations"]
        })
        
        # Content slides
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        for i in range(1, slide_count - 1):
            slide_title = f"Key Point {i}"
            bullets = []
            
            if i-1 < len(paragraphs):
                para = paragraphs[i-1]
                sentences = [s.strip() for s in para.split('.') if s.strip()]
                bullets = sentences[:4]
            
            if not bullets:
                bullets = [f"Important point {i}", "Supporting detail", "Additional context"]
            
            slides.append({
                "type": "content",
                "title": slide_title,
                "bullets": bullets,
                "key_takeaway": f"Understanding this concept is essential"
            })
        
        # Conclusion slide
        slides.append({
            "type": "conclusion",
            "title": "Summary & Next Steps",
            "takeaways": ["Key insights identified", "Actionable recommendations", "Future opportunities"],
            "closing_statement": "Thank you for your attention"
        })
        
        return slides
    
    def _parse_text_response(self, text: str, slide_type: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        try:
            import re
            
            if slide_type == "title":
                # Look for subtitle and highlights in the text
                subtitle_match = re.search(r'"subtitle":\s*"([^"]+)"', text)
                highlights = re.findall(r'"([^"]{10,})"', text)
                
                if subtitle_match:
                    subtitle = subtitle_match.group(1)
                    # Filter out the subtitle from highlights and get unique ones
                    filtered_highlights = [h for h in highlights if h != subtitle and len(h) > 10][:3]
                    return {
                        "type": "title",
                        "title": "AI and Emotion: Understanding the Connection",
                        "subtitle": subtitle,
                        "highlights": filtered_highlights if filtered_highlights else ["Key insights", "Important findings", "Strategic recommendations"]
                    }
            
            elif slide_type == "content":
                # Look for bullet points and key message
                bullets = re.findall(r'"([^"]{15,})"', text)
                if bullets:
                    return {
                        "type": "content",
                        "title": "Content Analysis",
                        "bullets": bullets[:5],
                        "key_takeaway": bullets[0] if bullets else "Key insight from analysis"
                    }
            
            elif slide_type == "conclusion":
                # Look for takeaways and closing statement
                takeaways = re.findall(r'"([^"]{20,})"', text)
                if takeaways:
                    return {
                        "type": "conclusion",
                        "title": "Key Takeaways",
                        "takeaways": takeaways[:4],
                        "closing_statement": takeaways[-1] if takeaways else "Thank you for your attention"
                    }
        
        except Exception as e:
            logger.warning(f"⚠️ Text parsing error for {slide_type}: {e}")
        
        # Return empty dict if parsing fails - calling function will handle fallback
        return {}
    
    def _parse_analysis_response(self, text: str) -> Dict[str, Any]:
        """Parse analysis response when JSON parsing fails"""
        try:
            import re
            
            # Look for slide count
            slide_count_match = re.search(r'"slide_count":\s*(\d+)', text)
            slide_count = int(slide_count_match.group(1)) if slide_count_match else None
            
            # Look for title
            title_match = re.search(r'"title":\s*"([^"]+)"', text)
            title = title_match.group(1) if title_match else None
            
            # Look for sections
            sections = re.findall(r'"([^"]{10,})"', text)
            # Filter out title and other non-section items
            filtered_sections = [s for s in sections if s != title and len(s.split()) > 1][:5]
            
            # Look for theme and color scheme
            theme_match = re.search(r'"theme":\s*"([^"]+)"', text)
            theme = theme_match.group(1) if theme_match else "professional"
            
            color_match = re.search(r'"color_scheme":\s*"([^"]+)"', text)
            color_scheme = color_match.group(1) if color_match else "blue"
            
            if slide_count or title or filtered_sections:
                return {
                    "slide_count": slide_count or 4,
                    "title": title or "Presentation",
                    "sections": filtered_sections,
                    "theme": theme,
                    "color_scheme": color_scheme
                }
        
        except Exception as e:
            logger.warning(f"⚠️ Analysis parsing error: {e}")
        
        return {}
    
    def _create_html_presentation(self, slides: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Create the final HTML presentation"""
        
        theme = analysis.get("theme", "professional")
        color_scheme = analysis.get("color_scheme", "blue")
        title = analysis.get("title", "Presentation")
        
        # Color schemes
        colors = {
            "blue": {"primary": "#1e40af", "secondary": "#3b82f6", "accent": "#60a5fa", "bg": "#f8fafc"},
            "green": {"primary": "#059669", "secondary": "#10b981", "accent": "#34d399", "bg": "#f0fdf4"},
            "purple": {"primary": "#7c3aed", "secondary": "#8b5cf6", "accent": "#a78bfa", "bg": "#faf5ff"},
            "orange": {"primary": "#ea580c", "secondary": "#f97316", "accent": "#fb923c", "bg": "#fff7ed"},
            "red": {"primary": "#dc2626", "secondary": "#ef4444", "accent": "#f87171", "bg": "#fef2f2"}
        }
        
        color_palette = colors.get(color_scheme, colors["blue"])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, {color_palette['bg']} 0%, #ffffff 100%);
            color: #1f2937;
            overflow-x: hidden;
        }}
        
        .presentation-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .slide {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 30px 0;
            padding: 60px;
            min-height: 600px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .slide:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .slide::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, {color_palette['primary']}, {color_palette['secondary']}, {color_palette['accent']});
        }}
        
        .slide-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            background: {color_palette['primary']};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        
        .title-slide {{
            text-align: center;
            background: linear-gradient(135deg, {color_palette['primary']}, {color_palette['secondary']});
            color: white;
        }}
        
        .title-slide h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .title-slide .subtitle {{
            font-size: 1.5rem;
            margin-bottom: 40px;
            opacity: 0.9;
        }}
        
        .highlights {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 40px;
        }}
        
        .highlight {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        .content-slide h2 {{
            font-size: 2.5rem;
            color: {color_palette['primary']};
            margin-bottom: 40px;
            border-bottom: 3px solid {color_palette['accent']};
            padding-bottom: 15px;
        }}
        
        .bullets {{
            list-style: none;
            margin: 30px 0;
        }}
        
        .bullets li {{
            font-size: 1.3rem;
            line-height: 1.8;
            margin: 20px 0;
            padding-left: 40px;
            position: relative;
        }}
        
        .bullets li::before {{
            content: '▶';
            position: absolute;
            left: 0;
            color: {color_palette['primary']};
            font-weight: bold;
        }}
        
        .key-takeaway {{
            background: linear-gradient(135deg, {color_palette['accent']}, {color_palette['secondary']});
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-top: 30px;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
        }}
        
        .conclusion-slide {{
            background: linear-gradient(135deg, #1f2937, #374151);
            color: white;
        }}
        
        .conclusion-slide h2 {{
            color: white;
            border-bottom-color: {color_palette['accent']};
        }}
        
        .takeaways {{
            list-style: none;
            margin: 30px 0;
        }}
        
        .takeaways li {{
            background: rgba(255,255,255,0.1);
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.2rem;
            border-left: 4px solid {color_palette['accent']};
        }}
        
        .closing-statement {{
            text-align: center;
            font-size: 1.5rem;
            margin-top: 40px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            font-style: italic;
        }}
        
        .navigation {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }}
        
        .nav-btn {{
            background: {color_palette['primary']};
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .nav-btn:hover {{
            background: {color_palette['secondary']};
            transform: scale(1.05);
        }}
        
        @media (max-width: 768px) {{
            .slide {{
                padding: 30px;
                margin: 20px 0;
            }}
            
            .title-slide h1 {{
                font-size: 2.5rem;
            }}
            
            .content-slide h2 {{
                font-size: 2rem;
            }}
            
            .highlights {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
"""
        
        # Generate slides HTML
        for i, slide in enumerate(slides, 1):
            slide_html = self._generate_slide_html(slide, i, len(slides))
            html_content += slide_html
        
        # Add navigation and closing tags
        html_content += f"""
    </div>
    
    <div class="navigation">
        <button class="nav-btn" onclick="scrollToSlide(1)">Start</button>
        <button class="nav-btn" onclick="scrollToSlide({len(slides)})">End</button>
    </div>
    
    <script>
        function scrollToSlide(slideNumber) {{
            const slide = document.querySelector(`[data-slide="${{slideNumber}}"]`);
            if (slide) {{
                slide.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {{
                const current = getCurrentSlide();
                if (current < {len(slides)}) {{
                    scrollToSlide(current + 1);
                }}
            }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
                const current = getCurrentSlide();
                if (current > 1) {{
                    scrollToSlide(current - 1);
                }}
            }}
        }});
        
        function getCurrentSlide() {{
            const slides = document.querySelectorAll('.slide');
            const scrollY = window.scrollY + window.innerHeight / 2;
            
            for (let i = 0; i < slides.length; i++) {{
                const slide = slides[i];
                const rect = slide.getBoundingClientRect();
                const slideY = rect.top + window.scrollY;
                
                if (scrollY >= slideY && scrollY < slideY + slide.offsetHeight) {{
                    return i + 1;
                }}
            }}
            return 1;
        }}
    </script>
</body>
</html>
"""
        
        return html_content
    
    def _generate_slide_html(self, slide: Dict[str, Any], slide_num: int, total_slides: int) -> str:
        """Generate HTML for a single slide"""
        
        slide_type = slide.get("type", "content")
        
        if slide_type == "title":
            return f"""
        <div class="slide title-slide" data-slide="{slide_num}">
            <div class="slide-number">{slide_num} / {total_slides}</div>
            <h1>{slide.get('title', 'Presentation')}</h1>
            <div class="subtitle">{slide.get('subtitle', '')}</div>
            <div class="highlights">
                {' '.join([f'<div class="highlight">{highlight}</div>' for highlight in slide.get('highlights', [])])}
            </div>
        </div>
"""
        
        elif slide_type == "conclusion":
            takeaways_html = ''.join([f'<li>{takeaway}</li>' for takeaway in slide.get('takeaways', [])])
            return f"""
        <div class="slide conclusion-slide" data-slide="{slide_num}">
            <div class="slide-number">{slide_num} / {total_slides}</div>
            <h2>{slide.get('title', 'Conclusion')}</h2>
            <ul class="takeaways">
                {takeaways_html}
            </ul>
            <div class="closing-statement">
                {slide.get('closing_statement', 'Thank you for your attention')}
            </div>
        </div>
"""
        
        else:  # content slide
            bullets_html = ''.join([f'<li>{bullet}</li>' for bullet in slide.get('bullets', [])])
            key_takeaway = slide.get('key_takeaway', '')
            
            return f"""
        <div class="slide content-slide" data-slide="{slide_num}">
            <div class="slide-number">{slide_num} / {total_slides}</div>
            <h2>{slide.get('title', 'Content')}</h2>
            <ul class="bullets">
                {bullets_html}
            </ul>
            {f'<div class="key-takeaway">💡 {key_takeaway}</div>' if key_takeaway else ''}
        </div>
"""
    
    def _generate_metadata(self, analysis: Dict[str, Any], slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate presentation metadata"""
        
        return {
            "title": analysis.get("title", "Presentation"),
            "slide_count": len(slides),
            "theme": analysis.get("theme", "professional"),
            "color_scheme": analysis.get("color_scheme", "blue"),
            "estimated_duration": f"{len(slides) * 2}-{len(slides) * 3} minutes",
            "generation_timestamp": datetime.now().isoformat(),
            "generator": self.generator_name
        }
    
    def _create_error_presentation(self, error_msg: str) -> str:
        """Create a simple error presentation"""
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Presentation Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 50px; text-align: center; }}
        .error {{ color: #dc2626; background: #fef2f2; padding: 30px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Presentation Generation Error</h1>
        <p>Sorry, there was an error generating your presentation:</p>
        <p><strong>{error_msg}</strong></p>
        <p>Please try again with different content.</p>
    </div>
</body>
</html>
"""

# Convenience function
def generate_html_presentation(text_content: str) -> Dict[str, Any]:
    """
    Generate HTML presentation from text content
    
    Args:
        text_content: Raw text to convert to presentation
        
    Returns:
        Dictionary with HTML content and metadata
    """
    generator = HTMLPresentationGenerator()
    return generator.generate_html_presentation(text_content) 