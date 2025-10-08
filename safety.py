RED_FLAGS = {
    # Cardiovascular Emergencies
    "chest pain", "heart attack", "heart pain", "heart problems", "cardiac", "heartache",
    "shortness of breath", "difficulty breathing", "breathing problems",
    "irregular heartbeat", "rapid heartbeat", "heart palpitations",
    
    # Neurological Emergencies
    "stroke", "severe headache", "sudden severe headache", "thunderclap headache",
    "numbness", "weakness on one side", "facial drooping", "speech problems",
    "confusion", "loss of consciousness", "fainting", "seizure", "convulsion",
    
    # Gastrointestinal Emergencies
    "blood in vomit", "vomiting blood", "black stools", "bloody stool", "rectal bleeding",
    "severe abdominal pain", "acute abdomen", "appendicitis", "severe nausea",
    
    # Respiratory Emergencies
    "severe breathing difficulty", "can't breathe", "choking", "severe asthma attack",
    
    # Other Medical Emergencies
    "severe pain", "unbearable pain", "crushing pain", "suicidal thoughts",
    "severe allergic reaction", "anaphylaxis", "severe swelling", "difficulty swallowing",
    "high fever", "fever over 103", "severe dehydration", "severe dizziness",
    
    # Mental Health Emergencies
    "suicidal", "self harm", "psychotic", "hallucinations", "severe depression",
    
    # Trauma
    "severe injury", "major trauma", "head injury", "loss of consciousness",
    
    # Cancer/Serious Conditions
    "cancer", "tumor", "lump", "unexplained weight loss", "severe fatigue",
}

CASUAL_HINTS = {
    # Pain and Inflammation
    "mild headache", "headache", "tension headache", "migraine",
    "muscle aches", "muscle pain", "sore muscles", "knee pain", "joint pain",
    "back pain", "neck pain", "shoulder pain", "sprain", "strain",
    "inflammation", "swelling", "bruise", "minor injury",
    
    # Respiratory
    "cough", "dry cough", "productive cough", "chest congestion", "mucus",
    "runny nose", "stuffy nose", "nasal congestion", "sneezing",
    "mild cold", "common cold", "flu symptoms", "mild fever",
    
    # Gastrointestinal
    "stomach ache", "stomach pain", "abdominal pain", "belly ache",
    "heartburn", "acid reflux", "indigestion", "sour stomach", "upset stomach",
    "nausea", "mild nausea", "motion sickness", "diarrhea", "constipation",
    "gas", "bloating", "stomach upset",
    
    # Allergies
    "allergies", "seasonal allergies", "hay fever", "itchy eyes", "watery eyes",
    "allergic reaction", "mild allergic reaction",
    
    # Sleep and Energy
    "insomnia", "trouble sleeping", "fatigue", "tiredness", "low energy",
    
    # Skin
    "rash", "mild rash", "itchy skin", "dry skin", "minor burn",
    "sunburn", "bug bite", "insect bite",
    
    # Other Common Conditions
    "sore throat", "throat pain", "hoarse voice", "laryngitis",
    "toothache", "dental pain", "mouth pain", "canker sore",
    "earache", "ear pain", "vertigo", "dizziness", "mild dizziness",
    "anxiety", "stress", "mild anxiety", "nervousness",
    "menstrual cramps", "period pain", "pms symptoms",
}

def has_red_flag(texts: list[str]) -> bool:
    corpus = " ".join((t or "").lower() for t in texts)
    return any(flag in corpus for flag in RED_FLAGS)