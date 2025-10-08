from flask import Flask, request, jsonify
import re
import logging
from typing import Dict, Any, Optional, Tuple, List

from validators import UserRequest, AITriage, APIError
from safety import has_red_flag
from dosing_rules import compute_conservative_dose
from openai_client import get_ai_pharmacist_recommendation

app = Flask(__name__, static_folder="public", static_url_path="")

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/health", methods=["GET"])
def health():
    try:
        ai_ok = get_ai_pharmacist_recommendation({
            "age": 30, "sex": "F", "height_cm": 165, "weight_kg": 60,
            "symptoms": ["headache"], "allergies": [], "conditions": [],
            "pain_level": 5, "notes": ""
        }) is not None
    except Exception:
        ai_ok = False
    return {"ok": True, "ai_pharmacist_ok": ai_ok}

# ───────── OTC fallback (kept minimal) ─────────
try:
    from otc_catalog import OTC, OTC_ORDER
except ImportError:
    OTC_ORDER = [
        "acetaminophen", "ibuprofen", "dextromethorphan",
        "guaifenesin", "cetirizine", "loratadine",
        "famotidine", "meclizine", "calcium_carbonate",
    ]
    OTC = {
        "acetaminophen": {"brands": ["Tylenol"], "generic": "Acetaminophen", "form": "tablet", "unit_mg": 500,
            "single_dose_cap_mg": 1000, "max_daily_mg": 3000,
            "frequency_hours": 6, "frequency_label": "every 6 hours as needed"},
        "ibuprofen": {"brands": ["Advil","Motrin"], "generic": "Ibuprofen", "form": "tablet", "unit_mg": 200,
            "single_dose_cap_mg": 600, "max_daily_mg": 1200,
            "frequency_hours": 6, "frequency_label": "every 6–8 hours with food as needed"},
        "dextromethorphan": {"brands": ["Delsym","Robitussin"], "generic": "Dextromethorphan", "form": "liquid",
            "mg_per_ml": 6, "single_dose_cap_mg": 60, "max_daily_mg": 120,
            "frequency_hours": 12, "frequency_label": "every 12 hours as needed"},
        "guaifenesin": {"brands": ["Mucinex"], "generic": "Guaifenesin", "form": "tablet", "unit_mg": 200,
            "single_dose_cap_mg": 600, "max_daily_mg": 2400,
            "frequency_hours": 4, "frequency_label": "every 4 hours as needed with water"},
        "cetirizine": {"brands": ["Zyrtec"], "generic": "Cetirizine", "form": "tablet", "unit_mg": 10,
            "single_dose_cap_mg": 10, "max_daily_mg": 10,
            "frequency_hours": 24, "frequency_label": "once daily"},
        "loratadine": {"brands": ["Claritin"], "generic": "Loratadine", "form": "tablet", "unit_mg": 10,
            "single_dose_cap_mg": 10, "max_daily_mg": 10,
            "frequency_hours": 24, "frequency_label": "once daily"},
        "famotidine": {"brands": ["Pepcid"], "generic": "Famotidine", "form": "tablet", "unit_mg": 10,
            "single_dose_cap_mg": 20, "max_daily_mg": 40,
            "frequency_hours": 12, "frequency_label": "once or twice daily as needed"},
        "meclizine": {"brands": ["Bonine"], "generic": "Meclizine", "form": "tablet", "unit_mg": 25,
            "single_dose_cap_mg": 25, "max_daily_mg": 50,
            "frequency_hours": 24, "frequency_label": "once daily as needed"},
        "calcium_carbonate": {"brands": ["Tums"], "generic": "Calcium Carbonate", "form": "tablet", "unit_mg": 500,
            "single_dose_cap_mg": 1000, "max_daily_mg": 3000,
            "frequency_hours": 4, "frequency_label": "as needed per label"},
    }

# ───────── Local emergency phrases (added STD/STI set) ─────────
LOCAL_RED_FLAGS = [
    # neuro/head injury
    "head trauma", "head injury", "concussion", "loss of consciousness", "passed out", "seizure",
    "worst headache", "slurred speech", "weakness on one side",
    # cardio/resp
    "chest pain", "shortness of breath", "difficulty breathing",
    # bleeding/sepsis
    "vomiting blood", "coughing blood", "black tarry stools", "stiff neck", "fever over 103",
    # pregnancy
    "pregnancy bleeding", "pregnancy pain",
    # allergic emergency
    "anaphylaxis", "severe allergic reaction",
    # stroke/mi keywords
    "suspected stroke", "suspected heart attack",
    # oncology
    "cancer",
    # NEW: any sexual disease (STD/STI and common names)
    "std", "sti", "sexually transmitted disease", "sexually transmitted infection",
    "chlamydia", "gonorrhea", "syphilis", "herpes", "hsv", "trichomonas", "trichomoniasis",
    "hpv", "genital warts", "hiv", "aids",
    "hepatitis b", "hepatitis c"
]

# ───────── Non-problem detector ─────────
NON_PROBLEM_TOKENS = {
    "", " ", "-", "none", "n/a", "na", "no", "test", "testing", "hello", "hi", "ok", "okay", "fine", "good"
}
def is_not_real_problem(symptoms: List[str], notes: str) -> bool:
    """
    Returns True if the user didn't really enter a symptom/problem.
    Heuristics: empty; only trivial tokens; length < 3 and not alphanumeric; 'none', 'test', etc.
    """
    s = " ".join(symptoms or []).strip().lower()
    n = (notes or "").strip().lower()
    if s in NON_PROBLEM_TOKENS and (n in NON_PROBLEM_TOKENS or n == ""):
        return True
    if not s and not n:
        return True
    # no letters/digits at all or extremely short
    if len(s) < 3 and len(n) < 3:
        return True
    return False

def text_has_local_red_flag(symptoms: List[str], conditions: List[str], notes: str) -> bool:
    text = " ".join((symptoms or []) + (conditions or []) + [notes or ""]).lower()
    return any(flag in text for flag in LOCAL_RED_FLAGS)

# ───────── helpers ─────────
def format_tablet_dose(total_mg:int, unit_mg:int):
    units = max(1, round(total_mg / unit_mg)) if unit_mg>0 else 1
    confirmed = units * unit_mg
    return f"{units} tablet{'s' if units!=1 else ''} ({unit_mg}mg each)", units, confirmed

def format_liquid_dose(total_mg:int, mg_per_ml:float):
    ml = round(total_mg / mg_per_ml, 1) if mg_per_ml>0 else 0.0
    confirmed = round(ml * mg_per_ml)
    return f"{ml} mL (≈{confirmed}mg)", ml, confirmed

def validate_dose_safety(drug_key: str, suggested_mg: int, age: int, weight_kg: float, conditions: list)->tuple[bool,str,int]:
    warnings = []
    corrected_mg = suggested_mg
    if age is not None and age < 12:
        warnings.append("Pediatric dosing requires special consideration"); corrected_mg = min(corrected_mg, 400)
    elif age is not None and age < 18:
        warnings.append("Adolescent dosing - using conservative approach"); corrected_mg = min(corrected_mg, 600)
    if weight_kg is not None and weight_kg < 50:
        warnings.append("Low body weight - reducing dose for safety"); corrected_mg = min(corrected_mg, 400)
    elif weight_kg is not None and weight_kg > 120:
        warnings.append("High body weight - dose may need adjustment")
    if any((c or "").lower() in ["kidney","renal","liver","hepatic"] for c in (conditions or [])):
        warnings.append("Kidney/liver conditions detected - using conservative dosing"); corrected_mg = min(corrected_mg, 400)
    if any((c or "").lower() in ["ulcer","gi bleed","stomach"] for c in (conditions or [])):
        warnings.append("GI conditions detected - ibuprofen may be contraindicated"); corrected_mg = min(corrected_mg, 400)
    if drug_key == "ibuprofen":
        corrected_mg = min(corrected_mg, 600)
        if suggested_mg > 600: warnings.append("High ibuprofen dose - consider acetaminophen alternative")
    elif drug_key == "acetaminophen":
        corrected_mg = min(corrected_mg, 750)
    corrected_mg = min(corrected_mg, suggested_mg)
    if corrected_mg < 200: warnings.append("Dose may be too low to be effective"); corrected_mg = max(corrected_mg, 200)
    return (len(warnings) == 0), ("; ".join(warnings) if warnings else "Dose validated and safe"), corrected_mg

# ───────── endpoint ─────────
@app.route("/recommend", methods=["POST", "OPTIONS"])
def recommend():
    if request.method == "OPTIONS":
        return "", 200

    # 1) Parse
    try:
        payload = UserRequest(**(request.get_json(force=True)))
    except Exception as e:
        return jsonify(APIError(error=f"Invalid request: {e}").model_dump()), 400

    # 1a) Require a real problem
    if is_not_real_problem(payload.symptoms or [], payload.notes or ""):
        return jsonify(APIError(error="Please enter a problem or symptom.").model_dump()), 400

    # 2) Static red flags from your original rules
    if has_red_flag((payload.symptoms or []) + (payload.conditions or [])):
        triage = AITriage(
            triage_alert="See a doctor",
            message="One or more symptoms suggest a potentially serious condition. Please seek medical care immediately."
        )
        return jsonify(triage.model_dump()), 200

    # 3) Local emergency backstop (now includes any sexual disease)
    if text_has_local_red_flag(payload.symptoms, payload.conditions, payload.notes or ""):
        triage = AITriage(
            triage_alert="See a doctor",
            message="One or more symptoms suggest a potentially serious condition. Please seek medical care."
        )
        return jsonify(triage.model_dump()), 200

    # 4) AI-first (also signals triage)
    ai_rec = get_ai_pharmacist_recommendation(request.get_json(force=True))
    ai_triage = (ai_rec or {}).get("triage", {}) if ai_rec else {}
    if ai_triage.get("red_flag"):
        reason = ai_triage.get("reason", "serious condition")
        triage = AITriage(
            triage_alert="See a doctor",
            message=f"One or more symptoms suggest a potentially serious condition ({reason}). Please seek medical care."
        )
        return jsonify(triage.model_dump()), 200

    # 5) If AI says no OTC → neutral card
    if not ai_rec or ai_rec.get("selected_medication", {}).get("drug_key") in [None, "", "none"]:
        return jsonify({
            "drug_name": "No OTC recommended",
            "brand": "None",
            "generic": "None",
            "dosage": "—",
            "frequency": "—",
            "max_per_24h": "—",
            "side_effects": "—",
            "timing_advice": None,
            "safety_validation": {
                "is_safe": True,
                "warning": ai_triage.get("reason") or "OTC self-treatment is not recommended.",
                "original_dose_mg": 0,
                "validated_dose_mg": 0,
                "dose_reduced": False
            },
            "ai_used": True,
            "medical_disclaimer": (
                "IMPORTANT: This demo is not medical advice. Always consult a clinician for diagnosis and treatment."
            )
        }), 200

    # 6) Finalize AI med with safety caps
    ai_key = ai_rec["selected_medication"]["drug_key"]
    if ai_key not in OTC:
        return jsonify({
            "drug_name": "No OTC recommended",
            "brand": "None",
            "generic": "None",
            "dosage": "—",
            "frequency": "—",
            "max_per_24h": "—",
            "side_effects": "—",
            "timing_advice": None,
            "safety_validation": {
                "is_safe": True,
                "warning": "Medication not in OTC catalog; consult a clinician.",
                "original_dose_mg": 0,
                "validated_dose_mg": 0,
                "dose_reduced": False
            },
            "ai_used": True,
            "medical_disclaimer": (
                "IMPORTANT: This demo is not medical advice. Always consult a clinician for diagnosis and treatment."
            )
        }), 200

    choice = {"key": ai_key, **OTC[ai_key]}
    choice["brand"] = choice["brands"][0] if choice.get("brands") else "Generic"

    height = payload.height_cm or 170.0
    weight = payload.weight_kg or 70.0
    if ai_key in {"acetaminophen", "ibuprofen"}:
        suggested_mg = compute_conservative_dose(
            drug_key=ai_key, height_cm=height, weight_kg=weight,
            age=payload.age, conditions=payload.conditions,
        )
    else:
        suggested_mg = choice["single_dose_cap_mg"]

    is_safe, safety_warning, validated_mg = validate_dose_safety(
        ai_key, suggested_mg, payload.age, weight, payload.conditions or []
    )

    if choice["form"] == "tablet":
        dose_text, _, confirmed_mg = format_tablet_dose(validated_mg, choice["unit_mg"])
    elif choice["form"] == "liquid":
        dose_text, _, confirmed_mg = format_liquid_dose(validated_mg, choice["mg_per_ml"])
    else:
        dose_text, confirmed_mg = f"{validated_mg} mg", validated_mg

    freq = ai_rec.get("dosing", {}).get("frequency") or choice.get("frequency_label", "follow label directions")
    max_day = choice.get("max_daily_mg", "Follow label directions")

    response = {
        "drug_name": f"{choice['brand']} ({choice['generic']})",
        "brand": choice["brand"],
        "generic": choice["generic"],
        "dosage": dose_text,
        "frequency": freq,
        "max_per_24h": max_day if isinstance(max_day, int) else str(max_day),
        "side_effects": "See label for common side effects.",
        "timing_advice": None,
        "safety_validation": {
            "is_safe": is_safe,
            "warning": safety_warning,
            "original_dose_mg": suggested_mg,
            "validated_dose_mg": confirmed_mg,
            "dose_reduced": confirmed_mg < suggested_mg
        },
        "ai_used": True,
        "medical_disclaimer": (
            "IMPORTANT: This demo is not medical advice. Always consult a clinician for diagnosis and treatment."
        ),
        "ai_details": ai_rec
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
