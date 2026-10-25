# AI Prompt Templates for CleanSignal

AIR_QUALITY_PROMPT = """
You are an environmental monitoring assistant. Analyze this pollution report and categorize it.

Report details:
- Description: {description}
- Location: {location}
- Reported type: {reported_type}

Categorize into one of these types:
1. air_quality - Smog, smoke, dust, chemical fumes, poor air quality
2. water_contamination - Chemical spills, sewage overflow, contaminated water
3. noise_pollution - Construction noise, traffic noise, industrial noise
4. waste_management - Illegal dumping, littering, improper waste disposal
5. other - Other environmental concerns

Return ONLY the category name (air_quality, water_contamination, noise_pollution, waste_management, or other).
"""

SEVERITY_ASSESSMENT_PROMPT = """
Assess the severity of this pollution incident on a scale of 1-5:
1 - Minor inconvenience, low impact
2 - Moderate concern, local impact
3 - Significant issue, community impact
4 - Serious problem, health concerns possible
5 - Critical emergency, immediate action needed

Incident description: {description}
Location: {location}

Return ONLY a number from 1-5.
"""

LOCATION_VALIDATION_PROMPT = """
Validate if this location is suitable for pollution reporting:
- Location: {location}
- Expected coordinates format: latitude, longitude

If valid, return the coordinates in JSON format: {"valid": true, "lat": X.XXXX, "lon": X.XXXX}
If invalid or unknown, return: {"valid": false, "reason": "..."}
"""

EMAIL_VERIFICATION_PROMPT = """
Verify if this email address appears to be valid:
- Email: {email}

Return JSON: {"valid": true/false, "reason": "..."}
""