import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD2H61xj9WRR6N0_w7D2xtVbvHc89Ng_Tw")
# CORS domains can be tightened later
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")

# Max safe single doses (mg)
MAX_DOSE_MG = {
    "acetaminophen": 1000,
    "ibuprofen": 800,
}