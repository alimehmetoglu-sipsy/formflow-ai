from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any
import os

class TemplateEngine:
    def __init__(self):
        # Get the templates directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(os.path.dirname(current_dir), "templates")
        
        # Create templates directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render(self, template_type: str, data: Dict) -> str:
        """Render HTML dashboard using appropriate template"""
        
        # For now, use a generic template if specific ones don't exist
        try:
            template_map = {
                "diet_plan": "diet_plan.html",
                "lead_score": "lead_score.html",
                "event_registration": "event_registration.html",
                "generic": "generic.html"
            }
            
            template_file = template_map.get(template_type, "generic.html")
            template = self.env.get_template(template_file)
            
            return template.render(data=data, template_type=template_type)
        except Exception as e:
            print(f"Template rendering error: {str(e)}")
            # Return a basic HTML template if rendering fails
            return self._get_fallback_html(template_type, data)
    
    def _get_fallback_html(self, template_type: str, data: Dict) -> str:
        """Generate fallback HTML when template rendering fails"""
        
        if template_type == "diet_plan":
            return self._render_diet_plan_html(data)
        elif template_type == "lead_score":
            return self._render_lead_score_html(data)
        elif template_type == "event_registration":
            return self._render_event_html(data)
        else:
            return self._render_generic_html(data)
    
    def _render_diet_plan_html(self, data: Dict) -> str:
        """Render diet plan HTML"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Personalized Diet Plan - FormFlow AI</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Inter', sans-serif; }}
                .gradient-bg {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
            </style>
        </head>
        <body class="bg-gray-50">
            <!-- Header -->
            <div class="gradient-bg text-white py-12">
                <div class="container mx-auto px-4">
                    <h1 class="text-4xl font-bold mb-4">Your 7-Day Diet Plan</h1>
                    <p class="text-xl opacity-90">Personalized nutrition for {data.get('user_profile', {}).get('goals', 'your health goals')}</p>
                </div>
            </div>
            
            <!-- Stats Cards -->
            <div class="container mx-auto px-4 -mt-8">
                <div class="grid md:grid-cols-4 gap-4">
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="text-gray-500 text-sm">Daily Calories</div>
                        <div class="text-3xl font-bold text-purple-600">{data.get('daily_calories', 2000)}</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="text-gray-500 text-sm">Protein</div>
                        <div class="text-3xl font-bold text-blue-600">{data.get('macro_breakdown', {}).get('protein', 150)}g</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="text-gray-500 text-sm">Carbs</div>
                        <div class="text-3xl font-bold text-green-600">{data.get('macro_breakdown', {}).get('carbs', 200)}g</div>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <div class="text-gray-500 text-sm">Fat</div>
                        <div class="text-3xl font-bold text-orange-600">{data.get('macro_breakdown', {}).get('fat', 65)}g</div>
                    </div>
                </div>
            </div>
            
            <!-- Weekly Meal Plan -->
            <div class="container mx-auto px-4 mt-8">
                <h2 class="text-2xl font-bold mb-6">Weekly Meal Plan</h2>
                <div class="grid md:grid-cols-7 gap-4">
                    {self._render_meal_days(data.get('meal_plan', {}))}
                </div>
            </div>
            
            <!-- Shopping List -->
            <div class="container mx-auto px-4 mt-8 mb-12">
                <h2 class="text-2xl font-bold mb-6">Shopping List</h2>
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="grid md:grid-cols-3 gap-6">
                        {self._render_shopping_list(data.get('shopping_list', {}))}
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="bg-gray-800 text-white py-8">
                <div class="container mx-auto px-4 text-center">
                    <p class="mb-2">Generated by FormFlow AI</p>
                    <p class="text-sm opacity-75">Transform your forms into intelligent dashboards</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_meal_days(self, meal_plan: Dict) -> str:
        """Render meal plan days"""
        days_html = []
        for day, meals in meal_plan.items():
            if isinstance(meals, dict):
                days_html.append(f"""
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="font-semibold text-purple-600 mb-3">{day.title()}</h3>
                    <div class="mb-3">
                        <div class="text-xs text-gray-500 mb-1">Breakfast</div>
                        <div class="text-sm font-medium">{meals.get('breakfast', {}).get('meal', 'Healthy breakfast')}</div>
                        <div class="text-xs text-gray-400">{meals.get('breakfast', {}).get('calories', 350)} cal</div>
                    </div>
                    <div class="mb-3">
                        <div class="text-xs text-gray-500 mb-1">Lunch</div>
                        <div class="text-sm font-medium">{meals.get('lunch', {}).get('meal', 'Nutritious lunch')}</div>
                        <div class="text-xs text-gray-400">{meals.get('lunch', {}).get('calories', 450)} cal</div>
                    </div>
                    <div class="mb-3">
                        <div class="text-xs text-gray-500 mb-1">Dinner</div>
                        <div class="text-sm font-medium">{meals.get('dinner', {}).get('meal', 'Balanced dinner')}</div>
                        <div class="text-xs text-gray-400">{meals.get('dinner', {}).get('calories', 550)} cal</div>
                    </div>
                </div>
                """)
        return ''.join(days_html)
    
    def _render_shopping_list(self, shopping_list: Dict) -> str:
        """Render shopping list"""
        lists_html = []
        for category, items in shopping_list.items():
            if isinstance(items, list) and items:
                items_html = ''.join([f"""
                <li class="text-sm text-gray-600 flex items-center">
                    <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    {item}
                </li>
                """ for item in items])
                
                lists_html.append(f"""
                <div>
                    <h3 class="font-semibold text-gray-700 mb-2">{category.title()}</h3>
                    <ul class="space-y-1">
                        {items_html}
                    </ul>
                </div>
                """)
        return ''.join(lists_html)
    
    def _render_lead_score_html(self, data: Dict) -> str:
        """Render lead score HTML"""
        score = data.get('lead_score', 0)
        category = data.get('lead_category', 'Unknown')
        color = 'green' if score > 70 else 'yellow' if score > 40 else 'red'
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lead Analysis Report - FormFlow AI</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-4xl font-bold mb-8">Lead Analysis Report</h1>
                
                <!-- Score Card -->
                <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
                    <div class="text-center">
                        <div class="text-6xl font-bold text-{color}-600">{score}</div>
                        <div class="text-2xl text-gray-600 mt-2">{category} Lead</div>
                    </div>
                </div>
                
                <!-- Insights -->
                <div class="bg-white rounded-lg shadow p-6 mb-8">
                    <h2 class="text-2xl font-bold mb-4">Key Insights</h2>
                    <ul class="space-y-2">
                        {"".join([f'<li class="flex items-start"><span class="text-green-500 mr-2">✓</span>{insight}</li>' for insight in data.get('key_insights', [])])}
                    </ul>
                </div>
                
                <!-- Recommended Actions -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-2xl font-bold mb-4">Recommended Actions</h2>
                    <ul class="space-y-2">
                        {"".join([f'<li class="flex items-start"><span class="text-blue-500 mr-2">→</span>{action}</li>' for action in data.get('recommended_actions', [])])}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_event_html(self, data: Dict) -> str:
        """Render event registration HTML"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Event Registration Confirmed - FormFlow AI</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8 max-w-2xl">
                <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-8">
                        <h1 class="text-3xl font-bold">Registration Confirmed!</h1>
                        <p class="mt-2">Your ticket is ready</p>
                    </div>
                    
                    <!-- Ticket Info -->
                    <div class="p-8">
                        <div class="mb-6">
                            <h2 class="text-xl font-semibold mb-2">Attendee Information</h2>
                            <p class="text-gray-600">Name: {data.get('attendee_name', 'Guest')}</p>
                            <p class="text-gray-600">Email: {data.get('attendee_email', '')}</p>
                        </div>
                        
                        <div class="mb-6">
                            <h2 class="text-xl font-semibold mb-2">Event Details</h2>
                            <p class="text-gray-600">Event: {data.get('event_details', {}).get('name', 'Event')}</p>
                            <p class="text-gray-600">Date: {data.get('event_details', {}).get('date', 'TBD')}</p>
                            <p class="text-gray-600">Time: {data.get('event_details', {}).get('time', 'TBD')}</p>
                            <p class="text-gray-600">Location: {data.get('event_details', {}).get('location', 'TBD')}</p>
                        </div>
                        
                        <div class="border-t pt-6">
                            <p class="text-center text-2xl font-mono font-bold text-purple-600">
                                {data.get('ticket_number', 'TICKET-001')}
                            </p>
                            <p class="text-center text-sm text-gray-500 mt-2">Your Ticket Number</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _render_generic_html(self, data: Dict) -> str:
        """Render generic dashboard HTML"""
        import json
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Form Response Dashboard - FormFlow AI</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-4xl font-bold mb-8">Form Response Analysis</h1>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-2xl font-bold mb-4">Response Summary</h2>
                    <pre class="bg-gray-100 p-4 rounded overflow-x-auto">
{json.dumps(data, indent=2)}
                    </pre>
                </div>
            </div>
        </body>
        </html>
        """