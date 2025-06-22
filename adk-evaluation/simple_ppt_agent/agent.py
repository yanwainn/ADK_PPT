"""
Enhanced PowerPoint Agent with Gemini LLM Integration for actual content generation.
"""

import os
import sys
import json
import traceback
from typing import Dict, Any
from datetime import datetime
import time
from collections import deque

# Add parent directory to path to access modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from google.adk.agents import Agent

# Import the working sequential workflow system and HTML generator
try:
    from modules.sequential_agents import SequentialWorkflowCoordinator
    from modules.html_presentation_generator import HTMLPresentationGenerator
    SEQUENTIAL_AVAILABLE = True
    HTML_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Sequential agents not available: {e}")
    SequentialWorkflowCoordinator = None
    HTMLPresentationGenerator = None
    SEQUENTIAL_AVAILABLE = False
    HTML_GENERATOR_AVAILABLE = False

# Import Gemini API for content generation
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print("🔑 Gemini API configured for HTML generation")
    else:
        GEMINI_AVAILABLE = False
        print("⚠️ Gemini API key not found")
        
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API not available")


class RateLimitManager:
    """Manages API rate limiting to avoid quota exceeded errors"""
    
    def __init__(self, max_requests_per_minute=8):  # Set to 8 to stay under 10/min limit
        self.max_requests = max_requests_per_minute
        self.request_times = deque()
        self.last_request_time = 0
        self.min_interval = 60.0 / max_requests_per_minute  # Minimum seconds between requests
    
    def can_make_request(self) -> bool:
        """Check if we can make a request without hitting rate limits"""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # Check if we're under the rate limit
        if len(self.request_times) >= self.max_requests:
            return False
        
        # Check minimum interval between requests
        if now - self.last_request_time < self.min_interval:
            return False
        
        return True
    
    def record_request(self):
        """Record that a request was made"""
        now = time.time()
        self.request_times.append(now)
        self.last_request_time = now
    
    def wait_if_needed(self):
        """Wait if necessary to avoid rate limits"""
        if not self.can_make_request():
            wait_time = self.min_interval - (time.time() - self.last_request_time)
            if wait_time > 0:
                print(f"⏱️ Rate limit protection: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)


class GeminiHTMLGenerator:
    """
    Gemini-powered HTML presentation generator with rate limiting
    """
    
    def __init__(self):
        self.model_name = "gemini-2.0-flash-exp"
        self.model = None
        self.rate_limiter = RateLimitManager()
        self.fallback_mode = False
        
        if GEMINI_AVAILABLE:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                print(f"🤖 Gemini HTML generator initialized with rate limiting")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
                self.fallback_mode = True
    
    def generate_slide_content(self, slide_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate actual content for a slide using Gemini with rate limiting"""
        if not self.model or self.fallback_mode:
            print("📝 Using fallback content generation")
            return self._fallback_slide_content(slide_data)
        
        # Check rate limits
        if not self.rate_limiter.can_make_request():
            print("⚠️ Rate limit reached, using fallback content")
            return self._fallback_slide_content(slide_data)
        
        try:
            # Wait if needed to respect rate limits
            self.rate_limiter.wait_if_needed()
            
            slide_type = slide_data.get("type", "content")
            slide_title = slide_data.get("title", "")
            
            if slide_type == "title":
                prompt = f"""
Create engaging content for a title slide of a professional presentation:

Title: {slide_title}
Context: {context[:500]}...

Generate:
1. A compelling subtitle (max 15 words)
2. 2-3 key highlights or value propositions as bullet points
3. Professional tone appropriate for business presentation

Format as JSON with keys: subtitle, highlights
"""
            
            elif slide_type == "conclusion":
                prompt = f"""
Create compelling conclusion content for a presentation:

Title: {slide_title}
Context: {context[:500]}...

Generate:
1. 4-5 key takeaways or summary points
2. 2-3 actionable next steps or recommendations
3. A memorable closing statement

Format as JSON with keys: takeaways, next_steps, closing_statement
"""
            
            else:  # content slide
                prompt = f"""
Create detailed content for a presentation slide:

Slide Title: {slide_title}
Context: {context[:800]}...

Generate:
1. 4-6 detailed bullet points that are informative and engaging
2. A key insight or main message for this slide
3. Supporting details or examples where relevant

Make the content professional, actionable, and valuable to the audience.
Format as JSON with keys: bullet_points, key_message, supporting_details
"""
            
            # Record the request and make the API call
            self.rate_limiter.record_request()
            response = self.model.generate_content(prompt)
            
            # Clean the response text and try to parse JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse JSON response
            try:
                content_data = json.loads(response_text)
                print(f"✅ Generated content for {slide_type} slide")
                return content_data
            except json.JSONDecodeError:
                # If JSON parsing fails, extract content manually
                return self._parse_text_response(response.text, slide_type)
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⚠️ Rate limit exceeded, switching to fallback mode")
                self.fallback_mode = True  # Switch to fallback mode for remaining requests
            else:
                print(f"⚠️ Gemini content generation failed: {e}")
            return self._fallback_slide_content(slide_data)
    
    def _parse_text_response(self, text: str, slide_type: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if slide_type == "title":
            return {
                "subtitle": "Professional Insights and Analysis",
                "highlights": lines[:3] if lines else ["Key insights", "Data-driven analysis", "Strategic recommendations"]
            }
        elif slide_type == "conclusion":
            return {
                "takeaways": lines[:5] if lines else ["Key insight 1", "Key insight 2", "Key insight 3"],
                "next_steps": ["Review findings", "Implement recommendations"],
                "closing_statement": "Thank you for your attention"
            }
        else:
            return {
                "bullet_points": lines[:6] if lines else ["Key point 1", "Key point 2", "Key point 3"],
                "key_message": "Important insight from analysis",
                "supporting_details": "Additional context and examples"
            }
    
    def _fallback_slide_content(self, slide_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback content when Gemini is not available"""
        slide_type = slide_data.get("type", "content")
        
        if slide_type == "title":
            return {
                "subtitle": "Professional Analysis and Insights",
                "highlights": ["Data-driven insights", "Strategic recommendations", "Actionable outcomes"]
            }
        elif slide_type == "conclusion":
            return {
                "takeaways": ["Key findings summarized", "Strategic implications identified", "Clear next steps outlined"],
                "next_steps": ["Review recommendations", "Develop action plan"],
                "closing_statement": "Thank you for your attention"
            }
        else:
            return {
                "bullet_points": ["Professional insight from analysis", "Supporting evidence and data", "Strategic implications", "Recommended actions"],
                "key_message": "Important takeaway from the content analysis",
                "supporting_details": "Additional context and supporting information"
            }

    def generate_color_palette(self, themes: list) -> Dict[str, str]:
        """Generate color palette based on themes with rate limiting"""
        if not self.model or self.fallback_mode:
            print("🎨 Using default color palette")
            return self._default_color_palette()
        
        # Check rate limits for color palette generation
        if not self.rate_limiter.can_make_request():
            print("⚠️ Rate limit reached, using default colors")
            return self._default_color_palette()
        
        try:
            # Wait if needed to respect rate limits
            self.rate_limiter.wait_if_needed()
            
            prompt = f"""
Based on these presentation themes: {', '.join(themes)}, suggest a professional color palette.

Generate 5 hex colors for:
1. Primary (main headers, titles)
2. Secondary (subheadings, accents)  
3. Background (slide backgrounds)
4. Text (main text color)
5. Accent (highlights, call-outs)

Consider the themes and suggest colors that convey professionalism and match the content type.
Return as JSON with keys: primary, secondary, background, text, accent
"""
            
            # Record the request and make the API call
            self.rate_limiter.record_request()
            response = self.model.generate_content(prompt)
            try:
                colors = json.loads(response.text)
                print("✅ Generated custom color palette")
                return colors
            except:
                return self._default_color_palette()
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⚠️ Rate limit exceeded for colors, using default palette")
                self.fallback_mode = True
            else:
                print(f"⚠️ Color palette generation failed: {e}")
            return self._default_color_palette()
    
    def _default_color_palette(self) -> Dict[str, str]:
        """Default professional color palette"""
        return {
            "primary": "#2c3e50",
            "secondary": "#3498db", 
            "background": "#ffffff",
            "text": "#2c3e50",
            "accent": "#e74c3c"
        }

# Initialize HTML generator
html_generator = GeminiHTMLGenerator()


def generate_enhanced_html(result_data: Dict[str, Any], title: str, document_text: str) -> str:
    """Generate enhanced HTML presentation using Gemini LLM."""
    slides = result_data.get("slide_structure", result_data.get("slides", []))
    metadata = result_data.get("metadata", {})
    themes = metadata.get("themes", result_data.get("themes", ["General"]))
    
    # Generate color palette based on themes
    colors = html_generator.generate_color_palette(themes)
    
    # Generate actual slide content using Gemini
    enhanced_slides = []
    for slide in slides:
        enhanced_content = html_generator.generate_slide_content(slide, document_text)
        enhanced_slides.append({**slide, "enhanced_content": enhanced_content})
    
    html = f"""<!DOCTYPE html>
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
            background: linear-gradient(135deg, {colors['background']} 0%, #f8f9fa 100%);
            color: {colors['text']};
            line-height: 1.6;
        }}
        
        .presentation-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .slide {{
            background: {colors['background']};
            margin: 30px 0;
            padding: 60px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid {colors['primary']};
            min-height: 400px;
            position: relative;
            overflow: hidden;
        }}
        
        .slide::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: linear-gradient(45deg, {colors['accent']}20, transparent);
            border-radius: 0 15px 0 100px;
        }}
        
        .slide-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            background: {colors['primary']};
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .title-slide {{
            text-align: center;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            border: none;
        }}
        
        .title-slide h1 {{
            font-size: 3.5em;
            margin-bottom: 20px;
            font-weight: 300;
            letter-spacing: -1px;
        }}
        
        .title-slide .subtitle {{
            font-size: 1.4em;
            margin-bottom: 40px;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .title-slide .highlights {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 40px;
        }}
        
        .highlight-item {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 25px;
            font-size: 1.1em;
            backdrop-filter: blur(10px);
        }}
        
        .content-slide h2 {{
            color: {colors['primary']};
            font-size: 2.5em;
            margin-bottom: 30px;
            font-weight: 600;
            position: relative;
        }}
        
        .content-slide h2::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 80px;
            height: 4px;
            background: {colors['accent']};
            border-radius: 2px;
        }}
        
        .bullet-points {{
            list-style: none;
            margin: 30px 0;
        }}
        
        .bullet-points li {{
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-left: 40px;
            position: relative;
            line-height: 1.6;
        }}
        
        .bullet-points li::before {{
            content: '▶';
            position: absolute;
            left: 0;
            color: {colors['accent']};
            font-size: 1.2em;
            top: 2px;
        }}
        
        .key-message {{
            background: linear-gradient(90deg, {colors['secondary']}15, transparent);
            padding: 25px;
            border-left: 4px solid {colors['secondary']};
            margin: 30px 0;
            border-radius: 0 10px 10px 0;
            font-style: italic;
            font-size: 1.2em;
            color: {colors['primary']};
        }}
        
        .conclusion-slide {{
            background: linear-gradient(135deg, {colors['secondary']} 0%, {colors['primary']} 100%);
            color: white;
            border: none;
        }}
        
        .conclusion-slide h2 {{
            color: white;
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .takeaways {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .takeaway-item {{
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .next-steps {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin-top: 30px;
        }}
        
        .closing-statement {{
            text-align: center;
            font-size: 1.4em;
            margin-top: 40px;
            font-weight: 300;
            opacity: 0.9;
        }}
        
        .metadata {{
            background: {colors['background']};
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
        }}
        
        .metadata h3 {{
            color: {colors['primary']};
            margin-bottom: 15px;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .metadata-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        @media (max-width: 768px) {{
            .slide {{
                padding: 30px 20px;
                margin: 20px 0;
            }}
            
            .title-slide h1 {{
                font-size: 2.5em;
            }}
            
            .content-slide h2 {{
                font-size: 2em;
            }}
            
            .highlights {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .takeaways {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="metadata">
            <h3>📊 Presentation Overview</h3>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div class="metadata-item">
                    <strong>Themes:</strong> {', '.join(themes)}
                </div>
                <div class="metadata-item">
                    <strong>Total Slides:</strong> {len(enhanced_slides)}
                </div>
                <div class="metadata-item">
                    <strong>AI-Generated:</strong> Enhanced with Gemini LLM
                </div>
            </div>
        </div>
"""
    
    # Generate slides
    for i, slide in enumerate(enhanced_slides):
        slide_number = slide.get("slide_number", i + 1)
        slide_type = slide.get("type", "content")
        slide_title = slide.get("title", f"Slide {slide_number}")
        enhanced_content = slide.get("enhanced_content", {})
        
        if slide_type == "title":
            subtitle = enhanced_content.get("subtitle", "Professional Analysis")
            highlights = enhanced_content.get("highlights", [])
            
            html += f"""
        <div class="slide title-slide">
            <div class="slide-number">{slide_number}</div>
            <h1>{slide_title}</h1>
            <div class="subtitle">{subtitle}</div>
            <div class="highlights">
"""
            for highlight in highlights:
                html += f'                <div class="highlight-item">{highlight}</div>\n'
            
            html += """            </div>
        </div>
"""
        
        elif slide_type == "conclusion":
            takeaways = enhanced_content.get("takeaways", [])
            next_steps = enhanced_content.get("next_steps", [])
            closing = enhanced_content.get("closing_statement", "Thank you")
            
            html += f"""
        <div class="slide conclusion-slide">
            <div class="slide-number">{slide_number}</div>
            <h2>{slide_title}</h2>
            <div class="takeaways">
"""
            for takeaway in takeaways:
                html += f'                <div class="takeaway-item">{takeaway}</div>\n'
            
            html += """            </div>
            <div class="next-steps">
                <h3>🎯 Next Steps</h3>
                <ul class="bullet-points">
"""
            for step in next_steps:
                html += f'                    <li>{step}</li>\n'
            
            html += f"""                </ul>
            </div>
            <div class="closing-statement">{closing}</div>
        </div>
"""
        
        else:  # content slide
            bullet_points = enhanced_content.get("bullet_points", [])
            key_message = enhanced_content.get("key_message", "")
            
            html += f"""
        <div class="slide content-slide">
            <div class="slide-number">{slide_number}</div>
            <h2>{slide_title}</h2>
            <ul class="bullet-points">
"""
            for point in bullet_points:
                html += f'                <li>{point}</li>\n'
            
            html += """            </ul>
"""
            if key_message:
                html += f'            <div class="key-message">💡 <strong>Key Insight:</strong> {key_message}</div>\n'
            
            html += """        </div>
"""
    
    html += """    </div>
</body>
</html>"""
    
    return html


def create_presentation_from_text(document_text: str, presentation_title: str = "") -> str:
    """
    Create an enhanced presentation from text using Gemini LLM for actual content generation.
    
    Args:
        document_text: The input text content
        presentation_title: Optional title for the presentation
        
    Returns:
        JSON string with result information
    """
    if not SEQUENTIAL_AVAILABLE:
        return json.dumps({
            "status": "error",
            "message": "Sequential workflow system not available",
            "details": "Could not import sequential_agents module"
        })
    
    try:
        # Create output directory
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_presentations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the sequential workflow coordinator
        coordinator = SequentialWorkflowCoordinator()
        
        # Execute the workflow
        result = coordinator.execute_full_workflow(document_text=document_text)
        
        if result.get("status") == "success":
            # Save the enhanced HTML presentation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"ai_presentation_{timestamp}.html"
            html_path = os.path.join(output_dir, html_filename)
            
            # Also save to static directory for web serving
            static_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'presentations')
            os.makedirs(static_dir, exist_ok=True)
            static_path = os.path.join(static_dir, html_filename)
            
            # Generate enhanced HTML using Gemini LLM (with rate limiting)
            print("🎨 Generating enhanced presentation with AI...")
            html_content = generate_enhanced_html(
                result, 
                presentation_title or result.get("metadata", {}).get("document_title", "AI-Generated Presentation"),
                document_text
            )
            
            # Save to both locations
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            with open(static_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create download URL
            download_url = f"http://localhost:8002/presentations/{html_filename}"
            
            # Get slide information
            slides_info = result.get("slide_structure", result.get("slides", []))
            slide_titles = [slide.get("title", "Untitled") for slide in slides_info]
            
            # Check if we used fallback mode due to rate limits
            ai_mode = "AI-powered" if GEMINI_AVAILABLE and not html_generator.fallback_mode else "Template-based"
            rate_limit_msg = " (Rate limits applied)" if html_generator.fallback_mode else ""
            
            return json.dumps({
                "status": "success",
                "message": f"✅ {'AI-Enhanced' if not html_generator.fallback_mode else 'Professional'} Presentation created successfully!{rate_limit_msg}",
                "presentation_path": html_path,
                "download_url": download_url,
                "direct_link": f"Click here to view: {download_url}",
                "execution_time": f"{result.get('execution_time', 0):.2f} seconds",
                "slide_count": len(slides_info),
                "slides": slide_titles,
                "themes": result.get("metadata", {}).get("themes", []),
                "ai_features": [
                    f"✨ {ai_mode} content generation",
                    "🎨 Professional color schemes", 
                    "📝 Intelligent slide structuring",
                    "💡 Auto-generated insights",
                    "📱 Mobile-responsive design"
                ],
                "enhancement_details": {
                    "gemini_available": GEMINI_AVAILABLE,
                    "content_generation": ai_mode,
                    "rate_limiting": "Active" if not html_generator.fallback_mode else "Fallback mode",
                    "design_optimization": "Theme-based color palettes",
                    "responsive_design": "Mobile and desktop optimized"
                },
                "note": "If you see 'Template-based' content, this is due to API rate limits. Wait a moment and try again for AI-enhanced content." if html_generator.fallback_mode else "Full AI enhancement applied!"
            }, indent=2)
        else:
            return json.dumps({
                "status": "error", 
                "message": f"❌ Workflow failed: {result.get('error', 'Unknown error')}",
                "details": result
            })
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to create presentation: {str(e)}",
            "error_details": traceback.format_exc()
        })


def get_system_status() -> str:
    """
    Get the status of the enhanced presentation generation system.
    
    Returns:
        JSON string with system status
    """
    try:
        status = {
            "sequential_workflow": SEQUENTIAL_AVAILABLE,
            "gemini_llm": GEMINI_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "🤖 AI-powered content generation with Gemini LLM",
                "📊 Intelligent document analysis", 
                "🎨 Theme-based design optimization",
                "📱 Mobile-responsive HTML presentations",
                "💡 Auto-generated insights and takeaways",
                "🎯 Professional slide structuring"
            ] if SEQUENTIAL_AVAILABLE else ["System unavailable"],
            "ai_features": {
                "content_generation": GEMINI_AVAILABLE,
                "color_palette_optimization": GEMINI_AVAILABLE,
                "intelligent_structuring": SEQUENTIAL_AVAILABLE,
                "fallback_mode": True
            }
        }
        
        if SEQUENTIAL_AVAILABLE:
            # Get workflow info
            from modules.sequential_agents import get_workflow_info
            workflow_info = get_workflow_info()
            status.update(workflow_info)
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to get system status: {str(e)}"
        })


# Create the root agent using ADK's standard Agent class
root_agent = Agent(
    name="simple_ppt_agent",
    model="gemini-2.0-flash-exp",
    description="AI-Enhanced PowerPoint generation agent using Gemini LLM for intelligent content creation.",
    instruction="""You are an advanced PowerPoint generation agent powered by Gemini LLM that creates professional presentations from text content.

🤖 AI-Enhanced Features:
- Intelligent content analysis using Gemini LLM
- Auto-generated slide content with real insights
- Theme-based color palette optimization  
- Professional design with responsive layouts
- Smart bullet point generation
- Contextual key insights and takeaways

You can:
1. Analyze text content using AI to identify key themes and structure
2. Generate actual slide content (not placeholders) using Gemini LLM
3. Create professional HTML presentations with:
   - Title slide with AI-generated highlights
   - Content slides with intelligent bullet points
   - Conclusion slide with key takeaways and next steps
   - Mobile-responsive design
   - Theme-optimized color schemes

4. Provide system status and capabilities

Key improvements over basic systems:
✨ Real content generation (not templates)
🎨 AI-optimized visual design
📱 Mobile and desktop responsive
💡 Intelligent insights extraction
🎯 Professional presentation structure

Use 'create_presentation_from_text' with your document content to generate AI-enhanced presentations.
Use 'get_system_status' to check AI capabilities and system health.""",
    tools=[create_presentation_from_text, get_system_status]
) 