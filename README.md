# AbsorpGen AI - AI Pharmacist System

AbsorpGen AI is an **AI-powered pharmacist system** that provides intelligent medication recommendations with comprehensive safety validation. The system combines deterministic AI decision-making with multi-layer safety protocols to ensure patient safety.

## 🚀 **Key Features**

- **AI Pharmacist**: Intelligent medication selection and dosing
- **Multi-Layer Safety**: Triple-validation system with AI override capability
- **Context-Aware Routing**: Considers recent medications, pain level, and conditions
- **Deterministic Behavior**: Consistent outputs for same inputs (temperature=0)
- **Comprehensive Fallbacks**: Rule-based system when AI fails
- **Patient Education**: Personalized warnings and guidance

## 🏗️ **Project Structure**

```
AbsorpGen_AI/
├── app_simple.py           # Main Flask application with AI pharmacist
├── openai_client.py        # AI pharmacist client and safety validation
├── validators.py           # Pydantic models for request validation
├── safety.py              # Red-flag detection and safety rules
├── dosing_rules.py        # Conservative dosing calculations
├── otc_catalog.py         # OTC medication database
├── public/
│   └── index.html         # Frontend SPA
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🛠️ **Setup**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key:
# OPENAI_API_KEY=sk-your_actual_key_here
# OPENAI_MODEL=gpt-4o-mini
```

### 3. **Run the Application**
```bash
python app_simple.py
```

### 4. **Access the Application**
Open http://localhost:5000/ in your browser

## 🧠 **How It Works**

### **1. Patient Input**
- Demographics (age, sex, height, weight)
- Symptoms and conditions
- Pain level (1-10 scale)
- Free-text notes (e.g., "I took Tylenol 2 hours ago and it didn't work")

### **2. AI Analysis**
- **Medication Selection**: AI chooses optimal OTC medication
- **Dosing Calculation**: Personalized dosing based on patient factors
- **Safety Validation**: Multiple safety checks and constraints
- **Patient Education**: Comprehensive warnings and guidance

### **3. Safety Validation**
- **Age-based caps**: Conservative dosing for minors
- **Condition-based adjustments**: Reduced doses for kidney/liver issues
- **Hard safety limits**: Never exceed medical safety caps
- **Alternative suggestions**: Safer options when needed

### **4. Response Generation**
- Clean medication cards with dosing instructions
- Safety warnings and patient education
- Alternative medication suggestions
- Timing advice for recent medications

## 📊 **API Endpoints**

### **POST /recommend**
Main recommendation endpoint that processes patient requests.

**Request:**
```json
{
  "age": 35,
  "sex": "M",
  "height_cm": 170,
  "weight_kg": 70,
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
  "safety_validation": {
    "is_safe": true,
    "warning": "Dose validated and safe",
    "dose_reduced": false
  },
  "ai_pharmacist": {
    "medication_selected": {
      "reasoning": "Best choice for your pain and inflammation",
      "safety_notes": "Take with food to minimize stomach irritation"
    },
    "patient_education": {
      "key_points": ["Take with food", "Stay hydrated"],
      "warnings": ["Avoid if you have ulcers"],
      "when_to_seek_help": "If pain persists beyond 3 days"
    }
  }
}
```

### **GET /health**
Health check endpoint with AI pharmacist status.
```json
{
  "ok": true,
  "ai_pharmacist_ok": true
}
```

## 🔒 **Safety Features**

- **Multi-Layer Validation**: AI → Safety → Fallback
- **Hard Dosing Caps**: Never exceed medical safety limits
- **Context-Aware Routing**: Avoid recently ineffective medications
- **Condition-Based Adjustments**: Reduced doses for high-risk patients
- **Alternative Suggestions**: Safer options when primary choice has concerns

## 🎯 **Patentable Innovations**

1. **Multi-Layer AI Safety Architecture**: AI constrained by safety validation layers
2. **Context-Aware Medication Routing**: Intelligent routing based on patient history
3. **Deterministic Medical AI**: Consistent outputs with safety validation
4. **Pain-Adaptive Dosing**: Medication selection based on pain level
5. **Notes-Aware History**: Natural language parsing of medication history

## 🚨 **Important Disclaimers**

- **Proof of Concept**: This is a demonstration system
- **Not Medical Advice**: Always consult qualified healthcare professionals
- **Educational Purpose**: For research and development purposes only
- **Safety First**: Multiple validation layers ensure patient safety

## 🔮 **Future Enhancements**

- Integration with external drug databases (OpenFDA, RxNorm)
- Machine learning models for improved dosing accuracy
- Multi-language support
- Mobile application
- Electronic health record integration

## 📝 **License**

This project is for educational and research purposes. Always consult qualified medical professionals for actual medical advice.

---

**AbsorpGen AI**: Where AI meets medical safety for intelligent medication recommendations. 