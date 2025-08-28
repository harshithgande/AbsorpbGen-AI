from flask import Flask, request, jsonify
import re
import logging

from validators import UserRequest, AITriage, APIError  # pain_level & notes included
from safety import has_red_flag
from dosing_rules import compute_conservative_dose
from openai_client import get_ai_pharmacist_recommendation

# ──────────────────────────────────────────────────────────────────────────────
# Serve the SPA from /public (with basic CORS support)
# ──────────────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="public", static_url_path="")

# Simple CORS headers for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ─────────────────── Optional: serve SPA ───────────────────
@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/health", methods=["GET"])
def health():
    # Test AI pharmacist connectivity
    ai_ok = False
    try:
        # Simple test call to check if AI pharmacist is working
        test_payload = {"age": 30, "sex": "F", "height_cm": 165, "weight_kg": 60, "symptoms": ["headache"], "allergies": [], "conditions": [], "pain_level": 5, "notes": ""}
        test_result = get_ai_pharmacist_recommendation(test_payload)
        ai_ok = test_result is not None
    except Exception as e:
        ai_ok = False
        print(f"Health check error: {e}")
    
    return {"ok": True, "ai_pharmacist_ok": ai_ok}

# ─────────────────── OTC catalog (import/fallback) ───────────────────
try:
    from otc_catalog import OTC, OTC_ORDER
except ImportError:
    OTC_ORDER = [
        "acetaminophen", "ibuprofen", "dextromethorphan",
        "guaifenesin", "cetirizine", "loratadine",
        "famotidine", "meclizine", "calcium_carbonate",
    ]
    OTC = {
        "acetaminophen": {
            "brands": ["Tylenol", "Equate Acetaminophen"],
            "generic": "Acetaminophen",
            "form": "tablet",
            "unit_mg": 500,
            "single_dose_cap_mg": 1000,
            "max_daily_mg": 3000,
            "symptoms": ["fever", "headache", "pain", "sore throat", "toothache"],
            "avoid_if": [],
            "frequency_hours": 6,
            "frequency_label": "every 6 hours as needed",
        },
        "ibuprofen": {
            "brands": ["Advil", "Motrin"],
            "generic": "Ibuprofen",
            "form": "tablet",
            "unit_mg": 200,
            "single_dose_cap_mg": 800,
            "max_daily_mg": 1200,
            "symptoms": ["muscle aches", "joint pain", "sprain", "back pain", "inflammation", "pain"],
            "avoid_if": ["ulcer", "gi bleed", "kidney", "renal", "pregnan"],
            "frequency_hours": 6,
            "frequency_label": "every 6–8 hours with food as needed",
        },
        "dextromethorphan": {
            "brands": ["Delsym", "Robitussin"],
            "generic": "Dextromethorphan",
            "form": "liquid",
            "mg_per_ml": 6,  # 30 mg per 5 mL
            "single_dose_cap_mg": 60,
            "max_daily_mg": 120,
            "symptoms": ["cough", "dry cough"],
            "avoid_if": ["maoi", "linezolid", "serotonin"],
            "frequency_hours": 12,
            "frequency_label": "every 12 hours as needed",
        },
        "guaifenesin": {
            "brands": ["Mucinex", "Robitussin Chest Congestion"],
            "generic": "Guaifenesin",
            "form": "tablet",
            "unit_mg": 200,
            "single_dose_cap_mg": 600,
            "max_daily_mg": 2400,
            "symptoms": ["chest congestion", "productive cough", "mucus"],
            "avoid_if": [],
            "frequency_hours": 4,
            "frequency_label": "every 4 hours as needed with water",
        },
        "cetirizine": {
            "brands": ["Zyrtec"],
            "generic": "Cetirizine",
            "form": "tablet",
            "unit_mg": 10,
            "single_dose_cap_mg": 10,
            "max_daily_mg": 10,
            "symptoms": ["allergies", "sneezing", "runny nose", "itchy eyes"],
            "avoid_if": [],
            "frequency_hours": 24,
            "frequency_label": "once daily",
        },
        "loratadine": {
            "brands": ["Claritin"],
            "generic": "Loratadine",
            "form": "tablet",
            "unit_mg": 10,
            "single_dose_cap_mg": 10,
            "max_daily_mg": 10,
            "symptoms": ["allergies", "sneezing", "runny nose", "itchy eyes"],
            "avoid_if": [],
            "frequency_hours": 24,
            "frequency_label": "once daily",
        },
        "famotidine": {
            "brands": ["Pepcid"],
            "generic": "Famotidine",
            "form": "tablet",
            "unit_mg": 10,
            "single_dose_cap_mg": 20,
            "max_daily_mg": 40,
            "symptoms": ["heartburn", "acid reflux", "indigestion"],
            "avoid_if": [],
            "frequency_hours": 12,
            "frequency_label": "once or twice daily as needed",
        },
        "meclizine": {
            "brands": ["Dramamine Less Drowsy", "Bonine"],
            "generic": "Meclizine",
            "form": "tablet",
            "unit_mg": 25,
            "single_dose_cap_mg": 25,
            "max_daily_mg": 50,
            "symptoms": ["nausea", "motion sickness", "vertigo"],
            "avoid_if": [],
            "frequency_hours": 24,
            "frequency_label": "once daily as needed (30–60 minutes before travel)",
        },
        "calcium_carbonate": {
            "brands": ["Tums"],
            "generic": "Calcium Carbonate",
            "form": "tablet",
            "unit_mg": 500,
            "single_dose_cap_mg": 1000,
            "max_daily_mg": 3000,
            "symptoms": ["heartburn", "sour stomach", "indigestion"],
            "avoid_if": [],
            "frequency_hours": 4,
            "frequency_label": "as needed per label",
        },
    }

# ───────────────────────── Helpers (same as your current file) ─────────────────────────
NAME_ALIASES = {
    "acetaminophen": ["acetaminophen", "tylenol", "paracetamol"],
    "ibuprofen": ["ibuprofen", "advil", "motrin"],
    "dextromethorphan": ["dextromethorphan", "delsym", "robitussin dm", "dm"],
    "guaifenesin": ["guaifenesin", "mucinex", "robitussin chest congestion"],
    "cetirizine": ["cetirizine", "zyrtec"],
    "loratadine": ["loratadine", "claritin"],
    "famotidine": ["famotidine", "pepcid"],
    "meclizine": ["meclizine", "bonine", "dramamine less drowsy"],
    "calcium_carbonate": ["calcium carbonate", "tums"],
}

WORD_TO_INT = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
NO_RELIEF_RE = re.compile(r"(no\s*(relief|difference|effect)|did(?:n['']t| not)\s*(work|help)|not\s*helping|ineffective|still\s*(in\s*pain|cough(ing)?))", re.I)

def _parse_hours_ago(text:str):
    m = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(hour|hr|hrs|hours)\s*(ago|back)?\b", text or "", flags=re.I)
    if not m: return None
    raw = m.group(1).lower()
    try: return int(raw)
    except ValueError: return WORD_TO_INT.get(raw)

def detect_recent_medication(notes:str):
    if not notes: return None, None, False
    txt = notes.lower()
    hours_ago = _parse_hours_ago(txt)
    no_relief = bool(NO_RELIEF_RE.search(txt))
    drug_key = None
    for key, aliases in NAME_ALIASES.items():
        if any(name in txt for name in aliases):
            drug_key = key; break
    return drug_key, hours_ago, no_relief

def validate_dose_safety(drug_key: str, suggested_mg: int, age: int, weight_kg: float, conditions: list) -> tuple[bool, str, int]:
    """
    Comprehensive dose safety validation with multiple checks
    Returns: (is_safe, warning_message, corrected_mg)
    """
    warnings = []
    corrected_mg = suggested_mg
    
    # 1. Age-based safety checks
    if age < 12:
        warnings.append("Pediatric dosing requires special consideration")
        corrected_mg = min(corrected_mg, 400)  # Conservative pediatric cap
    elif age < 18:
        warnings.append("Adolescent dosing - using conservative approach")
        corrected_mg = min(corrected_mg, 600)
    
    # 2. Weight-based safety (for very light or heavy patients)
    if weight_kg < 50:
        warnings.append("Low body weight - reducing dose for safety")
        corrected_mg = min(corrected_mg, 400)
    elif weight_kg > 120:
        warnings.append("High body weight - dose may need adjustment")
    
    # 3. Condition-based safety
    if any(cond.lower() in ["kidney", "renal", "liver", "hepatic"] for cond in conditions):
        warnings.append("Kidney/liver conditions detected - using conservative dosing")
        corrected_mg = min(corrected_mg, 400)
    
    if any(cond.lower() in ["ulcer", "gi bleed", "stomach"] for cond in conditions):
        warnings.append("GI conditions detected - ibuprofen may be contraindicated")
        corrected_mg = min(corrected_mg, 400)
    
    # 4. Drug-specific safety caps
    if drug_key == "ibuprofen":
        # Conservative ibuprofen caps
        if age < 18:
            corrected_mg = min(corrected_mg, 400)  # Max 2 tablets for minors
        else:
            corrected_mg = min(corrected_mg, 600)  # Max 3 tablets for adults
        
        # Additional ibuprofen warnings
        if suggested_mg > 600:
            warnings.append("High ibuprofen dose - consider acetaminophen alternative")
    
    elif drug_key == "acetaminophen":
        # Conservative acetaminophen caps
        if age < 18:
            corrected_mg = min(corrected_mg, 500)  # Max 1 tablet for minors
        else:
            corrected_mg = min(corrected_mg, 750)  # Max 1.5 tablets for adults
    
    # 5. Absolute safety caps
    corrected_mg = min(corrected_mg, suggested_mg)  # Never exceed original suggestion
    
    # 6. Minimum effective dose check
    if corrected_mg < 200:
        warnings.append("Dose may be too low to be effective")
        corrected_mg = max(corrected_mg, 200)
    
    warning_msg = "; ".join(warnings) if warnings else "Dose validated and safe"
    
    return len(warnings) == 0, warning_msg, corrected_mg

def suggest_alternative_medication(symptoms: list, allergies: list, conditions: list, pain_level: int, notes: str) -> dict:
    """
    Suggest alternative medications when primary choice has safety concerns
    """
    alternatives = []
    
    # If ibuprofen has safety concerns, suggest acetaminophen
    if any(cond.lower() in ["ulcer", "gi bleed", "kidney", "renal"] for cond in conditions):
        if "pain" in symptoms or "fever" in symptoms:
            alternatives.append({
                "drug": "acetaminophen",
                "reason": "Safer alternative for patients with GI/kidney conditions",
                "brand": "Tylenol",
                "generic": "Acetaminophen"
            })
    
    # If acetaminophen has concerns, suggest ibuprofen (if no GI issues)
    if any(cond.lower() in ["liver", "hepatic"] for cond in conditions):
        if "pain" in symptoms and not any(cond.lower() in ["ulcer", "gi bleed"] for cond in conditions):
            alternatives.append({
                "drug": "ibuprofen",
                "reason": "Alternative for patients with liver concerns",
                "brand": "Advil",
                "generic": "Ibuprofen"
            })
    
    # For high pain levels, suggest combination approach
    if pain_level >= 8:
        alternatives.append({
            "drug": "combination",
            "reason": "High pain level - consider alternating acetaminophen and ibuprofen",
            "brand": "Alternating",
            "generic": "Acetaminophen + Ibuprofen"
        })
    
    return alternatives

def select_otc(symptoms, allergies, conditions, pain_level=None, notes:str="")->dict:
    s = " ".join((symptoms or [])).lower()
    a = " ".join((allergies or [])).lower()
    c = " ".join((conditions or [])).lower()

    recent_key, hours_ago, no_relief = detect_recent_medication(notes)
    recent_min_interval = OTC.get(recent_key, {}).get("frequency_hours") if recent_key else None

    best_key, best_score = None, -10_000
    for key in OTC_ORDER:
        meta = OTC[key]
        if (meta["generic"].lower() in a) or any(b.lower() in a for b in meta["brands"]):
            continue
        if any(term in c for term in meta.get("avoid_if", [])):
            continue
        if recent_key == key and (no_relief or (hours_ago is not None and recent_min_interval and hours_ago < recent_min_interval)):
            continue
        score = sum(1 for kw in meta["symptoms"] if kw in s)
        if pain_level is not None and pain_level >= 7 and key == "ibuprofen":
            score += 2
        if no_relief and recent_key == "acetaminophen" and key == "ibuprofen":
            score += 2
        if no_relief and recent_key == key:
            score -= 5
        if score > best_score:
            best_score, best_key = score, key

    if not best_key:
        best_key = "acetaminophen"
    choice = {"key": best_key, **OTC[best_key]}
    choice["brand"] = choice["brands"][0]
    return choice

def format_tablet_dose(total_mg:int, unit_mg:int):
    units = max(1, round(total_mg / unit_mg)) if unit_mg>0 else 1
    confirmed = units * unit_mg
    return f"{units} tablet{'s' if units!=1 else ''} ({unit_mg}mg each)", units, confirmed

def format_liquid_dose(total_mg:int, mg_per_ml:float):
    ml = round(total_mg / mg_per_ml, 1) if mg_per_ml>0 else 0.0
    confirmed = round(ml * mg_per_ml)
    return f"{ml} mL (≈{confirmed}mg)", ml, confirmed

def build_timing_advice(notes:str):
    rk, hours_ago, no_relief = detect_recent_medication(notes or "")
    if not rk: return None
    meta = OTC.get(rk);  min_int = meta.get("frequency_hours"); brand = meta["brands"][0]
    parts = [f"You reported taking {brand} ({meta['generic']}) " + (f"about {hours_ago} hour(s) ago." if hours_ago is not None else "recently.")]
    if no_relief: parts.append("You also reported little or no relief.")
    if min_int and hours_ago is not None and hours_ago < min_int:
        wait = max(0, min_int - hours_ago)
        parts.append(f"Wait at least {wait} more hour(s) before another dose of that same medication.")
    return " ".join(parts)

# ───────────────────────── API: Recommendation ─────────────────────────
@app.route("/recommend", methods=["POST", "OPTIONS"])
def recommend():
    if request.method == "OPTIONS":
        return "", 200
    try:
        payload = UserRequest(**(request.get_json(force=True)))
    except Exception as e:
        return jsonify(APIError(error=f"Invalid request: {e}").model_dump()), 400

    if has_red_flag(payload.symptoms + payload.conditions):
        triage = AITriage(
            triage_alert="See a doctor",
            message="One or more symptoms suggest a potentially serious condition. Please seek medical care immediately.",
        )
        return jsonify(triage.model_dump()), 200

    choice = select_otc(
        payload.symptoms, payload.allergies, payload.conditions,
        pain_level=payload.pain_level, notes=(payload.notes or "")
    )
    drug_key = choice["key"]

    height = payload.height_cm or 170.0
    weight = payload.weight_kg or 70.0
    if drug_key in {"acetaminophen", "ibuprofen"}:
        suggested_mg = compute_conservative_dose(
            drug_key=drug_key, height_cm=height, weight_kg=weight,
            age=payload.age, conditions=payload.conditions,
        )
    else:
        suggested_mg = choice["single_dose_cap_mg"]

    cap = choice["single_dose_cap_mg"]
    max_day = choice.get("max_daily_mg")
    if suggested_mg > cap: suggested_mg = cap
    if suggested_mg <= 0: suggested_mg = cap
    
    # DOUBLE-CHECK: Comprehensive safety validation
    is_safe, safety_warning, validated_mg = validate_dose_safety(
        drug_key, suggested_mg, payload.age, weight, payload.conditions or []
    )
    
    # If dose is unsafe, suggest alternatives
    alternatives = []
    if not is_safe:
        alternatives = suggest_alternative_medication(
            payload.symptoms or [], payload.allergies or [], 
            payload.conditions or [], payload.pain_level or 0, 
            payload.notes or ""
        )
    
    # Use the validated (safer) dose
    suggested_mg = validated_mg
    original_suggested_mg = suggested_mg  # Keep track of original for comparison
    
    # Ensure validated_mg is always available for fallback dosing
    final_validated_mg = validated_mg

    # Try to get AI pharmacist recommendation first, with fallback to rule-based
    ai_recommendation = None
    try:
        ai_recommendation = get_ai_pharmacist_recommendation(request.get_json(force=True))
        if ai_recommendation:
            logging.info(f"AI pharmacist recommendation: {ai_recommendation['selected_medication']['reasoning']}")
            # Use AI-selected medication if different from rule-based choice
            if ai_recommendation['selected_medication']['drug_key'] != drug_key:
                logging.info(f"AI selected {ai_recommendation['selected_medication']['drug_key']} instead of {drug_key}")
                # Update choice to AI selection
                ai_drug_key = ai_recommendation['selected_medication']['drug_key']
                if ai_drug_key in OTC:
                    choice = {"key": ai_drug_key, **OTC[ai_drug_key]}
                    choice["brand"] = choice["brands"][0]
                    drug_key = ai_drug_key
                    # Recalculate safety caps for new drug
                    if drug_key in {"acetaminophen", "ibuprofen"}:
                        suggested_mg = compute_conservative_dose(
                            drug_key=drug_key, height_cm=height, weight_kg=weight,
                            age=payload.age, conditions=payload.conditions,
                        )
                    else:
                        suggested_mg = choice["single_dose_cap_mg"]
                    # Re-validate with new drug
                    is_safe, safety_warning, validated_mg = validate_dose_safety(
                        drug_key, suggested_mg, payload.age, weight, payload.conditions or []
                    )
                    suggested_mg = validated_mg
    except Exception as e:
        logging.warning(f"AI pharmacist failed, using rule-based fallback: {e}")
        ai_recommendation = None

    # Use AI pharmacist dosing if available, otherwise fall back to rule-based
    if ai_recommendation and ai_recommendation.get("dosing"):
        ai_dosing = ai_recommendation["dosing"]
        dose_text = ai_dosing.get("dose_text", "")
        how_to_take = ai_dosing.get("frequency", "")
        ai_total_mg = ai_dosing.get("total_mg", 0)
        
        # TRIPLE-CHECK: Re-verify unit math & cap for safety (never exceed validated dose)
        if choice["form"] == "tablet":
            _, units, confirmed_mg = format_tablet_dose(min(ai_total_mg, final_validated_mg), choice["unit_mg"])
            unit_details = {"units_per_dose": units, "per_unit_mg": choice["unit_mg"], "confirmed_total_mg": confirmed_mg}
        elif choice["form"] == "liquid":
            _, ml, confirmed_mg = format_liquid_dose(min(ai_total_mg, final_validated_mg), choice["mg_per_ml"])
            unit_details = {"ml_per_dose": ml, "mg_per_ml": choice["mg_per_ml"], "confirmed_total_mg": confirmed_mg}
        else:
            confirmed_mg = min(ai_total_mg, final_validated_mg)
            unit_details = {"confirmed_total_mg": confirmed_mg}
    else:
        # Fallback to rule-based dosing (using validated dose)
        if choice["form"] == "tablet":
            dose_text, units, confirmed_mg = format_tablet_dose(final_validated_mg, choice["unit_mg"])
            unit_details = {"units_per_dose": units, "per_unit_mg": choice["unit_mg"], "confirmed_total_mg": confirmed_mg}
        elif choice["form"] == "liquid":
            dose_text, ml, confirmed_mg = format_liquid_dose(final_validated_mg, choice["mg_per_ml"])
            unit_details = {"ml_per_dose": ml, "mg_per_ml": choice["mg_per_ml"], "confirmed_total_mg": confirmed_mg}
        else:
            dose_text = f"{final_validated_mg} mg"
            unit_details = {"confirmed_total_mg": final_validated_mg}

    # how_to_take is now set in the AI pharmacist dosing section above
    # If we're using fallback, set it here
    if not ai_recommendation or not ai_recommendation.get("dosing", {}).get("frequency"):
        freq_label = choice["frequency_label"]
        if drug_key == "ibuprofen" and choice.get("frequency_hours") == 6:
            how_to_take = f"{dose_text} • every 6–8 hours with food as needed"
        else:
            how_to_take = f"{dose_text} • {freq_label}"

    timing_advice = build_timing_advice(payload.notes or "")

    response = {
        "drug_name": f"{choice['brand']} ({choice['generic']})",
        "dosage": dose_text,
        "frequency": how_to_take,
        "side_effects": (
            "May cause stomach irritation; take with food and avoid if you have ulcers or kidney issues."
            if drug_key == "ibuprofen" else
            "May cause nausea or upset stomach if taken on an empty stomach."
            if drug_key == "acetaminophen" else
            "May cause drowsiness or dizziness; avoid combining with certain antidepressants (MAOIs)."
            if drug_key == "dextromethorphan" else
            "See label for common side effects."
        ),
        "timing_advice": timing_advice,
        "safety_validation": {
            "is_safe": is_safe,
            "warning": safety_warning,
            "original_dose_mg": original_suggested_mg,
            "validated_dose_mg": final_validated_mg,
            "dose_reduced": final_validated_mg < original_suggested_mg
        },
        "ai_pharmacist": {
            "medication_selected": ai_recommendation["selected_medication"] if ai_recommendation else None,
            "dosing_recommendation": ai_recommendation["dosing"] if ai_recommendation else None,
            "alternatives": ai_recommendation.get("alternatives", []) if ai_recommendation else [],
            "patient_education": ai_recommendation.get("patient_education", {}) if ai_recommendation else {},
            "safety_validation": ai_recommendation.get("safety_validation", {}) if ai_recommendation else {}
        } if ai_recommendation else None,
        "alternatives": alternatives if alternatives else None,
        "medical_disclaimer": (
            "IMPORTANT: AbsorpGen AI is a proof-of-concept and not a substitute for professional medical advice. "
            "Always consult a qualified clinician for diagnosis and treatment."
        ),
        "dose_basis": {
            "suggested_single_dose_mg": final_validated_mg,  # Use validated dose
            "single_dose_cap_mg": cap,
            "max_daily_mg": max_day,
            "form": choice["form"],
            **unit_details,
            "policy": "AI PHARMACIST: Intelligent medication selection + comprehensive safety validation + hard OTC caps",
            "ai_used": ai_recommendation is not None,
            "safety_checks_passed": is_safe,
        },
    }
    return jsonify(response), 200


if __name__ == "__main__":
    # If you open the frontend at http://localhost:5000/, calls to http://127.0.0.1:5000
    # will include an Origin header that matches the allowlist above.
    app.run(host="0.0.0.0", port=5000, debug=True) 