# AbsorpGen AI - Safety-First OTC Helper

AbsorpGen AI is a **safety-first OTC helper** that provides personalized medication recommendations with intelligent dosing guidance. The system combines deterministic safety rules with OpenAI-powered dosing optimization while maintaining strict security practices.

## 🚀 Features

- **Red-flag triage** for dangerous symptoms
- **Intelligent OTC selection** based on symptoms, allergies, and conditions
- **OpenAI-powered dosing** with safety caps and fallbacks
- **Notes-aware routing** that considers recent medication history
- **Deterministic behavior** for consistent recommendations
- **Server-side security** - API keys never exposed to the browser

## 🏗️ Architecture

- **Backend**: Flask with OpenAI integration
- **Frontend**: Single-page application served from Flask
- **AI**: OpenAI GPT-4o-mini for intelligent dosing
- **Safety**: Rule-based fallbacks and hard caps
- **Security**: Environment-based API key management

## 📁 Project Structure

```
AbsorpGen_AI/
├── app.py                 # Main Flask application with OpenAI integration
├── openai_client.py       # OpenAI client for dosing requests
├── validators.py          # Pydantic models for request validation
├── safety.py             # Red-flag detection logic
├── dosing_rules.py       # Conservative dosing calculations
├── otc_catalog.py        # OTC medication database
├── public/
│   └── index.html        # Frontend SPA
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
└── .gitignore            # Git ignore rules
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your OpenAI API key:

```env
OPENAI_API_KEY=sk-your_actual_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run the Application

```bash
python app.py
```

Open your browser to: http://localhost:5000/

## 🔒 Security Features

- **API keys stored server-side only** in `.env` file
- **Never exposed to browser** - all AI calls happen on the server
- **Environment-based configuration** for production deployment
- **CORS protection** with explicit origin allowlisting

## 🧠 How It Works

### 1. User Input
Users provide:
- Demographics (age, sex, height, weight)
- Symptoms and conditions
- Pain level (1-10)
- Free-text notes (e.g., "I took Tylenol 2 hours ago and it didn't work")

### 2. Safety Triage
- Red-flag detection for dangerous symptoms
- Automatic referral to medical care when needed

### 3. OTC Selection
- Deterministic selection based on symptom matching
- Avoids contraindicated medications
- Considers recent medication history from notes

### 4. AI-Powered Dosing
- OpenAI generates personalized dosing instructions
- Respects safety caps and medical guidelines
- Falls back to rule-based dosing if AI fails

### 5. Response Generation
- Clean, actionable medication cards
- Timing advice for recent medications
- Side effects and safety information

## 📊 API Endpoints

### POST /recommend
Main recommendation endpoint that processes user requests and returns medication guidance.

**Request:**
```json
{
  "age": 35,
  "sex": "F",
  "height_cm": 165,
  "weight_kg": 60,
  "symptoms": ["headache", "fever"],
  "allergies": ["penicillin"],
  "conditions": ["hypertension"],
  "pain_level": 7,
  "notes": "I took Tylenol 2 hours ago and it didn't help"
}
```

**Response:**
```json
{
  "drug_name": "Advil (Ibuprofen)",
  "dosage": "2 tablets (200mg each)",
  "frequency": "every 6–8 hours with food as needed",
  "side_effects": "May cause stomach irritation...",
  "timing_advice": "You reported taking Tylenol about 2 hours ago...",
  "dose_basis": {
    "suggested_single_dose_mg": 400,
    "single_dose_cap_mg": 800,
    "llm_used": true,
    "policy": "LLM dosing with BSA + age/condition reductions + hard OTC single-dose cap fallback"
  }
}
```

### GET /health
Health check endpoint that includes LLM connectivity status.

```json
{
  "ok": true,
  "llm_ok": true
}
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o-mini)

### CORS Configuration

The application serves the frontend from the same origin (port 5000) to avoid CORS issues. If you need to serve from a different port, update the `ALLOWED_ORIGINS` in `app.py`.

## 🧪 Testing

The application includes comprehensive error handling and fallbacks:

- **LLM failures** automatically fall back to rule-based dosing
- **API key issues** don't crash the application
- **Invalid responses** are caught and handled gracefully

## 🚨 Safety Features

- **Hard dosing caps** that cannot be exceeded
- **Age and condition-based reductions** for conservative dosing
- **Contraindication checking** against allergies and conditions
- **Recent medication awareness** to avoid over-dosing

## 🔮 Future Enhancements

- Integration with external drug databases (OpenFDA, RxNorm)
- Machine learning models for improved dosing accuracy
- Multi-language support
- Mobile application
- Electronic health record integration

## 📝 License

This project is for educational and research purposes. Always consult qualified medical professionals for actual medical advice.

## ⚠️ Disclaimer

**IMPORTANT**: AbsorpGen AI is a proof-of-concept and not a substitute for professional medical advice. Always consult a qualified clinician for diagnosis and treatment. 