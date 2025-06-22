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
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment variables")
    
    GEMINI_AVAILABLE = True
    
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print(f"🔑 Gemini API configured for HTML generation (key: {api_key[:10]}...)")
    else:
        GEMINI_AVAILABLE = False
        print("⚠️ Gemini API key not found in environment variables")
        
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API not available")


class RateLimitManager:
    """Manages API rate limiting to avoid quota exceeded errors"""
    
    def __init__(self, max_requests_per_minute=30):  # Increased to 30 for better throughput (still under 60/min limit)
        self.max_requests = max_requests_per_minute
        self.request_times = deque()
        self.last_request_time = 0
        self.min_interval = 60.0 / max_requests_per_minute  # Minimum seconds between requests
        self.debug = True  # Enable debugging
    
    def can_make_request(self) -> bool:
        """Check if we can make a request without hitting rate limits"""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # Check if we're under the rate limit
        if len(self.request_times) >= self.max_requests:
            if self.debug:
                print(f"🚫 Rate limit: {len(self.request_times)}/{self.max_requests} requests in last minute")
            return False
        
        # Check minimum interval between requests  
        if now - self.last_request_time < self.min_interval:
            if self.debug:
                print(f"⏱️ Rate limit: {now - self.last_request_time:.1f}s < {self.min_interval:.1f}s minimum interval")
            return False
        
        return True
    
    def record_request(self):
        """Record that a request was made"""
        now = time.time()
        self.request_times.append(now)
        self.last_request_time = now
        if self.debug:
            print(f"📝 Recorded request. Total in last minute: {len(self.request_times)}")
    
    def wait_if_needed(self):
        """Wait if necessary to avoid rate limits"""
        if not self.can_make_request():
            wait_time = self.min_interval - (time.time() - self.last_request_time)
            if wait_time > 0:
                print(f"⏱️ Rate limit protection: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)


class GeminiHTMLGenerator:
    """
    Gemini-powered HTML presentation generator with improved error handling and debugging
    """
    
    def __init__(self):
        self.model_name = "gemini-2.0-flash-exp"
        self.model = None
        self.rate_limiter = RateLimitManager()
        self.fallback_mode = False
        self.debug = True
        self.successful_requests = 0
        self.failed_requests = 0
        
        if GEMINI_AVAILABLE:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                print(f"🤖 Gemini HTML generator initialized with improved rate limiting")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
                self.fallback_mode = True
    
    def generate_slide_content(self, slide_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate actual content for a slide using Gemini with improved error handling"""
        slide_title = slide_data.get("title", "")
        slide_type = slide_data.get("type", "content")
        
        if self.debug:
            print(f"🎯 Generating content for {slide_type} slide: '{slide_title}'")
        
        if not self.model or self.fallback_mode:
            print(f"📝 Using fallback content for slide: {slide_title}")
            return self._fallback_slide_content(slide_data)
        
        # Check rate limits
        if not self.rate_limiter.can_make_request():
            print(f"⚠️ Rate limit reached for slide '{slide_title}', using fallback content")
            self.failed_requests += 1
            return self._fallback_slide_content(slide_data)
        
        try:
            # Wait if needed to respect rate limits
            self.rate_limiter.wait_if_needed()
            
            if slide_type == "title":
                prompt = f"""
Create engaging content for a title slide of a professional presentation.

Title: {slide_title}
Context: {context[:500]}...

Generate compelling content with:
1. A professional subtitle (max 15 words) that captures the essence
2. 3 key highlights or value propositions as bullet points
3. Content should be specific to the provided context, not generic

Return ONLY a JSON object with this exact structure:
{{
  "subtitle": "your subtitle here",
  "highlights": ["highlight 1", "highlight 2", "highlight 3"]
}}
"""
            
            elif slide_type == "conclusion":
                prompt = f"""
Create compelling conclusion content for a presentation.

Title: {slide_title}
Context: {context[:500]}...

Generate specific conclusion content with:
1. 4-5 key takeaways from the actual content (not generic)
2. 2-3 actionable next steps based on the context
3. A memorable closing statement related to the topic

Return ONLY a JSON object with this exact structure:
{{
  "takeaways": ["takeaway 1", "takeaway 2", "takeaway 3", "takeaway 4"],
  "next_steps": ["step 1", "step 2"],
  "closing_statement": "your closing statement"
}}
"""
            
            else:  # content slide
                prompt = f"""
Create professional, Canva-style content for a presentation slide with concise, impactful bullet points.

Slide Title: {slide_title}
Context: {context[:800]}...

Generate modern, professional content following these guidelines:

📋 BULLET POINT STYLE (Canva-inspired):
• Keep each bullet point 3-7 words maximum
• Use action-oriented, powerful language
• Start with strong verbs or key concepts
• Make each point visually scannable
• Focus on benefits and outcomes
• Use parallel structure across points

💡 CONTENT REQUIREMENTS:
1. 4-5 concise, punchy bullet points
2. Each point should be self-contained and clear
3. Use modern business language
4. Emphasize value propositions
5. Make content memorable and quotable

🎯 KEY MESSAGE:
• One compelling insight (8-12 words)
• Should capture the core value
• Use confident, authoritative tone

Return ONLY a JSON object with this exact structure:
{{
  "bullet_points": ["• Powerful action phrase", "• Clear benefit statement", "• Compelling outcome", "• Strategic advantage"],
  "key_message": "Core insight that drives results"
}}
"""
            
            if self.debug:
                print(f"🤖 Making Gemini API call for slide: {slide_title}")
            
            # Record the request and make the API call
            self.rate_limiter.record_request()
            response = self.model.generate_content(prompt)
            
            if self.debug:
                print(f"✅ Received Gemini response for slide: {slide_title}")
                print(f"📄 Response length: {len(response.text)} characters")
            
            # Clean the response text and try to parse JSON
            response_text = response.text.strip()
            
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
                content_data = json.loads(response_text)
                if self.debug:
                    print(f"✅ Successfully parsed JSON for slide: {slide_title}")
                    print(f"📊 Generated keys: {list(content_data.keys())}")
                
                self.successful_requests += 1
                return content_data
                
            except json.JSONDecodeError as e:
                if self.debug:
                    print(f"❌ JSON parsing failed for slide '{slide_title}': {e}")
                    print(f"📄 Raw response: {response_text[:200]}...")
                
                # Try to extract content manually
                parsed_content = self._parse_text_response(response.text, slide_type)
                if parsed_content and any(parsed_content.values()):
                    if self.debug:
                        print(f"✅ Manual parsing succeeded for slide: {slide_title}")
                    self.successful_requests += 1
                    return parsed_content
                else:
                    if self.debug:
                        print(f"❌ Manual parsing failed for slide: {slide_title}")
                    self.failed_requests += 1
                    return self._fallback_slide_content(slide_data)
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⚠️ Rate limit exceeded for slide '{slide_title}': {e}")
                self.fallback_mode = True
            else:
                print(f"❌ Gemini API error for slide '{slide_title}': {e}")
            
            self.failed_requests += 1
            return self._fallback_slide_content(slide_data)

    def _parse_text_response(self, text: str, slide_type: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        try:
            # Try to find JSON-like content in the text
            import re
            
            if slide_type == "title":
                subtitle_match = re.search(r'"subtitle":\s*"([^"]+)"', text)
                highlights_match = re.findall(r'"([^"]+)"', text)
                
                if subtitle_match:
                    subtitle = subtitle_match.group(1)
                    # Filter out the subtitle from highlights
                    highlights = [h for h in highlights_match if h != subtitle and len(h) > 10][:3]
                    return {"subtitle": subtitle, "highlights": highlights}
            
            elif slide_type == "conclusion":
                takeaways = re.findall(r'["\']([^"\']{20,})["\']', text)
                if takeaways:
                    return {
                        "takeaways": takeaways[:4],
                        "next_steps": takeaways[4:6] if len(takeaways) > 4 else ["Review findings", "Take action"],
                        "closing_statement": takeaways[-1] if takeaways else "Thank you"
                    }
            
            else:  # content slide
                points = re.findall(r'["\']([^"\']{10,})["\']', text)
                if points:
                    # Ensure bullet points start with bullet symbol
                    formatted_points = []
                    for point in points[:5]:
                        if not point.startswith('•'):
                            formatted_points.append(f"• {point}")
                        else:
                            formatted_points.append(point)
                    return {
                        "bullet_points": formatted_points,
                        "key_message": points[-1] if len(points) > 1 else "Transform insights into strategic advantage"
                    }
        
        except Exception as e:
            print(f"❌ Text parsing error: {e}")
        
        return {}

    def _fallback_slide_content(self, slide_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback content when Gemini is not available - now with slide-specific content"""
        slide_type = slide_data.get("type", "content")
        slide_title = slide_data.get("title", "")
        
        if self.debug:
            print(f"📝 Using fallback content for {slide_type} slide: {slide_title}")
        
        if slide_type == "title":
            return {
                "subtitle": f"Professional Analysis: {slide_title}",
                "highlights": [
                    f"Comprehensive overview of {slide_title.lower()}",
                    "Data-driven insights and analysis", 
                    "Strategic recommendations and next steps"
                ]
            }
        elif slide_type == "conclusion":
            return {
                "takeaways": [
                    f"Key insights from {slide_title.lower()} analysis",
                    "Strategic implications identified and analyzed",
                    "Clear recommendations provided",
                    "Actionable next steps outlined"
                ],
                "next_steps": [
                    "Review and validate findings",
                    "Develop detailed action plan",
                    "Implement recommended strategies"
                ],
                "closing_statement": "Thank you for your attention. Questions welcome."
            }
        else:
            return {
                "bullet_points": [
                    f"• {slide_title.replace(' ', ' ').title()} Analysis",
                    "• Data-Driven Insights",
                    "• Strategic Recommendations", 
                    "• Actionable Next Steps",
                    "• Measurable Outcomes"
                ],
                "key_message": f"Transform insights into strategic advantage",
                "supporting_details": "Professional analysis with clear action items"
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
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about content generation success/failure rates"""
        total_requests = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate:.1f}%",
            "fallback_mode": self.fallback_mode,
            "gemini_available": GEMINI_AVAILABLE and self.model is not None
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
    
    # Generate actual slide content using Gemini with proper spacing
    enhanced_slides = []
    for i, slide in enumerate(slides):
        if i > 0:  # Add delay between slides to respect rate limits
            print(f"⏱️ Waiting 5 seconds before generating slide {i+1}...")
            import time
            time.sleep(5)
        
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
            
            # Get generation statistics
            gen_stats = html_generator.get_generation_stats()
            
            # Determine the actual content generation mode
            if gen_stats["successful_requests"] > 0:
                ai_mode = "AI-powered"
                success_msg = f"✅ AI-Enhanced Presentation created successfully!"
                note = f"🤖 Generated {gen_stats['successful_requests']}/{gen_stats['total_requests']} slides with AI content ({gen_stats['success_rate']} success rate)"
            else:
                ai_mode = "Template-based"
                success_msg = f"✅ Professional Presentation created (Fallback Mode)"
                note = f"⚠️ Used template content due to API issues. Try again for AI-enhanced content."
            
            return json.dumps({
                "status": "success",
                "message": success_msg,
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
                    "generation_stats": gen_stats,
                    "design_optimization": "Theme-based color palettes",
                    "responsive_design": "Mobile and desktop optimized"
                },
                "note": note
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


def test_gemini_integration() -> str:
    """
    Test Gemini integration directly to diagnose issues.
    
    Returns:
        JSON string with test results
    """
    try:
        print("🧪 Testing Gemini integration...")
        
        # Test basic Gemini call
        test_slide = {
            "title": "Test Slide",
            "type": "content"
        }
        test_context = "This is a test document about artificial intelligence and machine learning applications."
        
        # Reset stats for clean test
        html_generator.successful_requests = 0
        html_generator.failed_requests = 0
        html_generator.fallback_mode = False
        
        # Generate test content
        result = html_generator.generate_slide_content(test_slide, test_context)
        stats = html_generator.get_generation_stats()
        
        return json.dumps({
            "status": "success",
            "test_result": result,
            "generation_stats": stats,
            "gemini_available": GEMINI_AVAILABLE,
            "api_key_configured": bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')),
            "model_initialized": html_generator.model is not None,
            "fallback_mode": html_generator.fallback_mode,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Gemini test failed: {str(e)}",
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
Use 'get_system_status' to check AI capabilities and system health.
Use 'test_gemini_integration' to diagnose and test Gemini API connectivity.""",
    tools=[create_presentation_from_text, get_system_status, test_gemini_integration]
) 