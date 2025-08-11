# otc_catalog.py

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
        "unit_mg": 500,                   # common OTC tablet
        "single_dose_cap_mg": 1000,       # per-dose cap
        "max_daily_mg": 3000,             # conservative daily max (demo)
        "symptoms": ["fever", "headache", "pain", "sore throat", "toothache"],
        "avoid_if": [],
        "frequency_hours": 6,              # every 6 hours
        "frequency_label": "every 6 hours as needed",
        "side_effects": "May cause nausea or upset stomach if taken on an empty stomach.",
    },
    "ibuprofen": {
        "brands": ["Advil", "Motrin"],
        "generic": "Ibuprofen",
        "form": "tablet",
        "unit_mg": 200,
        "single_dose_cap_mg": 800,
        "max_daily_mg": 1200,             # conservative OTC daily max
        "symptoms": ["muscle aches", "joint pain", "sprain", "back pain", "inflammation"],
        "avoid_if": ["ulcer", "gi bleed", "kidney", "renal", "pregnan"],
        "frequency_hours": 6,              # 6–8 is typical; we render 6–8 below
        "frequency_label": "every 6–8 hours with food as needed",
        "side_effects": "May cause stomach irritation; take with food and avoid if you have ulcers or kidney issues.",
    },
    "dextromethorphan": {
        "brands": ["Delsym", "Robitussin"],
        "generic": "Dextromethorphan",
        "form": "liquid",                 # <- use Delsym liquid to make q12h unambiguous
        "mg_per_ml": 6,                   # Delsym polistirex 30 mg per 5 mL -> 6 mg/mL
        "single_dose_cap_mg": 60,         # Delsym adult dose: 60 mg
        "max_daily_mg": 120,              # adult max
        "symptoms": ["cough", "dry cough"],
        "avoid_if": ["maoi", "linezolid", "serotonin"],
        "frequency_hours": 12,
        "frequency_label": "every 12 hours as needed",
        "side_effects": "May cause drowsiness or dizziness; avoid combining with certain antidepressants (MAOIs).",
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
        "side_effects": "May cause nausea; drink plenty of water to help loosen mucus.",
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
        "side_effects": "May cause mild drowsiness in some people.",
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
        "side_effects": "Generally non-drowsy; rare headache or dry mouth.",
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
        "side_effects": "Well tolerated; occasional headache or dizziness.",
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
        "side_effects": "May cause drowsiness; avoid driving until you know how you respond.",
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
        "side_effects": "May cause constipation if used frequently.",
    },
}
