# openai_client.py
import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

from openai import OpenAI
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Enhanced JSON schema for AI medication selection
MEDICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "selected_medication": {
            "type": "object",
            "properties": {
                "drug_key": {"type": "string"},  # "ibuprofen", "acetaminophen", etc.
                "brand": {"type": "string"},     # "Advil", "Tylenol", etc.
                "generic": {"type": "string"},   # "Ibuprofen", "Acetaminophen", etc.
                "reasoning": {"type": "string"}, # Why this medication was chosen
                "safety_notes": {"type": "string"}, # Any safety considerations
            },
            "required": ["drug_key", "brand", "generic", "reasoning"]
        },
        "dosing": {
            "type": "object",
            "properties": {
                "dose_text": {"type": "string"},   # "2 tablets (200mg each)"
                "frequency": {"type": "string"},   # "every 6–8 hours with food"
                "total_mg": {"type": "number"},   # parsed mg per dose
                "max_daily_mg": {"type": "number"}, # calculated daily limit
                "dose_rationale": {"type": "string"}, # why this specific dose
            },
            "required": ["dose_text", "frequency", "total_mg"]
        },
        "alternatives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "drug_key": {"type": "string"},
                    "brand": {"type": "string"},
                    "generic": {"type": "string"},
                    "reason": {"type": "string"},
                    "when_to_consider": {"type": "string"}
                }
            }
        },
        "patient_education": {
            "type": "object",
            "properties": {
                "key_points": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "when_to_seek_help": {"type": "string"}
            }
        },
        "safety_validation": {
            "type": "object",
            "properties": {
                "dose_within_limits": {"type": "boolean"},
                "contraindications_checked": {"type": "boolean"},
                "age_appropriate": {"type": "boolean"},
                "weight_appropriate": {"type": "boolean"}
            }
        }
    },
    "required": ["selected_medication", "dosing", "safety_validation"]
}

# Enhanced prompt for AI pharmacist role
AI_PHARMACIST_PROMPT = """You are AbsorpGen AI, an advanced AI pharmacist assistant. Your role is to:

1. SELECT the most appropriate OTC medication based on symptoms, patient factors, and safety
2. CALCULATE personalized dosing considering age, weight, conditions, and pain level
3. PROVIDE comprehensive patient education and safety information
4. SUGGEST alternatives when primary choice has concerns
5. VALIDATE all recommendations against safety standards

You have access to these OTC medications:
- Acetaminophen (Tylenol): Fever, pain, headache, safe for most patients
- Ibuprofen (Advil, Motrin): Pain, inflammation, muscle aches, avoid with GI/kidney issues
- Dextromethorphan (Delsym): Dry cough, avoid with MAOIs
- Guaifenesin (Mucinex): Productive cough, chest congestion
- Cetirizine (Zyrtec): Allergies, once daily
- Loratadine (Claritin): Allergies, once daily
- Famotidine (Pepcid): Heartburn, acid reflux
- Meclizine (Dramamine): Nausea, motion sickness
- Calcium Carbonate (Tums): Heartburn, indigestion

SAFETY RULES:
- Never exceed single-dose caps: Ibuprofen max 600mg, Acetaminophen max 750mg
- Pediatric dosing: Conservative caps for under 18
- Condition-based adjustments: Reduce doses for kidney/liver/GI conditions
- Pain level 8+: Consider combination approaches
- Recent medication: Avoid same drug if taken recently with no relief

Return ONLY a JSON object matching the provided schema. Be thorough but safe."""

def get_ai_pharmacist_recommendation(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    AI pharmacist makes comprehensive medication decisions
    Returns: Complete medication recommendation with safety validation
    """
    # Build comprehensive patient context
    patient_context = {
        "demographics": {
            "age": payload.get("age"),
            "sex": payload.get("sex"),
            "height_cm": payload.get("height_cm"),
            "weight_kg": payload.get("weight_kg")
        },
        "symptoms": payload.get("symptoms", []),
        "allergies": payload.get("allergies", []),
        "conditions": payload.get("conditions", []),
        "pain_level": payload.get("pain_level"),
        "notes": payload.get("notes", ""),
        "recent_medication": payload.get("recent_medication", "")
    }

    # Ask AI for comprehensive recommendation
    messages = [
        {"role": "system", "content": AI_PHARMACIST_PROMPT},
        {"role": "user", "content": f"JSON schema:\n{json.dumps(MEDICATION_SCHEMA)}"},
        {"role": "user", "content": f"Patient assessment:\n{json.dumps(patient_context)}"}
    ]

    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.1,  # Slight creativity for better reasoning
            response_format={"type": "json_object"}
        )
        text = resp.choices[0].message.content
        data = json.loads(text)
        
        # Validate AI response structure
        if not all(key in data for key in ["selected_medication", "dosing", "safety_validation"]):
            return None
            
        return data
    except Exception as e:
        print(f"AI pharmacist error: {e}")
        return None

# Keep the old function for backward compatibility
def get_llm_dose(payload: Dict[str, Any], suggested_cap_mg: int, chosen_drug: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Legacy function - now calls the new AI pharmacist
    """
    ai_rec = get_ai_pharmacist_recommendation(payload)
    if not ai_rec:
        return None
    
    # Convert new format to old format for compatibility
    return {
        "drug_name": f"{ai_rec['selected_medication']['brand']} ({ai_rec['selected_medication']['generic']})",
        "dose_text": ai_rec["dosing"]["dose_text"],
        "frequency": ai_rec["dosing"]["frequency"],
        "rationale": ai_rec["selected_medication"]["reasoning"],
        "total_mg": ai_rec["dosing"]["total_mg"]
    } 