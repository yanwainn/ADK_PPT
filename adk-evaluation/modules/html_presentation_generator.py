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

# Import theme management
try:
    from .presentation_themes import PresentationThemes, select_theme
except ImportError:
    PresentationThemes = None
    select_theme = None

# Import visual elements
try:
    from .visual_elements import VisualElementGenerator, VISUAL_ELEMENTS_CSS
except ImportError:
    VisualElementGenerator = None
    VISUAL_ELEMENTS_CSS = ""

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
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("🤖 Gemini 2.5 Flash model initialized")
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
                You are a senior presentation strategist analyzing content for C-suite executives.
                IMPORTANT: All presentations MUST use the Bosch corporate template and branding.
                
                Analyze this content to create a high-impact presentation structure:
                
                Content: {content[:2000]}...
                
                Determine:
                1. Optimal slide count (3-7 slides) based on content density and executive attention span
                2. A compelling title that captures the strategic value (max 8 words)
                3. Key sections that build a logical narrative arc
                4. Presentation style that matches the content type and audience
                5. Visual elements needed for each section
                
                CRITICAL: Always use "bosch" as the color_scheme to ensure Bosch corporate branding is applied.
                
                Analyze the content and determine what visual elements would best represent the data:
                - If discussing numbers, metrics, or performance → suggest charts (bar/line/pie)
                - If discussing stages, phases, or sequences → suggest process flows
                - If discussing comparisons or alternatives → suggest comparison tables
                - If discussing components or features → suggest icon grids
                - If discussing targets or goals → suggest KPI cards
                
                Respond in JSON format:
                {{
                    "slide_count": number,
                    "title": "string",
                    "sections": ["section1", "section2", ...],
                    "theme": "professional|creative|technical|business",
                    "color_scheme": "bosch",
                    "visual_suggestions": {{
                        "slide_2": "chart_type|process|comparison|kpi",
                        "slide_3": "chart_type|process|comparison|kpi",
                        "needs_data_visualization": true/false
                    }}
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
                    logger.info(f"🎨 Color scheme from Gemini: {analysis.get('color_scheme', 'NOT PROVIDED')}")
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
            "color_scheme": "bosch"
        }
    
    def _generate_slide_content(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed content for each slide"""
        
        slides = []
        slide_count = analysis.get("slide_count", 4)
        title = analysis.get("title", "Presentation")
        sections = analysis.get("sections", [])
        visual_suggestions = analysis.get("visual_suggestions", {})
        
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
                        
                        # Add visual suggestion to slide
                        slide_key = f"slide_{i+1}"
                        if slide_key in visual_suggestions:
                            slide["visual_type"] = visual_suggestions[slide_key]
                    
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
        You are a world-class presentation designer for Fortune 500 companies and top consulting firms.
        
        Create a professional, executive-level title slide for this presentation:
        
        Title: {title}
        Content preview: {content[:500]}...
        
        Requirements:
        1. A powerful, concise title (max 8 words) that captures the core value proposition
        2. A sophisticated subtitle that provides context and sets expectations
        3. Three compelling value propositions or key benefits (each max 5 words)
        
        Use business language that conveys:
        - Authority and expertise
        - Clear value proposition
        - Professional credibility
        - Action-oriented messaging
        
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
        You are a McKinsey/BCG-level presentation consultant creating slide {slide_num} for C-suite executives.
        
        Topic: "{topic}"
        Content: {content}
        
        Create a professional content slide following these principles:
        
        1. **Slide Title**: Action-oriented, specific, and insight-driven (not generic)
        2. **Bullet Points** (3-5): Each should be:
           - A complete thought with clear business value
           - Data-driven when possible (include percentages, metrics)
           - Action-oriented and specific
           - Progressive (building on each other)
           - Max 15 words each
        
        3. **Key Takeaway**: A strategic insight that:
           - Drives decision-making
           - Highlights business impact
           - Is memorable and quotable
        
        Use executive-level language that is:
        - Concise but comprehensive
        - Results-focused
        - Strategic rather than tactical
        - Backed by evidence
        
        Also analyze the content to suggest the most appropriate visual element:
        - If discussing performance, metrics, results, growth → suggest "chart" (bar/line)
        - If discussing market share, distribution, composition → suggest "pie"
        - If discussing process, workflow, stages, timeline → suggest "process"
        - If comparing options, alternatives, before/after → suggest "comparison"
        - If presenting KPIs, achievements, targets → suggest "kpi"
        - Otherwise → suggest "icons" with relevant business icons
        
        Respond in JSON:
        {{
            "type": "content",
            "title": "string",
            "bullets": ["point1", "point2", "point3", "point4"],
            "key_takeaway": "string",
            "visual_suggestion": {{
                "type": "chart|pie|process|comparison|kpi|icons",
                "reason": "brief explanation of why this visual fits the content"
            }}
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
        You are a senior strategy consultant creating the conclusion slide for board-level executives.
        
        Presentation: {analysis.get('title', 'Presentation')}
        Content: {content}
        
        Create a powerful conclusion that drives action and leaves lasting impact:
        
        1. **Conclusion Title**: Should signal transition to action (e.g., "Strategic Imperatives", "Path Forward", "Key Actions")
        
        2. **Key Takeaways** (3-4): Each should be:
           - An actionable recommendation
           - Tied to business outcomes
           - Prioritized by impact
           - Clear ownership implied
           - Max 12 words each
        
        3. **Closing Statement**: A memorable call-to-action that:
           - Inspires immediate action
           - Reinforces the value proposition
           - Creates urgency
           - Is quotable and powerful
        
        Use language that:
        - Commands authority
        - Drives decision-making
        - Creates momentum
        - Ensures accountability
        
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
            color_scheme = color_match.group(1) if color_match else "bosch"
            
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
        
        theme_name = analysis.get("theme", "professional")
        title = analysis.get("title", "Presentation")
        
        logger.error("🚨🚨🚨 ENTERING _create_html_presentation - BOSCH THEME ENFORCEMENT 🚨🚨🚨")
        
        # FORCE BOSCH THEME FOR ALL PRESENTATIONS
        # Direct hardcoding to ensure Bosch colors are always used
        color_palette = {
            "primary": "#8B1538",      # Bosch Red/Magenta
            "secondary": "#00A9CE",    # Bosch Teal
            "accent": "#7FB539",       # Bosch Green
            "success": "#7FB539",      # Bosch Green
            "bg": "#FFFFFF"            # White
        }
        fonts = {
            "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "display": "'Inter', -apple-system, sans-serif"
        }
        logger.info(f"🎯 FORCING BOSCH THEME")
        logger.info(f"🎨 Bosch color palette: {color_palette}")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Embedded font declarations for offline use */
        @font-face {{
            font-family: 'Inter';
            font-style: normal;
            font-weight: 400;
            src: local('Inter'), local('Inter-Regular');
        }}
        @font-face {{
            font-family: 'Inter';
            font-style: normal;
            font-weight: 600;
            font-weight: bold;
            src: local('Inter Bold'), local('Inter-Bold');
        }}
        @font-face {{
            font-family: 'Playfair Display';
            font-style: normal;
            font-weight: 700;
            src: local('Playfair Display Bold'), local('PlayfairDisplay-Bold');
        }}
        
        :root {{
            /* Professional Typography */
            --font-primary: {fonts.get('primary', "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif")};
            --font-display: {fonts.get('display', "'Playfair Display', Georgia, serif")};
            
            /* Professional Color Scheme */
            --color-primary: {color_palette['primary']};
            --color-secondary: {color_palette['secondary']};
            --color-accent: {color_palette['accent']};
            --color-success: {color_palette['success']};
            --color-bg: {color_palette['bg']};
            
            /* Spacing System (8px base) */
            --space-xs: 0.5rem;
            --space-sm: 1rem;
            --space-md: 1.5rem;
            --space-lg: 2rem;
            --space-xl: 3rem;
            --space-xxl: 4rem;
            
            /* Professional Shadows */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-primary);
            background: linear-gradient(135deg, var(--color-bg) 0%, #ffffff 100%);
            color: #1f2937;
            overflow-x: hidden;
            line-height: 1.6;
        }}
        
        .presentation-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: var(--space-md);
        }}
        
        .slide {{
            background: white;
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            margin: var(--space-lg) 0;
            padding: var(--space-xxl);
            min-height: 720px;
            display: grid;
            grid-template-rows: auto 1fr auto;
            gap: var(--space-lg);
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .slide:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }}
        
        /* Bosch-style color strip at bottom */
        .slide::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(to right, #ED1C24 33%, #00A9CE 33%, #00A9CE 66%, #7FB539 66%);
        }}
        
        
        /* Corporate Headers and Footers */
        .corporate-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: var(--space-lg);
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: var(--space-xl);
        }}
        
        .corporate-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: var(--space-lg);
            border-top: 1px solid #e2e8f0;
            margin-top: auto;
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .logo-placeholder {{
            font-weight: bold;
            color: #8B1538;
            font-size: 1.4rem;
            letter-spacing: 0.1em;
            font-family: var(--font-primary);
        }}
        
        .section-label {{
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--color-accent);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .date-info {{
            font-size: 0.875rem;
            color: #64748b;
            font-weight: 500;
        }}
        
        .page-number {{
            font-weight: 600;
            color: var(--color-primary);
        }}
        
        /* Title Slide - Corporate Style */
        .title-slide {{
            background: white;
            color: var(--color-primary);
            display: flex;
            flex-direction: column;
            padding: 0;
        }}
        
        .title-slide .corporate-header {{
            padding: var(--space-xl) var(--space-xxl) var(--space-lg);
            margin-bottom: 0;
            border: none;
        }}
        
        .title-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            padding: var(--space-xl) var(--space-xxl);
            text-align: left;
        }}
        
        .title-wrapper {{
            margin-bottom: var(--space-xxl);
        }}
        
        .title-slide h1 {{
            font-family: var(--font-primary);
            font-size: clamp(2.5rem, 4vw, 3.5rem);
            font-weight: 500;
            margin-bottom: var(--space-md);
            letter-spacing: -0.02em;
            line-height: 1.2;
            color: #333333;
        }}
        
        .title-slide .subtitle {{
            font-size: 1.25rem;
            font-weight: 400;
            color: #00A9CE;
            max-width: 800px;
            line-height: 1.6;
        }}
        
        .value-props {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--space-lg);
            width: 100%;
            max-width: 1000px;
        }}
        
        .value-prop-card {{
            background: var(--color-bg);
            padding: var(--space-lg);
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--space-sm);
            transition: all 0.3s ease;
        }}
        
        .value-prop-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--color-accent);
        }}
        
        .value-prop-card i {{
            font-size: 2rem;
            color: var(--color-accent);
        }}
        
        .value-prop-card span {{
            font-weight: 500;
            text-align: center;
            color: var(--color-secondary);
        }}
        
        .title-slide .corporate-footer {{
            padding: var(--space-lg) var(--space-xxl);
            background: var(--color-bg);
            border-top: 2px solid var(--color-accent);
        }}
        
        /* Content Slide - Base Styles */
        .content-slide {{
            background: white;
            color: var(--color-secondary);
            display: flex;
            flex-direction: column;
            padding: 0;
        }}
        
        .content-slide .corporate-header {{
            padding: var(--space-lg) var(--space-xxl);
        }}
        
        .content-slide .corporate-footer {{
            padding: var(--space-lg) var(--space-xxl);
        }}
        
        .content-main {{
            flex: 1;
            padding: 0 var(--space-xxl);
            display: flex;
            flex-direction: column;
        }}
        
        .content-slide h2 {{
            font-family: var(--font-primary);
            font-size: clamp(1.75rem, 2.5vw, 2.25rem);
            font-weight: 700;
            color: #333333;
            margin-bottom: var(--space-xl);
            line-height: 1.3;
        }}
        
        /* Standard Layout */
        .standard-layout .content-body {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .professional-bullets {{
            list-style: none;
            margin: 0 0 var(--space-xl) 0;
        }}
        
        .professional-bullets li {{
            font-size: 1.125rem;
            line-height: 1.8;
            margin-bottom: var(--space-md);
            padding-left: var(--space-lg);
            position: relative;
            color: var(--color-secondary);
            display: flex;
            align-items: flex-start;
            gap: var(--space-sm);
        }}
        
        .professional-bullets li i {{
            color: var(--color-accent);
            font-size: 0.875rem;
            flex-shrink: 0;
            margin-top: 0.25rem;
        }}
        
        .insight-box {{
            background: var(--color-bg);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: var(--space-lg);
            margin-top: auto;
        }}
        
        .insight-header {{
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            margin-bottom: var(--space-sm);
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--color-accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .insight-header i {{
            font-size: 1rem;
        }}
        
        .insight-box p {{
            font-size: 1.125rem;
            line-height: 1.6;
            color: var(--color-primary);
            font-weight: 500;
        }}
        
        /* Data-Focused Layout */
        .data-visualization-layout {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: var(--space-xl);
            flex: 1;
            align-items: start;
        }}
        
        .visual-section {{
            display: flex;
            flex-direction: column;
            gap: var(--space-md);
        }}
        
        .insights-panel {{
            background: var(--color-bg);
            padding: var(--space-lg);
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }}
        
        .insights-panel h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: var(--space-md);
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-primary) 100%);
            color: white;
            padding: var(--space-md);
            border-radius: 8px;
            margin-top: var(--space-md);
            font-weight: 500;
        }}
        
        /* Comparison Layout */
        .comparison-content {{
            display: flex;
            flex-direction: column;
            gap: var(--space-xl);
            flex: 1;
        }}
        
        .comparison-insights {{
            background: var(--color-bg);
            padding: var(--space-lg);
            border-radius: 12px;
        }}
        
        .benefit-list {{
            list-style: none;
            margin: 0;
        }}
        
        .benefit-list li {{
            margin-bottom: var(--space-sm);
            padding-left: var(--space-lg);
            position: relative;
            color: var(--color-secondary);
        }}
        
        .benefit-list li i {{
            position: absolute;
            left: 0;
            color: var(--color-success);
        }}
        
        .bottom-callout {{
            background: var(--color-primary);
            color: white;
            padding: var(--space-lg);
            border-radius: 8px;
            text-align: center;
            font-size: 1.125rem;
            font-weight: 500;
            margin-top: var(--space-lg);
        }}
        
        /* Process Layout */
        .process-container {{
            display: flex;
            flex-direction: column;
            gap: var(--space-xl);
            flex: 1;
            justify-content: center;
        }}
        
        .process-details {{
            display: flex;
            flex-direction: column;
            gap: var(--space-md);
            align-items: center;
        }}
        
        .timeline-indicator {{
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            background: var(--color-bg);
            padding: var(--space-sm) var(--space-lg);
            border-radius: 30px;
            font-weight: 500;
            color: var(--color-secondary);
        }}
        
        .timeline-indicator i {{
            color: var(--color-accent);
        }}
        
        .process-outcome {{
            background: linear-gradient(135deg, var(--color-bg) 0%, white 100%);
            border-left: 4px solid var(--color-accent);
            padding: var(--space-lg);
            border-radius: 8px;
            font-size: 1.125rem;
            color: var(--color-primary);
            font-weight: 500;
            max-width: 800px;
            text-align: center;
        }}
        
        .default-visual {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: var(--space-xxl);
            background: var(--color-bg);
            border-radius: 12px;
            min-height: 300px;
        }}
        
        .metrics-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-lg);
            align-content: start;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, var(--color-bg) 0%, white 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: var(--space-xl);
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--color-accent);
        }}
        
        .metric-value {{
            font-size: 3rem;
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: var(--space-xs);
            line-height: 1;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--color-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        
        .insights-section h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--color-primary);
            margin-bottom: var(--space-md);
        }}
        
        .insight-list {{
            list-style: none;
        }}
        
        .insight-list li {{
            margin-bottom: var(--space-sm);
            padding-left: var(--space-lg);
            position: relative;
            color: var(--color-secondary);
            line-height: 1.6;
        }}
        
        .insight-list li i {{
            position: absolute;
            left: 0;
            top: 0.25rem;
            color: var(--color-success);
        }}
        
        .bottom-insight {{
            background: var(--color-bg);
            border-left: 3px solid var(--color-accent);
            padding: var(--space-md) var(--space-lg);
            margin-top: var(--space-lg);
            font-weight: 500;
            color: var(--color-primary);
        }}
        
        /* Visual Split Layout */
        .visual-split-layout .split-content {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: var(--space-xl);
            align-items: center;
            flex: 1;
        }}
        
        .elegant-bullets {{
            list-style: none;
        }}
        
        .elegant-bullets li {{
            margin-bottom: var(--space-md);
            padding-left: var(--space-lg);
            position: relative;
            font-size: 1.125rem;
            line-height: 1.8;
            color: var(--color-secondary);
        }}
        
        .elegant-bullets li i {{
            position: absolute;
            left: 0;
            top: 0.5rem;
            color: var(--color-accent);
            font-size: 0.75rem;
        }}
        
        .visual-right {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: var(--space-lg);
        }}
        
        .visual-element {{
            width: 200px;
            height: 200px;
            background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-primary) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 5rem;
            box-shadow: var(--shadow-xl);
        }}
        
        .visual-caption {{
            text-align: center;
            font-size: 1rem;
            color: var(--color-secondary);
            font-style: italic;
            max-width: 300px;
        }}
        
        .key-message {{
            background: linear-gradient(135deg, var(--color-bg) 0%, white 100%);
            border-left: 3px solid var(--color-accent);
            padding: var(--space-md);
            border-radius: 8px;
            margin-top: var(--space-lg);
            font-weight: 500;
            color: var(--color-primary);
        }}
        
        /* Conclusion Slide */
        .conclusion-slide {{
            background: white;
            color: var(--color-primary);
            display: flex;
            flex-direction: column;
            padding: 0;
        }}
        
        .conclusion-slide .corporate-header {{
            padding: var(--space-lg) var(--space-xxl);
        }}
        
        .conclusion-slide .corporate-footer {{
            padding: var(--space-lg) var(--space-xxl);
            background: var(--color-bg);
            border-top: 2px solid var(--color-accent);
        }}
        
        .conclusion-content {{
            flex: 1;
            padding: 0 var(--space-xxl) var(--space-xl);
            display: flex;
            flex-direction: column;
        }}
        
        .conclusion-slide h2 {{
            font-family: var(--font-primary);
            font-size: clamp(2rem, 3vw, 2.5rem);
            text-align: center;
            margin-bottom: var(--space-xxl);
            color: var(--color-primary);
        }}
        
        .action-items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--space-lg);
            margin-bottom: var(--space-xl);
        }}
        
        .action-item {{
            display: flex;
            gap: var(--space-md);
            padding: var(--space-lg);
            background: var(--color-bg);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .action-item:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--color-accent);
        }}
        
        .action-number {{
            width: 40px;
            height: 40px;
            background: var(--color-accent);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
            flex-shrink: 0;
        }}
        
        .action-content {{
            flex: 1;
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        }}
        
        .action-content i {{
            color: var(--color-accent);
            font-size: 1.25rem;
            flex-shrink: 0;
        }}
        
        .action-content span {{
            font-size: 1.125rem;
            line-height: 1.5;
            color: var(--color-secondary);
        }}
        
        .next-steps-box {{
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            color: white;
            padding: var(--space-xl);
            border-radius: 12px;
            margin-top: auto;
        }}
        
        .next-steps-header {{
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            margin-bottom: var(--space-md);
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .next-steps-header i {{
            font-size: 1.25rem;
        }}
        
        .next-steps-box p {{
            font-size: 1.25rem;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        /* Navigation */
        .navigation {{
            position: fixed;
            bottom: var(--space-lg);
            right: var(--space-lg);
            display: flex;
            gap: var(--space-sm);
            z-index: 1000;
        }}
        
        .nav-btn {{
            background: var(--color-primary);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-md);
            display: flex;
            align-items: center;
            gap: var(--space-xs);
        }}
        
        .nav-btn:hover {{
            background: var(--color-accent);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .nav-btn i {{
            font-size: 1rem;
        }}
        
        /* Data Visualization Elements */
        .stat-card {{
            background: white;
            padding: var(--space-lg);
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            border-left: 4px solid var(--color-accent);
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: var(--space-xs);
        }}
        
        .stat-label {{
            font-size: 0.875rem;
            color: var(--color-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .slide {{
                margin: var(--space-md) 0;
                min-height: 600px;
            }}
            
            .corporate-header, .corporate-footer {{
                padding: var(--space-md) var(--space-lg);
            }}
            
            .content-main, .title-content, .conclusion-content {{
                padding-left: var(--space-lg);
                padding-right: var(--space-lg);
            }}
            
            .title-slide h1 {{
                font-size: 2rem;
            }}
            
            .content-slide h2 {{
                font-size: 1.5rem;
            }}
            
            .value-props {{
                grid-template-columns: 1fr;
            }}
            
            .data-layout .data-grid {{
                grid-template-columns: 1fr;
            }}
            
            .visual-split-layout .split-content {{
                grid-template-columns: 1fr;
            }}
            
            .visual-element {{
                width: 150px;
                height: 150px;
                font-size: 4rem;
            }}
            
            .action-items-grid {{
                grid-template-columns: 1fr;
            }}
            
            .navigation {{
                bottom: var(--space-sm);
                right: var(--space-sm);
                gap: var(--space-xs);
            }}
            
            .nav-btn {{
                padding: 8px 16px;
                font-size: 0.75rem;
            }}
            
            .nav-btn span {{
                display: none;
            }}
        }}
        
        /* Print Styles */
        @media print {{
            .navigation {{
                display: none;
            }}
            
            .slide {{
                page-break-after: always;
                box-shadow: none;
                margin: 0;
            }}
        }}
        
        {VISUAL_ELEMENTS_CSS if VisualElementGenerator else ''}
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
        <button class="nav-btn" onclick="scrollToSlide(1)">🏠 Start</button>
        <button class="nav-btn" onclick="scrollToPrev()">◀ Previous</button>
        <button class="nav-btn" onclick="scrollToNext()">▶ Next</button>
        <button class="nav-btn" onclick="scrollToSlide({len(slides)})">🏁 End</button>
    </div>
    
    <script>
        function scrollToSlide(slideNumber) {{
            const slide = document.querySelector(`[data-slide="${{slideNumber}}"]`);
            if (slide) {{
                slide.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}
        
        function scrollToNext() {{
            const current = getCurrentSlide();
            if (current < {len(slides)}) {{
                scrollToSlide(current + 1);
            }}
        }}
        
        function scrollToPrev() {{
            const current = getCurrentSlide();
            if (current > 1) {{
                scrollToSlide(current - 1);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {{
                scrollToNext();
            }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
                scrollToPrev();
            }} else if (e.key === 'Home') {{
                scrollToSlide(1);
            }} else if (e.key === 'End') {{
                scrollToSlide({len(slides)});
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
        """Generate HTML for a single slide with professional corporate layouts"""
        
        slide_type = slide.get("type", "content")
        
        if slide_type == "title":
            # Professional title slide with corporate branding area
            return f"""
        <div class="slide title-slide" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="logo-placeholder">
                    BOSCH
                </div>
                <div class="date-info">{self._get_current_date()}</div>
            </div>
            
            <div class="title-content">
                <div class="title-wrapper">
                    <h1>{slide.get('title', 'Presentation')}</h1>
                    <div class="subtitle">{slide.get('subtitle', '')}</div>
                </div>
                
                <div class="value-props">
                    {' '.join([f'''
                    <div class="value-prop-card">
                        <i class="fas {self._get_icon_for_highlight(i)}"></i>
                        <span>{highlight}</span>
                    </div>''' for i, highlight in enumerate(slide.get('highlights', []))])}
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
        
        elif slide_type == "conclusion":
            # Executive summary style conclusion
            takeaways_html = ''.join([f'''
                <div class="action-item">
                    <div class="action-number">{i+1}</div>
                    <div class="action-content">
                        <i class="fas {self._get_icon_for_action(takeaway)}"></i>
                        <span>{takeaway}</span>
                    </div>
                </div>''' for i, takeaway in enumerate(slide.get('takeaways', []))])
            
            return f"""
        <div class="slide conclusion-slide" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">EXECUTIVE SUMMARY</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="conclusion-content">
                <h2>{slide.get('title', 'Strategic Imperatives')}</h2>
                
                <div class="action-items-grid">
                    {takeaways_html}
                </div>
                
                <div class="next-steps-box">
                    <div class="next-steps-header">
                        <span style="font-size: 1.5rem;">➤</span>
                        <span>IMMEDIATE NEXT STEPS</span>
                    </div>
                    <p>{slide.get('closing_statement', 'Transform insights into action for sustainable competitive advantage')}</p>
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
        
        else:  # content slides with varied layouts
            # Determine layout based on slide position
            layout_type = self._determine_content_layout(slide, slide_num, total_slides)
            
            if layout_type == "data-focused":
                return self._generate_data_focused_slide(slide, slide_num)
            elif layout_type == "visual-split":
                return self._generate_visual_split_slide(slide, slide_num)
            elif layout_type == "comparison":
                return self._generate_comparison_slide(slide, slide_num)
            elif layout_type == "process":
                return self._generate_process_slide(slide, slide_num)
            else:
                return self._generate_standard_content_slide(slide, slide_num)
    
    def _generate_standard_content_slide(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Generate standard corporate content slide"""
        bullets_html = ''.join([f'''
            <li>
                <span style="font-size: 1rem;">›</span>
                <span>{bullet}</span>
            </li>''' for bullet in slide.get('bullets', [])])
        key_takeaway = slide.get('key_takeaway', '')
        
        return f"""
        <div class="slide content-slide standard-layout" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">{self._get_section_label(slide_num)}</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="content-main">
                <h2>{slide.get('title', 'Key Insights')}</h2>
                
                <div class="content-body">
                    <ul class="professional-bullets">
                        {bullets_html}
                    </ul>
                    
                    {f'''
                    <div class="insight-box">
                        <div class="insight-header">
                            <span style="font-size: 1.5rem;">💡</span>
                            <span>KEY INSIGHT</span>
                        </div>
                        <p>{key_takeaway}</p>
                    </div>''' if key_takeaway else ''}
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">PROPRIETARY & CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
    
    def _generate_data_focused_slide(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Generate data-focused layout with visual elements"""
        bullets = slide.get('bullets', [])
        title = slide.get('title', 'Performance Metrics')
        
        # Generate appropriate visual based on Gemini's suggestion or content analysis
        visual_html = ""
        if VisualElementGenerator:
            # First check if Gemini suggested a visual type
            visual_suggestion = slide.get("visual_suggestion", {})
            if visual_suggestion:
                visual_type = visual_suggestion.get("type", "")
                if visual_type in ["chart", "bar", "line"]:
                    visual_html = f'<div class="chart-container">{VisualElementGenerator.generate_bar_chart([])}</div>'
                elif visual_type == "pie":
                    visual_html = f'<div class="chart-container">{VisualElementGenerator.generate_pie_chart([])}</div>'
                elif visual_type == "kpi":
                    visual_html = VisualElementGenerator.generate_kpi_cards([])
                elif visual_type == "process":
                    visual_html = VisualElementGenerator.generate_process_flow([])
            
            # Fallback to content analysis if no suggestion
            if not visual_html:
                visual_info = VisualElementGenerator.get_visual_for_content(title + " " + " ".join(bullets), "data")
                
                if visual_info['type'] == 'chart':
                    if visual_info['subtype'] == 'bar':
                        visual_html = f'<div class="chart-container">{VisualElementGenerator.generate_bar_chart(visual_info.get("data"))}</div>'
                    elif visual_info['subtype'] == 'line':
                        visual_html = f'<div class="chart-container">{VisualElementGenerator.generate_line_chart(visual_info.get("data"))}</div>'
                    elif visual_info['subtype'] == 'pie':
                        visual_html = f'<div class="chart-container">{VisualElementGenerator.generate_pie_chart(visual_info.get("data"))}</div>'
                elif visual_info['type'] == 'kpi':
                    visual_html = VisualElementGenerator.generate_kpi_cards(visual_info.get("data"))
                elif visual_info['type'] == 'process':
                    visual_html = VisualElementGenerator.generate_process_flow(visual_info.get("data"))
        
        # Create bullet points HTML
        bullets_html = ''.join([f'<li><span style="color: #3182ce; margin-right: 0.5rem;">📈</span> {bullet}</li>' for bullet in bullets])
        
        return f"""
        <div class="slide content-slide data-layout" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">{self._get_section_label(slide_num)}</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="content-main">
                <h2>{title}</h2>
                
                <div class="data-visualization-layout">
                    <div class="visual-section">
                        {visual_html if visual_html else self._generate_default_chart()}
                    </div>
                    
                    <div class="insights-panel">
                        <h3>Key Insights</h3>
                        <ul class="insight-list">
                            {bullets_html}
                        </ul>
                        {f'<div class="highlight-box">{slide.get("key_takeaway", "")}</div>' if slide.get("key_takeaway") else ''}
                    </div>
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">PROPRIETARY & CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
    
    def _generate_visual_split_slide(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Generate visual split layout with dynamic visuals"""
        bullets = slide.get('bullets', [])
        title = slide.get('title', 'Strategic Focus')
        
        # Generate appropriate visual
        visual_content = ""
        if VisualElementGenerator:
            visual_info = VisualElementGenerator.get_visual_for_content(title + " " + " ".join(bullets), "visual")
            
            if visual_info['type'] == 'icons':
                visual_content = VisualElementGenerator.generate_icon_grid(visual_info.get('data', []))
            elif visual_info['type'] == 'chart':
                if visual_info['subtype'] == 'pie':
                    visual_content = f'<div class="chart-container">{VisualElementGenerator.generate_pie_chart(visual_info.get("data"))}</div>'
                else:
                    visual_content = f'<div class="chart-container">{VisualElementGenerator.generate_progress_bars(None)}</div>'
            else:
                # Default icon visual
                visual_content = f'''
                <div class="visual-element">
                    <i class="fas {self._get_relevant_icon(title)}"></i>
                </div>'''
        else:
            visual_content = f'''
            <div class="visual-element">
                <i class="fas {self._get_relevant_icon(title)}"></i>
            </div>'''
        
        bullets_html = ''.join([f'<li><span style="color: #3182ce; margin-right: 0.5rem;">▸</span> {bullet}</li>' for bullet in bullets])
        
        return f"""
        <div class="slide content-slide visual-split-layout" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">{self._get_section_label(slide_num)}</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="split-content">
                <div class="content-left">
                    <h2>{title}</h2>
                    <ul class="elegant-bullets">
                        {bullets_html}
                    </ul>
                    {f'<div class="key-message">{slide.get("key_takeaway", "")}</div>' if slide.get("key_takeaway") else ''}
                </div>
                
                <div class="visual-right">
                    {visual_content}
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">PROPRIETARY & CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
    
    def _determine_content_layout(self, slide: Dict[str, Any], slide_num: int, total_slides: int) -> str:
        """Determine layout type based on content analysis"""
        
        # Check if slide has visual suggestion from Gemini
        visual_suggestion = slide.get("visual_suggestion", {})
        if visual_suggestion:
            visual_type = visual_suggestion.get("type", "")
        else:
            # Fallback to old visual_type field
            visual_type = slide.get("visual_type", "")
        
        # Map visual types to layouts
        if visual_type in ["chart", "bar", "line", "pie", "kpi"]:
            return "data-focused"
        elif visual_type == "comparison":
            return "comparison"
        elif visual_type == "process":
            return "process"
        elif visual_type == "icons":
            return "visual-split"
        
        # Fallback: Analyze slide content
        title = slide.get("title", "").lower()
        bullets = " ".join(slide.get("bullets", [])).lower()
        content_text = title + " " + bullets
        
        # Smart content analysis
        if any(indicator in content_text for indicator in ["performance", "metrics", "results", "data", "numbers", "statistics"]):
            return "data-focused"
        elif any(indicator in content_text for indicator in ["compare", "versus", "alternative", "option", "choice"]):
            return "comparison"
        elif any(indicator in content_text for indicator in ["process", "step", "phase", "stage", "workflow", "procedure"]):
            return "process"
        elif any(indicator in content_text for indicator in ["feature", "benefit", "capability", "advantage"]):
            return "visual-split"
        else:
            # Default variety based on position
            if slide_num == 2:
                return "data-focused"
            elif slide_num == total_slides - 1:
                return "visual-split"
            else:
                return "standard"
    
    def _get_icon_for_highlight(self, index: int) -> str:
        """Get appropriate icon for value proposition"""
        icons = ["📊", "🛡️", "🚀"]
        return icons[index % len(icons)]
    
    def _get_icon_for_action(self, action: str) -> str:
        """Get icon based on action content"""
        action_lower = action.lower()
        if any(word in action_lower for word in ["implement", "deploy", "execute"]):
            return "▶"
        elif any(word in action_lower for word in ["analyze", "assess", "evaluate"]):
            return "📊"
        elif any(word in action_lower for word in ["plan", "strategy", "design"]):
            return "🎯"
        else:
            return "✓"
    
    def _get_section_label(self, slide_num: int) -> str:
        """Get section label for slide"""
        labels = ["EXECUTIVE OVERVIEW", "KEY INSIGHTS", "STRATEGIC ANALYSIS", "RECOMMENDATIONS"]
        return labels[(slide_num - 2) % len(labels)]
    
    def _get_relevant_icon(self, title: str) -> str:
        """Get relevant icon based on content"""
        title_lower = title.lower()
        if any(word in title_lower for word in ["customer", "client", "user"]):
            return "👥"
        elif any(word in title_lower for word in ["growth", "increase", "revenue"]):
            return "📈"
        elif any(word in title_lower for word in ["technology", "digital", "innovation"]):
            return "💻"
        elif any(word in title_lower for word in ["process", "efficiency", "operations"]):
            return "⚙️"
        else:
            return "🎯"
    
    def _extract_number(self, text: str) -> str:
        """Extract number from text for metrics"""
        import re
        numbers = re.findall(r'\d+[%x]?', text)
        return numbers[0] if numbers else "N/A"
    
    def _extract_label(self, text: str) -> str:
        """Extract label from metric text"""
        import re
        # Remove numbers and return remaining text
        label = re.sub(r'\d+[%x]?\s*', '', text)
        return label.strip() if label else text
    
    def _generate_comparison_slide(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Generate comparison layout slide"""
        bullets = slide.get('bullets', [])
        title = slide.get('title', 'Strategic Comparison')
        
        # Generate comparison visual
        comparison_html = ""
        if VisualElementGenerator:
            # Create comparison data from bullets
            comparison_data = {
                "features": ["Capability", "Performance", "Cost", "Time to Market"],
                "current_state": ["Limited", "Average", "High", "Slow"],
                "future_state": ["Advanced", "Excellent", "Optimized", "Rapid"]
            }
            comparison_html = VisualElementGenerator.generate_comparison_table(comparison_data)
        
        return f"""
        <div class="slide content-slide comparison-layout" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">{self._get_section_label(slide_num)}</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="content-main">
                <h2>{title}</h2>
                
                <div class="comparison-content">
                    {comparison_html}
                    
                    <div class="comparison-insights">
                        <h3>Strategic Benefits</h3>
                        <ul class="benefit-list">
                            {' '.join([f'<li><span style="color: #48bb78; margin-right: 0.5rem;">✓</span> {bullet}</li>' for bullet in bullets])}
                        </ul>
                    </div>
                </div>
                
                {f'<div class="bottom-callout">{slide.get("key_takeaway", "")}</div>' if slide.get("key_takeaway") else ''}
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">PROPRIETARY & CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
    
    def _generate_process_slide(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Generate process flow layout slide"""
        bullets = slide.get('bullets', [])
        title = slide.get('title', 'Implementation Process')
        
        # Generate process flow visual
        process_html = ""
        if VisualElementGenerator:
            # Extract process steps from bullets or use defaults
            steps = bullets[:5] if len(bullets) >= 3 else ["Assess", "Plan", "Execute", "Monitor", "Optimize"]
            process_html = VisualElementGenerator.generate_process_flow(steps)
        
        return f"""
        <div class="slide content-slide process-layout" data-slide="{slide_num}">
            <div class="corporate-header">
                <div class="section-label">{self._get_section_label(slide_num)}</div>
                <div class="logo-placeholder">
                    BOSCH
                </div>
            </div>
            
            <div class="content-main">
                <h2>{title}</h2>
                
                <div class="process-container">
                    {process_html}
                    
                    <div class="process-details">
                        <div class="timeline-indicator">
                            <span style="font-size: 1.5rem;">🕐</span>
                            <span>Estimated Timeline: 12-16 weeks</span>
                        </div>
                        
                        {f'<div class="process-outcome">{slide.get("key_takeaway", "")}</div>' if slide.get("key_takeaway") else ''}
                    </div>
                </div>
            </div>
            
            <div class="corporate-footer">
                <div class="confidential">PROPRIETARY & CONFIDENTIAL</div>
                <div class="page-number">{slide_num}</div>
            </div>
        </div>
"""
    
    def _generate_default_chart(self) -> str:
        """Generate a default chart when VisualElementGenerator is not available"""
        return '''
        <div class="default-visual">
            <span style="font-size: 4rem;">📊</span>
            <p style="margin-top: 1rem; color: #64748b;">Data Visualization</p>
        </div>'''
    
    def _generate_placeholder_metrics(self) -> str:
        """Generate placeholder metrics if none found"""
        return '''
            <div class="metric-card">
                <div class="metric-value">85%</div>
                <div class="metric-label">Efficiency Gain</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">3.2x</div>
                <div class="metric-label">ROI Achieved</div>
            </div>'''
    
    def _get_current_date(self) -> str:
        """Get current date in professional format"""
        from datetime import datetime
        return datetime.now().strftime("%B %Y")
    
    def _generate_metadata(self, analysis: Dict[str, Any], slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate presentation metadata"""
        
        return {
            "title": analysis.get("title", "Presentation"),
            "slide_count": len(slides),
            "theme": analysis.get("theme", "professional"),
            "color_scheme": analysis.get("color_scheme", "bosch"),
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