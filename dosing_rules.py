from math import sqrt
from typing import Optional
from config import MAX_DOSE_MG

# Utility: Mosteller BSA (m^2) from height (cm) and weight (kg)
def bsa_mosteller(height_cm: float, weight_kg: float) -> float:
    return sqrt((height_cm * weight_kg) / 3600.0)

# Conservative dose policy (demo): returns mg for selected OTCs
# NOTE: In production, this table would be drug‑specific per indication & age.
BASELINE_MG_PER_M2 = {
    "acetaminophen": 650,  # practical baseline per dose for common adult OTC use
    "ibuprofen": 400,
}

def age_adjustment_factor(age: Optional[int]) -> float:
    if age is None:
        return 1.0
    return 0.8 if age >= 65 else 1.0  # 20% reduction for ≥65

def condition_adjustment_factor(conditions: list[str]) -> float:
    text = " ".join((c or "").lower() for c in conditions or [])
    factor = 1.0
    # conservative reductions for hepatic/renal, ulcers, hypertension
    if any(k in text for k in ["liver", "hepatic"]):
        factor *= 0.8
    if any(k in text for k in ["kidney", "renal"]):
        factor *= 0.8
    if "ulcer" in text or "gi bleed" in text:
        factor *= 0.7
    return factor

def apply_safety_cap(drug_key: str, mg: float) -> float:
    cap = MAX_DOSE_MG.get(drug_key, mg)
    return min(mg, cap)

def compute_conservative_dose(drug_key: str, height_cm: float, weight_kg: float, age: Optional[int], conditions: list[str]) -> int:
    bsa = bsa_mosteller(height_cm, weight_kg)
    baseline = BASELINE_MG_PER_M2.get(drug_key, 0) * bsa
    adjusted = baseline * age_adjustment_factor(age) * condition_adjustment_factor(conditions)
    safe = apply_safety_cap(drug_key, adjusted)
    # Round to practical increments of 50 mg
    return int(round(safe / 50.0) * 50)