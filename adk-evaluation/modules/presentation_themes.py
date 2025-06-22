"""
Professional Presentation Themes Configuration

This module defines theme configurations for different presentation contexts,
ensuring consistent, professional design across all presentations.
"""

from typing import Dict, Any


class PresentationThemes:
    """Manages professional presentation themes and color schemes"""
    
    # Professional color schemes with semantic meaning
    THEMES = {
        "financial": {
            "name": "Financial Authority",
            "description": "Trust and stability for financial presentations",
            "colors": {
                "primary": "#1a365d",      # Deep Navy
                "secondary": "#2d3748",     # Charcoal
                "accent": "#3182ce",        # Trust Blue
                "success": "#48bb78",       # Growth Green
                "warning": "#f6e05e",       # Gold
                "bg": "#f8fafc"            # Light Gray
            },
            "fonts": {
                "primary": "'Inter', -apple-system, sans-serif",
                "display": "'Playfair Display', Georgia, serif"
            },
            "suitable_for": ["financial", "banking", "investment", "quarterly", "earnings"]
        },
        
        "technology": {
            "name": "Tech Innovation",
            "description": "Modern and innovative for tech presentations",
            "colors": {
                "primary": "#0066cc",       # Tech Blue
                "secondary": "#2d3748",     # Dark Gray
                "accent": "#7c4dff",        # Purple
                "success": "#00e676",       # Green
                "warning": "#ff9800",       # Orange
                "bg": "#fafafa"            # Off White
            },
            "fonts": {
                "primary": "'Inter', -apple-system, sans-serif",
                "display": "'Inter', -apple-system, sans-serif"
            },
            "suitable_for": ["technology", "software", "innovation", "digital", "ai", "data"]
        },
        
        "sales": {
            "name": "Sales Energy",
            "description": "Energetic and persuasive for sales presentations",
            "colors": {
                "primary": "#c05621",       # Energetic Orange
                "secondary": "#1a365d",     # Trust Blue
                "accent": "#ed8936",        # Bright Orange
                "success": "#48bb78",       # Success Green
                "warning": "#f6ad55",       # Warning Orange
                "bg": "#fffaf0"            # Warm White
            },
            "fonts": {
                "primary": "'Inter', -apple-system, sans-serif",
                "display": "'Playfair Display', Georgia, serif"
            },
            "suitable_for": ["sales", "marketing", "growth", "customer", "revenue"]
        },
        
        "strategy": {
            "name": "Strategic Vision",
            "description": "Executive-level strategy presentations",
            "colors": {
                "primary": "#2d3748",       # Executive Gray
                "secondary": "#1a365d",     # Deep Blue
                "accent": "#805ad5",        # Strategic Purple
                "success": "#48bb78",       # Achievement Green
                "warning": "#e53e3e",       # Risk Red
                "bg": "#f7fafc"            # Professional White
            },
            "fonts": {
                "primary": "'Inter', -apple-system, sans-serif",
                "display": "'Playfair Display', Georgia, serif"
            },
            "suitable_for": ["strategy", "executive", "board", "vision", "transformation"]
        },
        
        "healthcare": {
            "name": "Healthcare Trust",
            "description": "Clean and trustworthy for healthcare",
            "colors": {
                "primary": "#0f4c3a",       # Medical Green
                "secondary": "#2d3748",     # Professional Gray
                "accent": "#48bb78",        # Health Green
                "success": "#68d391",       # Positive Green
                "warning": "#3182ce",       # Info Blue
                "bg": "#f0fdf4"            # Soft Green
            },
            "fonts": {
                "primary": "'Inter', -apple-system, sans-serif",
                "display": "'Inter', -apple-system, sans-serif"
            },
            "suitable_for": ["healthcare", "medical", "wellness", "pharmaceutical", "health"]
        }
    }
    
    @classmethod
    def get_theme_by_content(cls, content: str, theme_hint: str = None) -> Dict[str, Any]:
        """
        Intelligently select a theme based on content analysis
        
        Args:
            content: The presentation content
            theme_hint: Optional theme suggestion
            
        Returns:
            Theme configuration dictionary
        """
        content_lower = content.lower()
        
        # If theme hint provided, try to match it
        if theme_hint:
            theme_hint_lower = theme_hint.lower()
            for theme_key, theme_data in cls.THEMES.items():
                if theme_hint_lower in theme_data["suitable_for"]:
                    return cls._prepare_theme(theme_key, theme_data)
        
        # Score each theme based on keyword matches
        theme_scores = {}
        for theme_key, theme_data in cls.THEMES.items():
            score = 0
            for keyword in theme_data["suitable_for"]:
                if keyword in content_lower:
                    score += content_lower.count(keyword)
            theme_scores[theme_key] = score
        
        # Select theme with highest score, default to strategy if no matches
        best_theme = max(theme_scores, key=theme_scores.get)
        if theme_scores[best_theme] == 0:
            best_theme = "strategy"  # Default professional theme
            
        return cls._prepare_theme(best_theme, cls.THEMES[best_theme])
    
    @classmethod
    def _prepare_theme(cls, theme_key: str, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare theme data for use"""
        return {
            "key": theme_key,
            "name": theme_data["name"],
            "colors": theme_data["colors"],
            "fonts": theme_data["fonts"],
            "description": theme_data["description"]
        }
    
    @classmethod
    def get_theme_by_name(cls, theme_name: str) -> Dict[str, Any]:
        """Get a specific theme by name"""
        if theme_name in cls.THEMES:
            return cls._prepare_theme(theme_name, cls.THEMES[theme_name])
        return cls._prepare_theme("strategy", cls.THEMES["strategy"])  # Default
    
    @classmethod
    def get_color_scheme_for_slide_type(cls, theme: Dict[str, Any], slide_type: str) -> Dict[str, str]:
        """Get specific color scheme for different slide types"""
        base_colors = theme["colors"]
        
        if slide_type == "title":
            return {
                "background": f"linear-gradient(135deg, {base_colors['primary']} 0%, {base_colors['secondary']} 100%)",
                "text": "#ffffff",
                "accent": base_colors["accent"]
            }
        elif slide_type == "content":
            return {
                "background": f"linear-gradient(135deg, #ffffff 0%, {base_colors['bg']} 100%)",
                "text": base_colors["secondary"],
                "heading": base_colors["primary"],
                "accent": base_colors["accent"]
            }
        elif slide_type == "conclusion":
            return {
                "background": f"linear-gradient(135deg, {base_colors['secondary']} 0%, {base_colors['primary']} 100%)",
                "text": "#ffffff",
                "accent": base_colors["success"]
            }
        else:
            return {
                "background": "#ffffff",
                "text": base_colors["secondary"],
                "accent": base_colors["accent"]
            }


# Convenience function
def select_theme(content: str, theme_hint: str = None) -> Dict[str, Any]:
    """Select appropriate theme based on content"""
    return PresentationThemes.get_theme_by_content(content, theme_hint)