import os
import json
import boto3
from typing import Dict, Any, List

BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

DETERMINISTIC_ACTION_TEMPLATES = {
    "delivery_rider": "Prioritize high-mileage runs before {start}; schedule rest stops in enclosed facilities during {window}.",
    "parent": "Keep children inside for play sessions during the peak exposure window ({window}).",
    "runner": "Shift scheduled workout to indoor cardio or complete training prior to {start}.",
    "school_admin": "Move outdoor recesses, athletic practice, and bus queues indoors between {window}.",
    "office_commuter": "Depart before {start} or delay transit until after {end} to avoid trapped road exhaust."
}

def generate_ai_explanation(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invokes Amazon Bedrock to explain the ML prediction and provide profile-safe guidance.
    Falls back gracefully to deterministic templates if AWS Bedrock is inaccessible.
    """
    location = forecast_data.get("location", "Bengaluru")
    profile = forecast_data.get("profile", "office_commuter")
    risk = forecast_data.get("risk", "HIGH")
    window = forecast_data.get("forecast_window", "18:00-21:00")
    predicted_pm25 = forecast_data.get("predicted_pm25", 110)
    wind_speed = forecast_data.get("wind_speed", 1.8)

    # 1. Deterministic Fallback Template
    start, end = window.split("-") if "-" in window else ("18:00", "21:00")
    fallback_action = DETERMINISTIC_ACTION_TEMPLATES.get(
        profile,
        "Limit prolonged outdoor physical exertion during the elevated exposure window."
    ).format(start=start, end=end, window=window)

    fallback_payload = {
        "summary": f"{risk.replace('_', ' ')} pollution surge expected across {location}.",
        "why": [
            f"Particulate matter trend is accelerating toward {predicted_pm25} µg/m³",
            f"Surface wind speed of {wind_speed} m/s prevents adequate pollutant dispersion",
            "Diurnal traffic volume peaks along primary commuting corridors"
        ],
        "action": fallback_action,
        "is_ai_generated": False
    }

    # 2. Attempt Amazon Bedrock Invocation
    try:
        client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        
        prompt = f"""
You are the explainability engine for BreatheAhead, an air-pollution early-warning system in India.
Context:
- Location: {location}
- User Profile: {profile}
- Risk Level: {risk}
- High-Risk Window: {window}
- Forecasted PM2.5: {predicted_pm25} µg/m³
- Wind Speed: {wind_speed} m/s

CRITICAL RULES:
1. Do NOT make clinical or medical diagnoses (do not say "you will suffer an asthma attack").
2. Focus on clear, preventive, operational scheduling recommendations.
3. You must output raw JSON matching this schema:
{{
  "summary": "Short 1-sentence warning",
  "why": ["driver 1", "driver 2", "driver 3"],
  "action": "Profile-specific actionable guidance"
}}
Do not include any Markdown or formatting tags outside the JSON.
"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}]
        })

        response = client.invoke_model(
            modelId=CLAUDE_MODEL_ID,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        
        raw_body = response["body"].read().decode("utf-8")
        parsed_body = json.loads(raw_body)
        ai_text = parsed_body["content"][0]["text"].strip()
        
        # Clean potential markdown wrapping
        if ai_text.startswith("```json"):
            ai_text = ai_text[7:-3].strip()
        elif ai_text.startswith("```"):
            ai_text = ai_text[3:-3].strip()
            
        result = json.loads(ai_text)
        result["is_ai_generated"] = True
        return result

    except Exception as e:
        # Graceful degradation ensures frontend never breaks during demo
        return fallback_payload