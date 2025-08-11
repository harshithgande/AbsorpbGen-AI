from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import re

from validators import UserRequest, AITriage, APIError  # pain_level & notes included
from safety import has_red_flag
from dosing_rules import compute_conservative_dose

# Serve the SPA from /public so frontend + API share the SAME origin (5000)
app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)  # harmless; same-origin means browsers won't need it

# ----------------- Add permissive headers (belt & suspenders) -----------------
@app.after_request
def add_cors_headers(resp: Response):
    origin = request.headers.get("Origin")
    if origin:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Headers"] = request.headers.get(
        "Access-Control-Request-Headers", "Content-Type, Authorization"
    )
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp

# ----------------- Serve SPA -----------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        return ("", 204)
    return {"ok": True}

# ----------------- OTC catalog (import/fallback) -----------------
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
            "max_daily_mg": 1200,  # conservative OTC daily max
            "symptoms": ["muscle aches", "joint pain", "sprain", "back pain", "inflammation", "pain"],
            "avoid_if": ["ulcer", "gi bleed", "kidney", "renal", "pregnan"],
            "frequency_hours": 6,  # rendered as 6–8 below
            "frequency_label": "every 6–8 hours with food as needed",
        },
        "dextromethorphan": {
            "brands": ["Delsym", "Robitussin"],
            "generic": "Dextromethorphan",
            "form": "liquid",
            "mg_per_ml": 6,  # Delsym polistirex 30 mg per 5 mL
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

# ----------------- Helpers -----------------
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

# --- smarter note parsing ---
WORD_TO_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12
}

NO_RELIEF_RE = re.compile(
    r"(no\s*(relief|difference|effect)|did(?:n['’]t| not)\s*(work|help)|not\s*helping|ineffective|still\s*(in\s*pain|cough(ing)?))",
    re.I,
)

def _parse_hours_ago(text: str):
    """
    Accepts '2 hours ago', '2 hr', 'two hours ago', etc. Returns int hours or None.
    """
    if not text:
        return None
    m = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(hour|hr|hrs|hours)\s*(ago|back)?\b",
        text,
        flags=re.I,
    )
    if not m:
        return None
    raw = m.group(1).lower()
    try:
        return int(raw)
    except ValueError:
        return WORD_TO_INT.get(raw)

def detect_recent_medication(notes: str):
    """
    Detect a recent medication mention and no-relief indication.
    Returns (drug_key, hours_ago, no_relief_flag)
    """
    if not notes:
        return None, None, False
    txt = notes.lower()

    hours_ago = _parse_hours_ago(txt)
    no_relief = bool(NO_RELIEF_RE.search(txt))

    drug_key = None
    for key, aliases in NAME_ALIASES.items():
        for name in aliases:
            if name in txt:
                drug_key = key
                break
        if drug_key:
            break

    return drug_key, hours_ago, no_relief

def select_otc(symptoms, allergies, conditions, pain_level=None, notes: str = "") -> dict:
    """
    Deterministic OTC selection with:
      - allergy/condition screens
      - avoid same med if taken too recently OR user reported no relief
      - gentle bias to ibuprofen for high pain (>=7)
      - extra bias away from the failed drug; toward alternative
    """
    s = " ".join((symptoms or [])).lower()
    a = " ".join((allergies or [])).lower()
    c = " ".join((conditions or [])).lower()

    recent_key, hours_ago, no_relief = detect_recent_medication(notes)
    recent_min_interval = None
    if recent_key and recent_key in OTC:
        recent_min_interval = OTC[recent_key].get("min_interval_hours") or OTC[recent_key].get("frequency_hours")

    best_key, best_score = None, -10_000
    for key in OTC_ORDER:  # stable order
        meta = OTC[key]
        # allergy / condition screens
        if (meta["generic"].lower() in a) or any(b.lower() in a for b in meta["brands"]):
            continue
        if any(term in c for term in meta.get("avoid_if", [])):
            continue
        # avoid same drug too soon or if user says it didn't help
        if recent_key == key and (no_relief or (hours_ago is not None and recent_min_interval and hours_ago < recent_min_interval)):
            continue

        score = 0
        # symptom overlap
        score += sum(1 for kw in meta["symptoms"] if kw in s)

        # pain bias
        if pain_level is not None and pain_level >= 7 and key == "ibuprofen":
            score += 2

        # if acetaminophen failed, nudge toward ibuprofen
        if no_relief and recent_key == "acetaminophen" and key == "ibuprofen":
            score += 2

        # penalize the failed drug heavily
        if no_relief and recent_key == key:
            score -= 5

        if score > best_score:
            best_score, best_key = score, key

    if not best_key:
        best_key = "acetaminophen"

    choice = {"key": best_key, **OTC[best_key]}
    choice["brand"] = choice["brands"][0]
    return choice

def format_tablet_dose(total_mg: int, unit_mg: int):
    if unit_mg <= 0:
        return f"{total_mg} mg", 0, total_mg
    units = max(1, round(total_mg / unit_mg))
    confirmed = units * unit_mg
    text = f"{units} tablet{'s' if units != 1 else ''} ({unit_mg}mg each)"
    return text, units, confirmed

def format_liquid_dose(total_mg: int, mg_per_ml: float):
    if not mg_per_ml or mg_per_ml <= 0:
        return f"{total_mg} mg", 0.0, total_mg
    ml = round(total_mg / mg_per_ml, 1)
    confirmed = round(ml * mg_per_ml)
    text = f"{ml} mL (≈{confirmed}mg)"
    return text, ml, confirmed

def build_timing_advice(notes: str):
    """
    Respect min interval and acknowledge no-relief when present.
    """
    rk, hours_ago, no_relief = detect_recent_medication(notes or "")
    if not rk:
        return None
    meta = OTC.get(rk)
    if not meta:
        return None

    min_int = meta.get("min_interval_hours") or meta.get("frequency_hours")
    brand = meta["brands"][0]

    parts = []
    if hours_ago is not None:
        parts.append(f"You reported taking {brand} ({meta['generic']}) about {hours_ago} hour(s) ago.")
    else:
        parts.append(f"You reported taking {brand} ({meta['generic']}) recently.")

    if no_relief:
        parts.append("You also reported little or no relief.")

    if min_int and hours_ago is not None and hours_ago < min_int:
        wait = max(0, min_int - hours_ago)
        parts.append(f"Wait at least {wait} more hour(s) before another dose of that same medication.")

    return " ".join(parts)

# ----------------- API: Recommendation -----------------
@app.route("/recommend", methods=["POST", "OPTIONS"])
def recommend():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        payload = UserRequest(**(request.get_json(force=True)))
    except Exception as e:
        return jsonify(APIError(error=f"Invalid request: {e}").model_dump()), 400

    # 1) Safety triage
    if has_red_flag(payload.symptoms + payload.conditions):
        triage = AITriage(
            triage_alert="See a doctor",
            message="One or more symptoms suggest a potentially serious condition. Please seek medical care immediately.",
        )
        return jsonify(triage.model_dump()), 200

    # 2) Choose OTC (deterministic, US OTC only)
    choice = select_otc(
        payload.symptoms, payload.allergies, payload.conditions,
        pain_level=payload.pain_level, notes=(payload.notes or "")
    )
    drug_key = choice["key"]

    # 3) Dose calculation
    height = payload.height_cm or 170.0
    weight = payload.weight_kg or 70.0

    if drug_key in {"acetaminophen", "ibuprofen"}:
        suggested_mg = compute_conservative_dose(
            drug_key=drug_key,
            height_cm=height,
            weight_kg=weight,
            age=payload.age,
            conditions=payload.conditions,
        )
    else:
        suggested_mg = choice["single_dose_cap_mg"]

    cap = choice["single_dose_cap_mg"]
    max_day = choice.get("max_daily_mg")
    if suggested_mg > cap:
        suggested_mg = cap
    if suggested_mg <= 0:
        suggested_mg = cap

    # 4) Format instructions + verify unit math
    unit_details = {}
    if choice["form"] == "tablet":
        dose_text, units, confirmed_mg = format_tablet_dose(suggested_mg, choice["unit_mg"])
        unit_details = {"units_per_dose": units, "per_unit_mg": choice["unit_mg"], "confirmed_total_mg": confirmed_mg}
    elif choice["form"] == "liquid":
        dose_text, ml, confirmed_mg = format_liquid_dose(suggested_mg, choice["mg_per_ml"])
        unit_details = {"ml_per_dose": ml, "mg_per_ml": choice["mg_per_ml"], "confirmed_total_mg": confirmed_mg}
    else:
        dose_text = f"{suggested_mg} mg"
        unit_details = {"confirmed_total_mg": suggested_mg}

    freq_label = choice["frequency_label"]
    freq_hours = choice.get("frequency_hours")
    how_to_take = f"{dose_text} • {freq_label}"
    if drug_key == "ibuprofen" and freq_hours == 6:
        how_to_take = f"{dose_text} • every 6–8 hours with food as needed"

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
        "medical_disclaimer": (
            "IMPORTANT: AbsorpGen AI is a proof-of-concept and not a substitute for professional medical advice. "
            "Always consult a qualified clinician for diagnosis and treatment."
        ),
        "dose_basis": {
            "suggested_single_dose_mg": suggested_mg,
            "single_dose_cap_mg": cap,
            "max_daily_mg": max_day,
            "form": choice["form"],
            **unit_details,
            "policy": "BSA + age/condition reductions + hard OTC single-dose cap",
        },
    }
    return jsonify(response), 200


if __name__ == "__main__":
    # IMPORTANT: run on 5000 (matches your index.html logic / API_BASE)
    # Open http://localhost:5000/
    app.run(host="0.0.0.0", port=5000, debug=True)
