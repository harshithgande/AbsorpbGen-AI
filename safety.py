RED_FLAGS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "severe pain",
    "numbness",
    "weakness on one side",
    "confusion",
    "fainting",
    "blood in vomit",
    "black stools",
    "suicidal thoughts",
    "stroke",
    "heart attack",
    "cancer",
}

CASUAL_HINTS = {
    "mild headache",
    "headache",
    "runny nose",
    "sore throat",
    "mild fever",
    "muscle aches",
    "knee pain",
    "joint pain",
    "allergies",
    "heartburn",
    "cough",
}

def has_red_flag(texts: list[str]) -> bool:
    corpus = " ".join((t or "").lower() for t in texts)
    return any(flag in corpus for flag in RED_FLAGS)