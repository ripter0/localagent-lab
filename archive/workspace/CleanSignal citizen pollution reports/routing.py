import json
from typing import Dict, Any
from prompts import ROUTING_PROMPT, CLASSIFICATION_PROMPT, VERIFICATION_PROMPT

class RoutingEngine:
    """AI-powered routing engine for pollution reports"""
    
    def __init__(self):
        self.routes = {
            'local_municipality': 'Local Municipality',
            'environmental_agency': 'Environmental Agency',
            'health_department': 'Health Department',
            'emergency_services': 'Emergency Services'
        }
    
    def route_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a pollution report to appropriate authority"""
        # Extract key information from report
        location = report_data.get('location', '')
        pollutant = report_data.get('pollutant_type', '')
        description = report_data.get('description', '').lower()
        severity = report_data.get('severity', 1)
        
        # Simple keyword-based routing (AI would enhance this)
        if any(word in description for word in ['fire', 'explosion', 'immediate']):
            route_type = 'emergency_services'
            priority = 'high'
        elif pollutant.lower() in ['smoke', 'air quality', 'fumes']:
            route_type = 'health_department'
            priority = 'medium'
        elif pollutant.lower() in ['chemical', 'industrial waste', 'factory']:
            route_type = 'environmental_agency'
            priority = 'high'
        else:
            route_type = 'local_municipality'
            priority = 'low'
        
        return {
            'route_type': self.routes[route_type],
            'priority': priority,
            'reason': f"Based on pollutant type: {pollutant} and description keywords",
            'recommended_actions': self._get_recommended_actions(route_type, severity)
        }
    
    def _get_recommended_actions(self, route_type: str, severity: int) -> list:
        """Get recommended actions based on route type and severity"""
        base_actions = [
            'Document the incident with photos',
            'Record exact location and time',
            'Note weather conditions'
        ]
        
        if severity >= 4:
            base_actions.extend([
                'Contact emergency services immediately',
                'Evacuate nearby areas if safe to do so'
            ])
        elif severity >= 3:
            base_actions.append('Monitor situation and update regularly')
        
        return base_actions
    
    def classify_report(self, report_text: str) -> Dict[str, Any]:
        """Classify a pollution report for better routing"""
        # Extract entities using simple pattern matching
        location = ''
        pollutant = ''
        
        if 'near' in report_text.lower():
            location = 'residential'
        elif 'factory' in report_text.lower() or 'plant' in report_text.lower():
            location = 'industrial'
        elif 'park' in report_text.lower() or 'public' in report_text.lower():
            location = 'public_space'
        
        return {
            'location_type': location,
            'extracted_entities': {'location': location},
            'suggested_actions': ['Verify with local authorities']
        }