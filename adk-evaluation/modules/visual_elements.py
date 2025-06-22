"""
Visual Elements and Chart Generation for Professional Presentations

This module provides SVG-based charts, icons, and visual elements
for creating rich, data-driven presentations.
"""

import random
from typing import Dict, List, Any, Tuple


class VisualElementGenerator:
    """Generates professional visual elements for presentations"""
    
    @staticmethod
    def generate_bar_chart(data: List[Dict[str, Any]], width: int = 400, height: int = 300) -> str:
        """Generate an SVG bar chart"""
        if not data:
            data = [
                {"label": "Q1", "value": 65},
                {"label": "Q2", "value": 78},
                {"label": "Q3", "value": 82},
                {"label": "Q4", "value": 91}
            ]
        
        max_value = max(d['value'] for d in data)
        bar_width = width / (len(data) * 1.5)
        spacing = bar_width * 0.5
        
        svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="barGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#8B1538;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#00A9CE;stop-opacity:1" />
                </linearGradient>
            </defs>'''
        
        for i, item in enumerate(data):
            bar_height = (item['value'] / max_value) * (height - 60)
            x = i * (bar_width + spacing) + spacing
            y = height - bar_height - 40
            
            svg += f'''
            <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" 
                  fill="url(#barGradient)" rx="4" />
            <text x="{x + bar_width/2}" y="{y - 10}" text-anchor="middle" 
                  font-size="14" font-weight="600" fill="#8B1538">{item['value']}</text>
            <text x="{x + bar_width/2}" y="{height - 20}" text-anchor="middle" 
                  font-size="12" fill="#64748b">{item['label']}</text>'''
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def generate_pie_chart(data: List[Dict[str, Any]], size: int = 300) -> str:
        """Generate an SVG pie chart"""
        if not data:
            data = [
                {"label": "Product A", "value": 35, "color": "#8B1538"},
                {"label": "Product B", "value": 25, "color": "#10b981"},
                {"label": "Product C", "value": 20, "color": "#f59e0b"},
                {"label": "Product D", "value": 20, "color": "#8b5cf6"}
            ]
        
        total = sum(d['value'] for d in data)
        center = size / 2
        radius = size / 2.5
        
        svg = f'''<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'''
        
        current_angle = -90  # Start at top
        for item in data:
            percentage = item['value'] / total
            angle = percentage * 360
            end_angle = current_angle + angle
            
            large_arc = 1 if angle > 180 else 0
            
            start_x = center + radius * VisualElementGenerator._cos(current_angle)
            start_y = center + radius * VisualElementGenerator._sin(current_angle)
            end_x = center + radius * VisualElementGenerator._cos(end_angle)
            end_y = center + radius * VisualElementGenerator._sin(end_angle)
            
            svg += f'''
            <path d="M {center} {center} L {start_x} {start_y} 
                     A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z"
                  fill="{item.get('color', '#8B1538')}" stroke="white" stroke-width="2" />'''
            
            # Label
            label_angle = current_angle + angle / 2
            label_x = center + (radius * 0.7) * VisualElementGenerator._cos(label_angle)
            label_y = center + (radius * 0.7) * VisualElementGenerator._sin(label_angle)
            
            svg += f'''
            <text x="{label_x}" y="{label_y}" text-anchor="middle" 
                  font-size="14" font-weight="600" fill="white">{item['value']}%</text>'''
            
            current_angle = end_angle
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def generate_line_chart(data: List[Dict[str, Any]], width: int = 400, height: int = 300) -> str:
        """Generate an SVG line chart"""
        if not data:
            data = [
                {"x": "Jan", "y": 30},
                {"x": "Feb", "y": 45},
                {"x": "Mar", "y": 42},
                {"x": "Apr", "y": 65},
                {"x": "May", "y": 78},
                {"x": "Jun", "y": 85}
            ]
        
        max_y = max(d['y'] for d in data)
        min_y = min(d['y'] for d in data)
        padding = 40
        
        points = []
        for i, item in enumerate(data):
            x = padding + (i * (width - 2 * padding) / (len(data) - 1))
            y = padding + (1 - (item['y'] - min_y) / (max_y - min_y)) * (height - 2 * padding)
            points.append((x, y))
        
        path = f"M {points[0][0]} {points[0][1]}"
        for x, y in points[1:]:
            path += f" L {x} {y}"
        
        svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#8B1538;stop-opacity:0.8" />
                    <stop offset="100%" style="stop-color:#8B1538;stop-opacity:0.1" />
                </linearGradient>
            </defs>
            
            <!-- Grid lines -->'''
        
        # Horizontal grid lines
        for i in range(5):
            y = padding + i * (height - 2 * padding) / 4
            svg += f'''<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" 
                        stroke="#e5e7eb" stroke-width="1" />'''
        
        # Area under line
        area_path = path + f" L {points[-1][0]} {height - padding} L {points[0][0]} {height - padding} Z"
        svg += f'''<path d="{area_path}" fill="url(#lineGradient)" />'''
        
        # Line
        svg += f'''<path d="{path}" fill="none" stroke="#8B1538" stroke-width="3" />'''
        
        # Points
        for i, (x, y) in enumerate(points):
            svg += f'''
            <circle cx="{x}" cy="{y}" r="5" fill="#8B1538" stroke="white" stroke-width="2" />
            <text x="{x}" y="{height - 20}" text-anchor="middle" font-size="12" fill="#64748b">{data[i]['x']}</text>'''
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def generate_progress_bars(items: List[Dict[str, Any]], width: int = 400, height: int = 200) -> str:
        """Generate progress bars"""
        if not items:
            items = [
                {"label": "Objective 1", "progress": 85},
                {"label": "Objective 2", "progress": 70},
                {"label": "Objective 3", "progress": 92}
            ]
        
        bar_height = 30
        spacing = 20
        
        svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'''
        
        for i, item in enumerate(items):
            y = i * (bar_height + spacing) + spacing
            progress_width = (item['progress'] / 100) * (width - 120)
            
            # Background
            svg += f'''<rect x="100" y="{y}" width="{width - 120}" height="{bar_height}" 
                        fill="#f3f4f6" rx="{bar_height/2}" />'''
            
            # Progress
            svg += f'''<rect x="100" y="{y}" width="{progress_width}" height="{bar_height}" 
                        fill="#8B1538" rx="{bar_height/2}" />'''
            
            # Label
            svg += f'''<text x="90" y="{y + bar_height/2 + 5}" text-anchor="end" 
                        font-size="14" fill="#64748b">{item['label']}</text>'''
            
            # Percentage
            svg += f'''<text x="{width - 10}" y="{y + bar_height/2 + 5}" text-anchor="end" 
                        font-size="14" font-weight="600" fill="#8B1538">{item['progress']}%</text>'''
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def generate_icon_grid(icons: List[Dict[str, str]], size: int = 80) -> str:
        """Generate a grid of icons with labels"""
        if not icons:
            icons = [
                {"icon": "fa-users", "label": "Team Growth"},
                {"icon": "fa-chart-line", "label": "Revenue Up"},
                {"icon": "fa-globe", "label": "Global Reach"},
                {"icon": "fa-shield-alt", "label": "Security First"}
            ]
        
        html = '<div class="icon-grid">'
        for item in icons:
            html += f'''
            <div class="icon-item">
                <div class="icon-circle">
                    <i class="fas {item['icon']}"></i>
                </div>
                <p>{item['label']}</p>
            </div>'''
        html += '</div>'
        
        return html
    
    @staticmethod
    def generate_process_flow(steps: List[str], vertical: bool = False) -> str:
        """Generate a process flow diagram"""
        if not steps:
            steps = ["Research", "Design", "Develop", "Test", "Deploy"]
        
        direction = "column" if vertical else "row"
        html = f'<div class="process-flow {direction}">'
        
        for i, step in enumerate(steps):
            html += f'''
            <div class="process-step">
                <div class="step-number">{i + 1}</div>
                <div class="step-content">{step}</div>
            </div>'''
            
            if i < len(steps) - 1:
                html += '<div class="process-arrow"><i class="fas fa-arrow-right"></i></div>'
        
        html += '</div>'
        return html
    
    @staticmethod
    def generate_comparison_table(data: Dict[str, List[Any]]) -> str:
        """Generate a comparison table"""
        if not data:
            data = {
                "features": ["Speed", "Cost", "Quality", "Support"],
                "option1": ["Fast", "$$$", "High", "24/7"],
                "option2": ["Moderate", "$$", "Medium", "Business Hours"]
            }
        
        html = '<div class="comparison-table"><table>'
        
        # Headers
        html += '<thead><tr><th>Features</th>'
        for key in data.keys():
            if key != "features":
                html += f'<th>{key.replace("_", " ").title()}</th>'
        html += '</tr></thead>'
        
        # Rows
        html += '<tbody>'
        for i, feature in enumerate(data.get("features", [])):
            html += f'<tr><td class="feature-name">{feature}</td>'
            for key, values in data.items():
                if key != "features" and i < len(values):
                    html += f'<td>{values[i]}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        
        return html
    
    @staticmethod
    def generate_kpi_cards(kpis: List[Dict[str, Any]]) -> str:
        """Generate KPI cards"""
        if not kpis:
            kpis = [
                {"value": "$2.5M", "label": "Revenue", "change": "+23%", "trend": "up"},
                {"value": "1,234", "label": "Customers", "change": "+15%", "trend": "up"},
                {"value": "98.5%", "label": "Satisfaction", "change": "+2%", "trend": "up"},
                {"value": "45ms", "label": "Response Time", "change": "-12%", "trend": "down"}
            ]
        
        html = '<div class="kpi-grid">'
        for kpi in kpis:
            trend_icon = "fa-arrow-up" if kpi.get("trend") == "up" else "fa-arrow-down"
            trend_class = "positive" if kpi.get("trend") == "up" else "negative"
            
            html += f'''
            <div class="kpi-card">
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-change {trend_class}">
                    <i class="fas {trend_icon}"></i> {kpi['change']}
                </div>
            </div>'''
        html += '</div>'
        
        return html
    
    @staticmethod
    def _cos(degrees: float) -> float:
        """Calculate cosine from degrees"""
        import math
        return math.cos(math.radians(degrees))
    
    @staticmethod
    def _sin(degrees: float) -> float:
        """Calculate sine from degrees"""
        import math
        return math.sin(math.radians(degrees))
    
    @staticmethod
    def get_visual_for_content(content: str, slide_type: str = "content") -> Dict[str, Any]:
        """Determine appropriate visual based on content analysis"""
        content_lower = content.lower()
        
        # Financial/Revenue
        if any(word in content_lower for word in ["revenue", "sales", "profit", "financial", "cost"]):
            return {
                "type": "chart",
                "subtype": "bar",
                "data": [
                    {"label": "Q1", "value": 65},
                    {"label": "Q2", "value": 78},
                    {"label": "Q3", "value": 85},
                    {"label": "Q4", "value": 92}
                ]
            }
        
        # Growth/Trend
        elif any(word in content_lower for word in ["growth", "trend", "increase", "progress"]):
            return {
                "type": "chart",
                "subtype": "line",
                "data": [
                    {"x": "Jan", "y": 30},
                    {"x": "Feb", "y": 45},
                    {"x": "Mar", "y": 55},
                    {"x": "Apr", "y": 65},
                    {"x": "May", "y": 78},
                    {"x": "Jun", "y": 88}
                ]
            }
        
        # Market Share/Distribution
        elif any(word in content_lower for word in ["market share", "distribution", "percentage", "portion"]):
            return {
                "type": "chart",
                "subtype": "pie",
                "data": [
                    {"label": "Segment A", "value": 35, "color": "#8B1538"},
                    {"label": "Segment B", "value": 25, "color": "#10b981"},
                    {"label": "Segment C", "value": 25, "color": "#f59e0b"},
                    {"label": "Other", "value": 15, "color": "#8b5cf6"}
                ]
            }
        
        # Process/Steps
        elif any(word in content_lower for word in ["process", "step", "phase", "workflow"]):
            return {
                "type": "process",
                "data": ["Analyze", "Design", "Implement", "Monitor", "Optimize"]
            }
        
        # Comparison
        elif any(word in content_lower for word in ["compare", "versus", "vs", "comparison"]):
            return {
                "type": "comparison",
                "data": {
                    "features": ["Performance", "Cost", "Scalability", "Support"],
                    "current": ["Average", "High", "Limited", "Basic"],
                    "proposed": ["Excellent", "Optimized", "Unlimited", "Premium"]
                }
            }
        
        # KPIs/Metrics
        elif any(word in content_lower for word in ["kpi", "metric", "performance", "result"]):
            return {
                "type": "kpi",
                "data": [
                    {"value": "87%", "label": "Efficiency", "change": "+12%", "trend": "up"},
                    {"value": "2.3x", "label": "ROI", "change": "+0.5x", "trend": "up"},
                    {"value": "$1.2M", "label": "Savings", "change": "+23%", "trend": "up"},
                    {"value": "45min", "label": "Time Saved", "change": "-15min", "trend": "down"}
                ]
            }
        
        # Default icons
        else:
            return {
                "type": "icons",
                "data": [
                    {"icon": "fa-lightbulb", "label": "Innovation"},
                    {"icon": "fa-users", "label": "Collaboration"},
                    {"icon": "fa-chart-line", "label": "Growth"},
                    {"icon": "fa-shield-alt", "label": "Security"}
                ]
            }


# CSS for visual elements
VISUAL_ELEMENTS_CSS = '''
/* Icon Grid */
.icon-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.icon-item {
    text-align: center;
}

.icon-circle {
    width: 80px;
    height: 80px;
    margin: 0 auto 1rem;
    background: linear-gradient(135deg, #8B1538, #00A9CE);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.icon-circle:hover {
    transform: scale(1.1);
}

.icon-item p {
    font-weight: 600;
    color: #333333;
}

/* Process Flow */
.process-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
    gap: 1rem;
}

.process-flow.column {
    flex-direction: column;
}

.process-step {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #f8fafc;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
}

.process-step:hover {
    border-color: #8B1538;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.step-number {
    width: 40px;
    height: 40px;
    background: #8B1538;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.25rem;
}

.process-arrow {
    color: #cbd5e1;
    font-size: 1.5rem;
}

/* Comparison Table */
.comparison-table {
    margin: 2rem 0;
    overflow-x: auto;
}

.comparison-table table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    overflow: hidden;
}

.comparison-table th {
    background: #8B1538;
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.comparison-table td {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
}

.comparison-table tr:last-child td {
    border-bottom: none;
}

.comparison-table tr:hover {
    background: #f8fafc;
}

.feature-name {
    font-weight: 600;
    color: #333333;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.kpi-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    text-align: center;
    transition: all 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    border-color: #8B1538;
}

.kpi-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #333333;
    margin-bottom: 0.5rem;
}

.kpi-label {
    font-size: 0.875rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.kpi-change {
    font-size: 1rem;
    font-weight: 600;
}

.kpi-change.positive {
    color: #10b981;
}

.kpi-change.negative {
    color: #ef4444;
}

/* Chart Container */
.chart-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin: 2rem 0;
}

.chart-container svg {
    max-width: 100%;
    height: auto;
}
'''