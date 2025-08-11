# AbsorpGen AI Backend

AbsorpGen AI is an intelligent backend for personalized drug recommendations, powered by FastAPI and Gemini AI.

## Features
- Accepts patient demographics and symptoms
- Calls Gemini AI for drug recommendations and pharmacokinetic predictions
- Designed for integration with mobile/web frontends

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## API Usage

### POST /recommend

Request JSON:
```json
{
  "age": 35,
  "weight": 70.5,
  "sex": "male",
  "height": 175.0,
  "symptoms": "headache, fever",
  "current_medications": "paracetamol"
}
```

Response JSON:
```json
{
  "recommendation": "...Gemini AI's response..."
}
```

## Notes
- The Gemini API key is currently hardcoded in `main.py`. For production, use environment variables.
- Future versions will integrate ML models and external drug databases (OpenFDA, RxNorm). 