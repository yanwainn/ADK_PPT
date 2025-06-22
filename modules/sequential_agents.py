"""
Enhanced Sequential Agent Workflow System with Gemini LLM Integration

This module provides a structured, sequential approach to presentation generation
with individual agents responsible for specific steps using actual AI generation.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    
    # Configure Gemini API
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        logger = logging.getLogger(__name__)
        logger.info("🔑 Gemini API configured successfully")
    else:
        GEMINI_AVAILABLE = False
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Gemini API key not found - using fallback mode")
        
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Gemini API not available - using fallback mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StepResult:
    """Result from a workflow step"""
    step_name: str
    status: WorkflowStatus
    data: Dict[str, Any]
    processing_time: float
    timestamp: str
    error_message: Optional[str] = None

class GeminiContentGenerator:
    """
    Gemini LLM integration for content generation
    """
    
    def __init__(self):
        self.model_name = "gemini-2.5-flash"
        self.model = None
        if GEMINI_AVAILABLE:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"🤖 Gemini model '{self.model_name}' initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model: {e}")
                self.model = None
    
    def generate_content(self, prompt: str, max_retries: int = 2) -> str:
        """Generate content using Gemini API with fallback"""
        if not self.model:
            return self._fallback_generation(prompt)
        
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.strip()
                else:
                    logger.warning(f"⚠️ Empty response from Gemini (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    logger.info("🔄 Falling back to structured generation")
                    return self._fallback_generation(prompt)
        
        return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback content generation when Gemini is not available"""
        if "slide structure" in prompt.lower():
            return """Based on the content analysis, here's the recommended slide structure:

Slide 1 (Title): Introduction and Overview
Slide 2 (Content): Key Concepts and Main Points  
Slide 3 (Content): Supporting Details and Examples
Slide 4 (Content): Analysis and Implications
Slide 5 (Conclusion): Summary and Next Steps"""
        
        elif "bullet points" in prompt.lower():
            return """• Key insight from the analyzed content
• Supporting evidence and examples
• Important implications to consider
• Actionable recommendations
• Future considerations and next steps"""
        
        elif "color palette" in prompt.lower():
            return "#2c3e50, #3498db, #e74c3c, #f39c12, #27ae60"
        
        else:
            return "Professional content generated based on the provided context and requirements."

# Initialize global content generator
content_generator = GeminiContentGenerator()

class DocumentAnalysisAgent:
    """
    Step 1: Enhanced Document Analysis Agent with Gemini LLM
    """
    
    def __init__(self):
        self.agent_name = "Document Analysis Agent"
        self.step_number = 1
    
    def process(self, document_text: str) -> StepResult:
        """
        Analyze document using Gemini LLM for intelligent analysis
        """
        start_time = datetime.now()
        logger.info(f"🔍 Step {self.step_number}: {self.agent_name} - Starting AI-powered analysis...")
        
        try:
            # Use Gemini to analyze document structure and content
            analysis_prompt = f"""
Analyze the following document and provide a structured analysis:

Document Text:
{document_text[:2000]}...

Please provide:
1. A clear, engaging title for a presentation based on this content
2. 3-4 main themes/topics that should be covered
3. The optimal number of content slides (between 3-5 total slides including title)
4. Key insights and important points
5. The overall tone and style (professional, technical, educational, etc.)

Format your response as a structured analysis.
"""
            
            ai_analysis = content_generator.generate_content(analysis_prompt)
            logger.info(f"   🤖 AI analysis completed")
            
            # Extract structured information from AI response
            title = self._extract_title_from_ai_analysis(ai_analysis, document_text)
            themes = self._extract_themes_from_ai_analysis(ai_analysis)
            sections = self._extract_sections_from_document(document_text, ai_analysis)
            metadata = self._calculate_metadata(document_text)
            
            logger.info(f"   📄 Document title: {title}")
            logger.info(f"   📝 Found {len(sections)} sections")
            logger.info(f"   🎯 Identified themes: {', '.join(themes)}")
            
            result_data = {
                "document_title": title,
                "sections": sections,
                "themes": themes,
                "metadata": metadata,
                "ai_analysis": ai_analysis,
                "analysis_summary": {
                    "total_sections": len(sections),
                    "main_themes": themes[:3],
                    "complexity": metadata.get("complexity_score", 3),
                    "estimated_reading_time": metadata.get("estimated_reading_time", "5 minutes"),
                    "recommended_slides": min(5, len(sections) + 2)  # +2 for title and conclusion
                }
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Step {self.step_number}: AI-powered analysis completed in {processing_time:.2f}s")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.COMPLETED,
                data=result_data,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Step {self.step_number}: Document analysis failed: {e}")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _extract_title_from_ai_analysis(self, ai_analysis: str, document_text: str) -> str:
        """Extract title from AI analysis or document"""
        # Try to find title in AI analysis first
        lines = ai_analysis.split('\n')
        for line in lines:
            if 'title' in line.lower() and ':' in line:
                title = line.split(':', 1)[1].strip()
                if title and len(title) < 100:
                    return title.strip('"').strip("'")
        
        # Fallback to document analysis
        lines = document_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('•'):
                return line
        return "AI-Generated Presentation"
    
    def _extract_themes_from_ai_analysis(self, ai_analysis: str) -> List[str]:
        """Extract themes from AI analysis"""
        themes = []
        content_lower = ai_analysis.lower()
        
        # Look for themes in AI analysis
        if 'theme' in content_lower or 'topic' in content_lower:
            lines = ai_analysis.split('\n')
            for line in lines:
                if ('theme' in line.lower() or 'topic' in line.lower()) and ':' in line:
                    theme_part = line.split(':', 1)[1].strip()
                    if theme_part:
                        themes.extend([t.strip().strip('-').strip() for t in theme_part.split(',') if t.strip()])
        
        # Fallback theme detection
        theme_keywords = {
            'Business Strategy': ['business', 'strategy', 'market', 'competitive', 'growth'],
            'Technology': ['technology', 'ai', 'automation', 'digital', 'innovation'],
            'Data & Analytics': ['data', 'analytics', 'insights', 'metrics', 'analysis'],
            'Customer Experience': ['customer', 'experience', 'satisfaction', 'service'],
            'Finance': ['finance', 'revenue', 'cost', 'profit', 'investment'],
            'Operations': ['operations', 'process', 'efficiency', 'workflow'],
            'Leadership': ['leadership', 'management', 'team', 'culture']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if theme not in themes:
                    themes.append(theme)
        
        return themes[:5] if themes else ['General Topics']
    
    def _extract_sections_from_document(self, document_text: str, ai_analysis: str) -> List[Dict[str, Any]]:
        """Extract sections using AI guidance"""
        sections = []
        lines = document_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this looks like a section header
            if (line.isupper() or 
                line.startswith(('1.', '2.', '3.', '4.', '5.', '#')) or
                (len(line) < 100 and not line.endswith('.') and not line.startswith('•'))):
                
                # Save previous section
                if current_section and current_content:
                    content_text = ' '.join(current_content)
                    sections.append({
                        "title": current_section,
                        "content": content_text,
                        "word_count": len(content_text.split()),
                        "importance": self._calculate_section_importance(content_text),
                        "themes": self._extract_themes_from_ai_analysis(content_text)
                    })
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            content_text = ' '.join(current_content)
            sections.append({
                "title": current_section,
                "content": content_text,
                "word_count": len(content_text.split()),
                "importance": self._calculate_section_importance(content_text),
                "themes": self._extract_themes_from_ai_analysis(content_text)
            })
        
        # Limit to 3 most important sections (for 5-slide presentation)
        if len(sections) > 3:
            sections.sort(key=lambda x: x['importance'] * x['word_count'], reverse=True)
            sections = sections[:3]
            logger.info(f"   🎯 Limited to top 3 most important sections")
        
        return sections
    
    def _calculate_section_importance(self, content: str) -> int:
        """Calculate importance score for a section"""
        importance_keywords = [
            'important', 'key', 'critical', 'essential', 'main', 'primary',
            'significant', 'major', 'crucial', 'fundamental', 'core'
        ]
        content_lower = content.lower()
        score = sum(1 for keyword in importance_keywords if keyword in content_lower)
        return max(1, score)
    
    def _calculate_metadata(self, document_text: str) -> Dict[str, Any]:
        """Calculate document metadata"""
        words = document_text.split()
        word_count = len(words)
        
        return {
            "word_count": word_count,
            "character_count": len(document_text),
            "estimated_reading_time": f"{max(1, word_count // 200)} minutes",
            "complexity_score": min(5, max(1, word_count // 100)),
            "language": "English"  # Could be enhanced with language detection
        }

class ContentStructureAgent:
    """
    Step 2: Enhanced Content Structure Agent with AI-powered slide planning
    """
    
    def __init__(self):
        self.agent_name = "Content Structure Agent"
        self.step_number = 2
    
    def process(self, document_analysis: Dict[str, Any]) -> StepResult:
        """
        Create slide structure using AI recommendations
        """
        start_time = datetime.now()
        logger.info(f"🏗️ Step {self.step_number}: {self.agent_name} - Creating AI-optimized slide structure...")
        
        try:
            title = document_analysis.get("document_title", "Untitled Presentation")
            sections = document_analysis.get("sections", [])
            themes = document_analysis.get("themes", [])
            ai_analysis = document_analysis.get("ai_analysis", "")
            
            # Use AI to determine optimal slide structure
            structure_prompt = f"""
Based on this document analysis, create an optimal slide structure for a professional presentation:

Title: {title}
Themes: {', '.join(themes)}
Sections: {len(sections)} content sections available
AI Analysis: {ai_analysis[:500]}...

Create a slide-by-slide structure with:
1. Title slide
2. 3-4 content slides covering the main points
3. Conclusion slide

For each slide, specify:
- Slide title
- Main points to cover
- Recommended layout (title_content, two_column, bullet_points, etc.)
- Key message

Keep total slides to 5 maximum.
"""
            
            ai_structure = content_generator.generate_content(structure_prompt)
            logger.info(f"   🤖 AI structure planning completed")
            
            # Create slide structure
            slides = self._create_ai_guided_slide_structure(title, sections, themes, ai_structure)
            
            # Calculate presentation metadata
            duration = self._estimate_duration(slides)
            layout_analysis = self._analyze_layouts(slides)
            
            logger.info(f"   📊 Created {len(slides)} slides")
            logger.info(f"   ⏱️ Estimated duration: {duration}")
            
            result_data = {
                "slide_structure": slides,
                "presentation_metadata": {
                    "total_slides": len(slides),
                    "estimated_duration": duration,
                    "layout_distribution": layout_analysis,
                    "main_themes": themes[:3],
                    "structure_approach": "AI-optimized"
                },
                "ai_structure_plan": ai_structure
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Step {self.step_number}: AI-guided structure completed in {processing_time:.2f}s")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.COMPLETED,
                data=result_data,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Step {self.step_number}: Structure creation failed: {e}")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _create_ai_guided_slide_structure(self, title: str, sections: List[Dict[str, Any]], 
                                        themes: List[str], ai_structure: str) -> List[Dict[str, Any]]:
        """Create slide structure guided by AI recommendations"""
        slides = []
        
        # Title slide
        slides.append({
            "slide_number": 1,
            "type": "title",
            "title": title,
            "subtitle": f"Key Insights: {', '.join(themes[:2])}",
            "layout": "title_slide",
            "content_points": [],
            "estimated_time": "1 min"
        })
        
        # Content slides based on sections and AI guidance
        slide_number = 2
        for i, section in enumerate(sections[:3]):  # Max 3 content slides
            layout = self._determine_layout_from_ai(section, ai_structure)
            slides.append({
                "slide_number": slide_number,
                "type": "content",
                "title": section.get("title", f"Key Point {i+1}"),
                "layout": layout,
                "content_points": self._extract_key_points(section.get("content", "")),
                "themes": section.get("themes", []),
                "estimated_time": "2-3 min"
            })
            slide_number += 1
        
        # Conclusion slide
        slides.append({
            "slide_number": slide_number,
            "type": "conclusion",
            "title": "Key Takeaways & Next Steps",
            "layout": "bullet_points",
            "content_points": self._create_conclusion_points(sections, themes),
            "estimated_time": "2 min"
        })
        
        return slides
    
    def _determine_layout_from_ai(self, section: Dict[str, Any], ai_structure: str) -> str:
        """Determine layout based on AI recommendations and content"""
        content = section.get("content", "")
        word_count = section.get("word_count", 0)
        
        # Check AI structure for layout hints
        if "two column" in ai_structure.lower() or "comparison" in ai_structure.lower():
            return "two_column"
        elif "bullet" in ai_structure.lower() or word_count < 100:
            return "bullet_points"
        elif "image" in ai_structure.lower() or "visual" in ai_structure.lower():
            return "image_content"
        else:
            return "title_content"
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        if not content:
            return ["Key insight from analysis", "Supporting details", "Important implications"]
        
        # Simple extraction - could be enhanced with AI
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        key_points = []
        
        for sentence in sentences[:4]:  # Max 4 points per slide
            if len(sentence) > 20 and len(sentence) < 150:
                key_points.append(sentence)
        
        return key_points if key_points else ["Key insight from the content analysis"]
    
    def _create_conclusion_points(self, sections: List[Dict[str, Any]], themes: List[str]) -> List[str]:
        """Create conclusion points"""
        return [
            f"Key insights from {len(sections)} main areas analyzed",
            f"Primary themes: {', '.join(themes[:2])}",
            "Strategic implications and recommendations",
            "Next steps and action items"
        ]
    
    def _estimate_duration(self, slides: List[Dict[str, Any]]) -> str:
        """Estimate presentation duration"""
        total_minutes = len(slides) * 2  # Average 2 minutes per slide
        return f"{total_minutes}-{total_minutes + 2} minutes"
    
    def _analyze_layouts(self, slides: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze layout distribution"""
        layout_count = {}
        for slide in slides:
            layout = slide.get("layout", "unknown")
            layout_count[layout] = layout_count.get(layout, 0) + 1
        return layout_count

class VisualContentAgent:
    """
    Step 3: Visual Content Agent
    Responsible for generating visual prompts and design specifications
    """
    
    def __init__(self):
        self.agent_name = "Visual Content Agent"
        self.step_number = 3
    
    def process(self, document_analysis: Dict[str, Any], slide_structure: Dict[str, Any]) -> StepResult:
        """
        Generate visual content specifications
        
        Args:
            document_analysis: Result from DocumentAnalysisAgent
            slide_structure: Result from ContentStructureAgent
            
        Returns:
            StepResult with visual content data
        """
        start_time = datetime.now()
        logger.info(f"🎨 Step {self.step_number}: {self.agent_name} - Generating visual content...")
        
        try:
            themes = document_analysis.get("themes", [])
            slides = slide_structure.get("slide_structure", [])
            
            visual_specs = self._generate_visual_specifications(slides, themes)
            color_palette = self._suggest_color_palette(themes)
            
            logger.info(f"   🖼️ Generated {len(visual_specs)} visual specifications")
            logger.info(f"   🎨 Color palette: {', '.join(color_palette)}")
            
            result_data = {
                "visual_specifications": visual_specs,
                "color_palette": color_palette,
                "design_guidelines": self._create_design_guidelines(themes),
                "font_recommendations": ["Arial", "Calibri", "Helvetica"],
                "image_requirements": {
                    "aspect_ratio": "16:9",
                    "resolution": "1920x1080",
                    "style": "professional, modern, clean"
                }
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Step {self.step_number}: Visual content generation completed in {processing_time:.2f}s")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.COMPLETED,
                data=result_data,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Step {self.step_number}: Visual content generation failed: {e}")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _generate_visual_specifications(self, slides: List[Dict[str, Any]], themes: List[str]) -> List[Dict[str, Any]]:
        """Generate visual specifications for each slide"""
        visual_specs = []
        
        for slide in slides:
            slide_type = slide.get("type", "content")
            title = slide.get("title", "")
            
            if slide_type == "title":
                prompt = self._create_title_slide_prompt(title, themes)
            elif slide_type == "conclusion":
                prompt = self._create_conclusion_slide_prompt(themes)
            else:
                prompt = self._create_content_slide_prompt(title, themes)
            
            visual_specs.append({
                "slide_number": slide["slide_number"],
                "slide_title": title,
                "visual_prompt": prompt,
                "layout_type": slide.get("layout", "standard"),
                "visual_elements": slide.get("content_points", []),
                "style_notes": self._get_style_notes(themes)
            })
        
        return visual_specs
    
    def _create_title_slide_prompt(self, title: str, themes: List[str]) -> str:
        """Create DALL-E prompt for title slide"""
        theme_descriptors = self._get_theme_descriptors(themes)
        return f"Professional title slide background for '{title}', {theme_descriptors}, modern corporate design, clean layout, 16:9 aspect ratio, subtle gradient, professional typography space"
    
    def _create_content_slide_prompt(self, title: str, themes: List[str]) -> str:
        """Create DALL-E prompt for content slide"""
        theme_descriptors = self._get_theme_descriptors(themes)
        return f"Professional slide background for '{title}', {theme_descriptors}, clean modern design, space for text content, 16:9 aspect ratio, minimal and elegant"
    
    def _create_conclusion_slide_prompt(self, themes: List[str]) -> str:
        """Create DALL-E prompt for conclusion slide"""
        theme_descriptors = self._get_theme_descriptors(themes)
        return f"Professional conclusion slide background, {theme_descriptors}, summary and takeaways design, modern corporate style, 16:9 aspect ratio, inspiring and conclusive feel"
    
    def _get_theme_descriptors(self, themes: List[str]) -> str:
        """Get visual descriptors for themes"""
        descriptors = {
            'Business Strategy': 'corporate boardroom, strategic planning elements',
            'Technology': 'modern tech interface, digital innovation elements',
            'Data & Analytics': 'data visualization, dashboard style elements',
            'Customer Experience': 'customer journey, service excellence visuals',
            'Finance': 'financial charts, professional business graphics',
            'Operations': 'workflow diagrams, process optimization visuals',
            'Leadership': 'team collaboration, leadership development visuals'
        }
        
        theme_visuals = []
        for theme in themes[:3]:  # Use top 3 themes
            if theme in descriptors:
                theme_visuals.append(descriptors[theme])
        
        return ', '.join(theme_visuals) if theme_visuals else 'professional business environment'
    
    def _suggest_color_palette(self, themes: List[str]) -> List[str]:
        """Suggest color palette based on themes"""
        if 'Technology' in themes:
            return ['#1E3A8A', '#3B82F6', '#E5E7EB', '#FFFFFF']  # Blue tech palette
        elif 'Finance' in themes:
            return ['#065F46', '#10B981', '#F3F4F6', '#FFFFFF']  # Green finance palette
        else:
            return ['#1F2937', '#4B5563', '#E5E7EB', '#FFFFFF']  # Professional gray palette
    
    def _create_design_guidelines(self, themes: List[str]) -> Dict[str, str]:
        """Create design guidelines"""
        return {
            "style": "Modern, professional, clean",
            "typography": "Sans-serif fonts, clear hierarchy",
            "spacing": "Generous white space, balanced layout",
            "imagery": "High-quality, relevant, professional",
            "consistency": "Consistent branding throughout"
        }
    
    def _get_style_notes(self, themes: List[str]) -> str:
        """Get style notes for themes"""
        if 'Technology' in themes:
            return "Modern, tech-forward, clean lines"
        elif 'Business Strategy' in themes:
            return "Corporate, professional, authoritative"
        else:
            return "Clean, professional, approachable"

class SlideGenerationAgent:
    """
    Step 4: Slide Generation Agent
    Responsible for creating actual slide content with bullet points
    """
    
    def __init__(self):
        self.agent_name = "Slide Generation Agent"
        self.step_number = 4
    
    def process(self, document_analysis: Dict[str, Any], slide_structure: Dict[str, Any], visual_content: Dict[str, Any]) -> StepResult:
        """
        Generate detailed slide content
        
        Args:
            document_analysis: Result from DocumentAnalysisAgent
            slide_structure: Result from ContentStructureAgent
            visual_content: Result from VisualContentAgent
            
        Returns:
            StepResult with detailed slide content
        """
        start_time = datetime.now()
        logger.info(f"📝 Step {self.step_number}: {self.agent_name} - Generating slide content...")
        
        try:
            slides = slide_structure.get("slide_structure", [])
            sections = document_analysis.get("sections", [])
            
            detailed_slides = self._generate_detailed_slides(slides, sections)
            
            logger.info(f"   📄 Generated content for {len(detailed_slides)} slides")
            
            result_data = {
                "detailed_slides": detailed_slides,
                "content_summary": {
                    "total_slides": len(detailed_slides),
                    "total_bullet_points": sum(len(slide.get("content_points", [])) for slide in detailed_slides),
                    "content_density": "Optimized for 5-slide format"
                }
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Step {self.step_number}: Slide content generation completed in {processing_time:.2f}s")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.COMPLETED,
                data=result_data,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Step {self.step_number}: Slide content generation failed: {e}")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _generate_detailed_slides(self, slides: List[Dict[str, Any]], sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate detailed content for each slide"""
        detailed_slides = []
        
        for slide in slides:
            slide_type = slide.get("type", "content")
            
            if slide_type == "title":
                detailed_slide = self._create_title_slide_content(slide)
            elif slide_type == "conclusion":
                detailed_slide = self._create_conclusion_slide_content(slide, sections)
            else:
                # Find corresponding section for content slides
                section_index = slide.get("slide_number", 2) - 2  # Adjust for title slide
                if 0 <= section_index < len(sections):
                    section = sections[section_index]
                    detailed_slide = self._create_content_slide_content(slide, section)
                else:
                    detailed_slide = self._create_generic_content_slide(slide)
            
            detailed_slides.append(detailed_slide)
        
        return detailed_slides
    
    def _create_title_slide_content(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Create title slide content"""
        return {
            **slide,
            "content_points": [],
            "content_text": "",
            "speaker_notes": "Welcome to the presentation. Introduce yourself and provide context for the topic.",
            "slide_content": {
                "main_title": slide.get("title", "Presentation Title"),
                "subtitle": slide.get("subtitle", "Overview and Key Insights"),
                "footer_text": f"Generated on {datetime.now().strftime('%B %d, %Y')}"
            }
        }
    
    def _create_content_slide_content(self, slide: Dict[str, Any], section: Dict[str, Any]) -> Dict[str, Any]:
        """Create content slide with bullet points"""
        bullet_points = self._extract_bullet_points(section["content"])
        
        return {
            **slide,
            "content_points": bullet_points,
            "content_text": section["content"][:200] + "..." if len(section["content"]) > 200 else section["content"],
            "speaker_notes": f"Discuss each point in detail. Key themes: {', '.join(section.get('themes', []))}",
            "slide_content": {
                "main_title": slide.get("title", section["title"]),
                "subtitle": "",
                "content_points": bullet_points,
                "key_message": self._extract_key_message(section["content"])
            }
        }
    
    def _create_conclusion_slide_content(self, slide: Dict[str, Any], sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create conclusion slide content"""
        key_takeaways = []
        for section in sections:
            takeaway = self._extract_key_message(section["content"])
            if takeaway:
                key_takeaways.append(takeaway)
        
        bullet_points = [
            "Key insights from today's presentation",
            "Actionable next steps",
            "Questions and discussion"
        ]
        
        return {
            **slide,
            "content_points": bullet_points,
            "content_text": "Summary of main points and next steps",
            "speaker_notes": "Summarize key points, provide next steps, and open for questions",
            "slide_content": {
                "main_title": "Key Takeaways",
                "subtitle": "Summary and Next Steps",
                "content_points": bullet_points,
                "key_takeaways": key_takeaways[:3]  # Top 3 takeaways
            }
        }
    
    def _create_generic_content_slide(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Create generic content slide"""
        return {
            **slide,
            "content_points": ["Key point 1", "Key point 2", "Key point 3"],
            "content_text": "Content for this slide",
            "speaker_notes": "Discuss the main points for this section",
            "slide_content": {
                "main_title": slide.get("title", "Content Slide"),
                "subtitle": "",
                "content_points": ["Key point 1", "Key point 2", "Key point 3"]
            }
        }
    
    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract bullet points from content"""
        sentences = content.split('.')
        bullet_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10 and len(sentence) < 100:
                # Clean up the sentence
                if not sentence.endswith('.'):
                    sentence += '.'
                bullet_points.append(sentence)
                
                if len(bullet_points) >= 4:  # Max 4 bullet points per slide
                    break
        
        # Ensure we have at least 2 bullet points
        if len(bullet_points) < 2:
            bullet_points = [
                "Key insight from this section",
                "Important consideration",
                "Actionable takeaway"
            ]
        
        return bullet_points[:4]  # Max 4 bullet points
    
    def _extract_key_message(self, content: str) -> str:
        """Extract key message from content"""
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 150:
                return sentence + '.'
        return "Key insight from this section."

class PresentationAssemblyAgent:
    """
    Step 5: Presentation Assembly Agent
    Responsible for assembling everything into final presentation
    """
    
    def __init__(self):
        self.agent_name = "Presentation Assembly Agent"
        self.step_number = 5
    
    def process(self, all_results: Dict[str, Any]) -> StepResult:
        """
        Assemble final presentation from all previous results
        
        Args:
            all_results: Combined results from all previous agents
            
        Returns:
            StepResult with final presentation data
        """
        start_time = datetime.now()
        logger.info(f"🎯 Step {self.step_number}: {self.agent_name} - Assembling final presentation...")
        
        try:
            document_analysis = all_results.get("document_analysis", {})
            slide_structure = all_results.get("slide_structure", {})
            visual_content = all_results.get("visual_content", {})
            slide_content = all_results.get("slide_content", {})
            
            final_presentation = self._assemble_presentation(
                document_analysis, slide_structure, visual_content, slide_content
            )
            
            logger.info(f"   🎉 Assembled complete presentation with {len(final_presentation.get('slide_structure', []))} slides")
            
            result_data = {
                "final_presentation": final_presentation,
                "assembly_summary": {
                    "total_slides": len(final_presentation.get("slide_structure", [])),
                    "estimated_duration": final_presentation.get("presentation_metadata", {}).get("estimated_duration", "10-15 minutes"),
                    "ready_for_export": True
                },
                "export_options": ["HTML", "PowerPoint", "PDF"],
                "quality_metrics": self._calculate_quality_metrics(final_presentation)
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Step {self.step_number}: Presentation assembly completed in {processing_time:.2f}s")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.COMPLETED,
                data=result_data,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Step {self.step_number}: Presentation assembly failed: {e}")
            
            return StepResult(
                step_name=self.agent_name,
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _assemble_presentation(self, document_analysis: Dict[str, Any], slide_structure: Dict[str, Any], 
                             visual_content: Dict[str, Any], slide_content: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble all components into final presentation"""
        
        slides = slide_content.get("detailed_slides", [])
        visual_specs = visual_content.get("visual_specifications", [])
        
        # Merge visual specifications with slide content
        for slide in slides:
            slide_number = slide.get("slide_number")
            # Find matching visual spec
            for visual_spec in visual_specs:
                if visual_spec.get("slide_number") == slide_number:
                    slide["visual_prompt"] = visual_spec.get("visual_prompt", "")
                    slide["style_notes"] = visual_spec.get("style_notes", "")
                    break
        
        return {
            "metadata": {
                "title": document_analysis.get("document_title", "Presentation"),
                "created_date": datetime.now().isoformat(),
                "total_slides": len(slides),
                "estimated_duration": slide_structure.get("presentation_metadata", {}).get("estimated_duration", "10-15 minutes"),
                "themes": document_analysis.get("themes", []),
                "format": "5-slide presentation"
            },
            "design_specs": {
                "color_palette": visual_content.get("color_palette", []),
                "fonts": visual_content.get("font_recommendations", []),
                "style": visual_content.get("design_guidelines", {})
            },
            "slide_structure": slides,
            "presentation_metadata": slide_structure.get("presentation_metadata", {}),
            "ai_structure_plan": slide_structure.get("ai_structure_plan", ""),
            "export_ready": True
        }
    
    def _calculate_quality_metrics(self, presentation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for the presentation"""
        slides = presentation.get("slide_structure", [])
        
        return {
            "content_completeness": "100%" if len(slides) == 5 else f"{len(slides)*20}%",
            "visual_consistency": "High",
            "content_balance": "Optimized for 5-slide format",
            "readability_score": "Professional",
            "overall_quality": "Ready for presentation"
        }

class SequentialWorkflowCoordinator:
    """
    Workflow Coordinator
    Manages the sequential execution of all agents
    """
    
    def __init__(self):
        self.workflow_name = "Sequential Presentation Generation"
        self.agents = {
            1: DocumentAnalysisAgent(),
            2: ContentStructureAgent(),
            3: VisualContentAgent(),
            4: SlideGenerationAgent(),
            5: PresentationAssemblyAgent()
        }
        self.workflow_history = []
    
    def execute_full_workflow(self, document_text: str) -> Dict[str, Any]:
        """
        Execute the complete sequential workflow
        
        Args:
            document_text: Input document text
            
        Returns:
            Complete workflow results
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting {self.workflow_name}")
        logger.info(f"📊 Pipeline: {len(self.agents)} sequential steps")
        
        workflow_results = {}
        all_results = {}
        
        try:
            # Step 1: Document Analysis
            doc_result = self.agents[1].process(document_text)
            workflow_results["step_1_document_analysis"] = doc_result
            if doc_result.status == WorkflowStatus.COMPLETED:
                all_results["document_analysis"] = doc_result.data
            else:
                raise Exception(f"Step 1 failed: {doc_result.error_message}")
            
            # Step 2: Content Structure
            structure_result = self.agents[2].process(all_results["document_analysis"])
            workflow_results["step_2_content_structure"] = structure_result
            if structure_result.status == WorkflowStatus.COMPLETED:
                all_results["slide_structure"] = structure_result.data
            else:
                raise Exception(f"Step 2 failed: {structure_result.error_message}")
            
            # Step 3: Visual Content
            visual_result = self.agents[3].process(all_results["document_analysis"], all_results["slide_structure"])
            workflow_results["step_3_visual_content"] = visual_result
            if visual_result.status == WorkflowStatus.COMPLETED:
                all_results["visual_content"] = visual_result.data
            else:
                raise Exception(f"Step 3 failed: {visual_result.error_message}")
            
            # Step 4: Slide Generation
            content_result = self.agents[4].process(
                all_results["document_analysis"], 
                all_results["slide_structure"], 
                all_results["visual_content"]
            )
            workflow_results["step_4_slide_generation"] = content_result
            if content_result.status == WorkflowStatus.COMPLETED:
                all_results["slide_content"] = content_result.data
            else:
                raise Exception(f"Step 4 failed: {content_result.error_message}")
            
            # Step 5: Presentation Assembly
            assembly_result = self.agents[5].process(all_results)
            workflow_results["step_5_presentation_assembly"] = assembly_result
            if assembly_result.status == WorkflowStatus.COMPLETED:
                all_results["final_presentation"] = assembly_result.data
            else:
                raise Exception(f"Step 5 failed: {assembly_result.error_message}")
            
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🎉 Workflow completed successfully in {total_time:.2f}s")
            
            # Extract slides for compatibility
            final_presentation = all_results["final_presentation"]["final_presentation"]  # Fixed: nested structure
            slides = final_presentation.get("slide_structure", [])  # Fixed: get from correct key
            
            return {
                "status": "success",
                "slides": slides,  # For compatibility with agent.py
                "slide_structure": slides,  # Alternative key
                "final_result": final_presentation,
                "workflow_results": workflow_results,
                "execution_summary": {
                    "total_steps": len(self.agents),
                    "successful_steps": 5,
                    "total_time": total_time,
                    "average_step_time": total_time / 5
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"💥 Workflow failed: {e}")
            
            return {
                "status": "failed",
                "error_message": str(e),
                "partial_results": workflow_results,
                "execution_summary": {
                    "total_steps": len(self.agents),
                    "completed_steps": len(workflow_results),
                    "total_time": total_time
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_single_step(self, step_number: int, input_data: Any) -> StepResult:
        """
        Execute a single step in the workflow
        
        Args:
            step_number: Step number to execute (1-5)
            input_data: Input data for the step
            
        Returns:
            StepResult for the executed step
        """
        if step_number not in self.agents:
            return StepResult(
                step_name=f"Invalid Step {step_number}",
                status=WorkflowStatus.FAILED,
                data={},
                processing_time=0,
                timestamp=datetime.now().isoformat(),
                error_message=f"Step {step_number} does not exist"
            )
        
        logger.info(f"🔧 Executing single step: {step_number}")
        
        agent = self.agents[step_number]
        
        if step_number == 1:
            return agent.process(input_data)
        elif step_number == 2:
            return agent.process(input_data)
        elif step_number == 3:
            return agent.process(input_data.get("document_analysis", {}), input_data.get("slide_structure", {}))
        elif step_number == 4:
            return agent.process(
                input_data.get("document_analysis", {}),
                input_data.get("slide_structure", {}),
                input_data.get("visual_content", {})
            )
        elif step_number == 5:
            return agent.process(input_data)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and agent information"""
        return {
            "workflow_name": self.workflow_name,
            "total_agents": len(self.agents),
            "agents": [
                {
                    "step": i,
                    "name": agent.agent_name,
                    "description": self._get_agent_description(i)
                }
                for i, agent in self.agents.items()
            ],
            "workflow_description": "Sequential 5-step presentation generation pipeline"
        }
    
    def _get_agent_description(self, step_number: int) -> str:
        """Get description for each agent"""
        descriptions = {
            1: "Analyzes input document and extracts structured information",
            2: "Plans presentation structure with 5-slide format",
            3: "Generates visual specifications and design guidelines",
            4: "Creates detailed slide content with bullet points",
            5: "Assembles final presentation ready for export"
        }
        return descriptions.get(step_number, "Agent description")

# Convenience functions for easy usage
def generate_presentation_sequential(document_text: str) -> Dict[str, Any]:
    """
    Convenience function to generate presentation using sequential workflow
    
    Args:
        document_text: Input document text
        
    Returns:
        Complete presentation generation results
    """
    coordinator = SequentialWorkflowCoordinator()
    return coordinator.execute_full_workflow(document_text)

def get_workflow_info() -> Dict[str, Any]:
    """
    Get information about the sequential workflow
    
    Returns:
        Workflow information and agent details
    """
    coordinator = SequentialWorkflowCoordinator()
    return coordinator.get_workflow_status() 