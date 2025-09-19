import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MedicineApp());
}

class MedicineApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AbsorpGen AI - Medicine Dosage',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MedicineForm(),
    );
  }
}

class MedicineForm extends StatefulWidget {
  @override
  _MedicineFormState createState() => _MedicineFormState();
}

class _MedicineFormState extends State<MedicineForm> {
  final _formKey = GlobalKey<FormState>();
  final _scrollController = ScrollController();
  
  // Form controllers
  final TextEditingController _ageController = TextEditingController();
  final TextEditingController _heightController = TextEditingController();
  final TextEditingController _weightController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();
  
  // Form data
  String _sex = 'M';
  int _painLevel = 5;
  List<String> _selectedSymptoms = [];
  List<String> _selectedAllergies = [];
  List<String> _selectedConditions = [];
  
  // API config - CHANGE THIS TO YOUR BACKEND URL
  String _apiBaseUrl = 'http://127.0.0.1:5000';
  
  // Loading state
  bool _isLoading = false;
  Map<String, dynamic>? _recommendation;
  String? _error;

  // Available options
  final List<String> _symptoms = [
    'fever', 'headache', 'pain', 'sore throat', 'toothache',
    'muscle aches', 'joint pain', 'sprain', 'back pain', 'inflammation',
    'cough', 'dry cough', 'chest congestion', 'productive cough', 'mucus',
    'allergies', 'sneezing', 'runny nose', 'itchy eyes',
    'heartburn', 'acid reflux', 'indigestion', 'sour stomach',
    'nausea', 'motion sickness', 'vertigo'
  ];

  final List<String> _allergies = [
    'acetaminophen', 'ibuprofen', 'aspirin', 'penicillin',
    'sulfa drugs', 'latex', 'shellfish', 'nuts', 'dairy', 'eggs'
  ];

  final List<String> _conditions = [
    'diabetes', 'hypertension', 'heart disease', 'kidney disease',
    'liver disease', 'ulcer', 'gi bleed', 'asthma', 'copd',
    'depression', 'anxiety', 'pregnancy', 'breastfeeding'
  ];

  @override
  void dispose() {
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _notesController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Check that at least one symptom is selected (required by your backend)
    if (_selectedSymptoms.isEmpty) {
      setState(() {
        _error = 'Please select at least one symptom';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _recommendation = null;
    });

    try {
      // Build payload matching your Pydantic UserRequest model
      final Map<String, dynamic> payload = {
        'symptoms': _selectedSymptoms, // Required field
        'allergies': _selectedAllergies, // Optional, defaults to []
        'conditions': _selectedConditions, // Optional, defaults to []
      };
      
      // Add optional fields only if provided
      if (_ageController.text.isNotEmpty) {
        payload['age'] = int.parse(_ageController.text);
      }
      if (_heightController.text.isNotEmpty) {
        payload['height_cm'] = double.parse(_heightController.text);
      }
      if (_weightController.text.isNotEmpty) {
        payload['weight_kg'] = double.parse(_weightController.text);
      }
      if (_sex.isNotEmpty) {
        payload['sex'] = _sex;
      }
      if (_painLevel > 0) {
        payload['pain_level'] = _painLevel;
      }
      if (_notesController.text.isNotEmpty) {
        payload['notes'] = _notesController.text;
      }

      final response = await http.post(
        Uri.parse('$_apiBaseUrl/recommend'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(payload),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _recommendation = data;
          _isLoading = false;
        });
        _scrollToRecommendation();
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _error = 'Failed to get recommendation: $e';
        _isLoading = false;
      });
    }
  }

  void _scrollToRecommendation() {
    Future.delayed(Duration(milliseconds: 100), () {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: Duration(milliseconds: 500),
        curve: Curves.easeInOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('AbsorpGen AI'),
        backgroundColor: Colors.blue[600],
        elevation: 2,
      ),
      body: SingleChildScrollView(
        controller: _scrollController,
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(),
              SizedBox(height: 24),
              _buildBasicInfoSection(),
              SizedBox(height: 20),
              _buildSymptomsSection(),
              SizedBox(height: 20),
              _buildAllergiesSection(),
              SizedBox(height: 20),
              _buildConditionsSection(),
              SizedBox(height: 20),
              _buildPainLevelSection(),
              SizedBox(height: 20),
              _buildNotesSection(),
              SizedBox(height: 24),
              _buildSubmitButton(),
              if (_isLoading) _buildLoadingIndicator(),
              if (_error != null) _buildErrorCard(),
              if (_recommendation != null) _buildRecommendationCard(),
              SizedBox(height: 100), // Extra space at bottom
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(Icons.medication, size: 48, color: Colors.blue[600]),
            SizedBox(height: 8),
            Text(
              'AI Medicine Dosage Assistant',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 4),
            Text(
              'Get personalized OTC medication recommendations',
              style: TextStyle(color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBasicInfoSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Basic Information', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text('Optional: Helps improve dosage accuracy', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _ageController,
                    decoration: InputDecoration(
                      labelText: 'Age',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.cake),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value != null && value.isNotEmpty) {
                        final age = int.tryParse(value);
                        if (age == null || age < 0 || age > 120) return 'Invalid age (0-120)';
                      }
                      return null; // Optional field
                    },
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _sex,
                    decoration: InputDecoration(
                      labelText: 'Sex',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.person),
                    ),
                    items: [
                      DropdownMenuItem(value: 'M', child: Text('Male')),
                      DropdownMenuItem(value: 'F', child: Text('Female')),
                    ],
                    onChanged: (value) => setState(() => _sex = value!),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _heightController,
                    decoration: InputDecoration(
                      labelText: 'Height (cm)',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.height),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value != null && value.isNotEmpty) {
                        final height = double.tryParse(value);
                        if (height == null || height < 30 || height > 250) return 'Invalid height (30-250cm)';
                      }
                      return null; // Optional field
                    },
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _weightController,
                    decoration: InputDecoration(
                      labelText: 'Weight (kg)',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.monitor_weight),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value != null && value.isNotEmpty) {
                        final weight = double.tryParse(value);
                        if (weight == null || weight < 1 || weight > 400) return 'Invalid weight (1-400kg)';
                      }
                      return null; // Optional field
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSymptomsSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Symptoms', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Select all symptoms you are experiencing:', style: TextStyle(color: Colors.grey[600])),
            SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: _symptoms.map((symptom) {
                final isSelected = _selectedSymptoms.contains(symptom);
                return FilterChip(
                  label: Text(symptom),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedSymptoms.add(symptom);
                      } else {
                        _selectedSymptoms.remove(symptom);
                      }
                    });
                  },
                  selectedColor: Colors.blue[100],
                  checkmarkColor: Colors.blue[800],
                );
              }).toList(),
            ),
            if (_selectedSymptoms.isEmpty)
              Container(
                margin: EdgeInsets.only(top: 8),
                padding: EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  border: Border.all(color: Colors.red[300]!),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text('⚠️ Please select at least one symptom to continue', 
                  style: TextStyle(color: Colors.red[700], fontSize: 12, fontWeight: FontWeight.w500)),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAllergiesSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Allergies', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Select any known allergies:', style: TextStyle(color: Colors.grey[600])),
            SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: _allergies.map((allergy) {
                final isSelected = _selectedAllergies.contains(allergy);
                return FilterChip(
                  label: Text(allergy),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedAllergies.add(allergy);
                      } else {
                        _selectedAllergies.remove(allergy);
                      }
                    });
                  },
                  selectedColor: Colors.red[100],
                  checkmarkColor: Colors.red[800],
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConditionsSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Medical Conditions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Select any existing medical conditions:', style: TextStyle(color: Colors.grey[600])),
            SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: _conditions.map((condition) {
                final isSelected = _selectedConditions.contains(condition);
                return FilterChip(
                  label: Text(condition),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedConditions.add(condition);
                      } else {
                        _selectedConditions.remove(condition);
                      }
                    });
                  },
                  selectedColor: Colors.orange[100],
                  checkmarkColor: Colors.orange[800],
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPainLevelSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Pain Level', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Rate your pain from 1 (mild) to 10 (severe):', style: TextStyle(color: Colors.grey[600])),
            SizedBox(height: 16),
            Row(
              children: [
                Text('1', style: TextStyle(fontSize: 16)),
                Expanded(
                  child: Slider(
                    value: _painLevel.toDouble(),
                    min: 1,
                    max: 10,
                    divisions: 9,
                    label: _painLevel.toString(),
                    onChanged: (value) {
                      setState(() {
                        _painLevel = value.round();
                      });
                    },
                  ),
                ),
                Text('10', style: TextStyle(fontSize: 16)),
              ],
            ),
            Center(
              child: Text(
                'Current: $_painLevel ${_getPainDescription(_painLevel)}',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getPainDescription(int level) {
    if (level <= 2) return '(Mild)';
    if (level <= 5) return '(Moderate)';
    if (level <= 7) return '(Severe)';
    return '(Very Severe)';
  }

  Widget _buildNotesSection() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Additional Notes', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Any recent medications, timing, or other details:', style: TextStyle(color: Colors.grey[600])),
            SizedBox(height: 12),
            TextFormField(
              controller: _notesController,
              decoration: InputDecoration(
                hintText: 'e.g., "Took ibuprofen 2 hours ago but no relief"',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.note_add),
              ),
              maxLines: 3,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      onPressed: _selectedSymptoms.isEmpty || _isLoading ? null : _submitForm,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: Text(
        _isLoading ? 'Getting Recommendation...' : 'Get Medicine Recommendation',
        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return Padding(
      padding: EdgeInsets.all(24),
      child: Column(
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('AI Pharmacist is analyzing your symptoms...', style: TextStyle(color: Colors.grey[600])),
        ],
      ),
    );
  }

  Widget _buildErrorCard() {
    return Card(
      color: Colors.red[50],
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(Icons.error, color: Colors.red[600], size: 48),
            SizedBox(height: 8),
            Text('Error', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red[800])),
            SizedBox(height: 8),
            Text(_error!, style: TextStyle(color: Colors.red[700])),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => setState(() => _error = null),
              child: Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationCard() {
    final rec = _recommendation!;
    
    // Check if this is a triage alert
    if (rec.containsKey('triage_alert')) {
      return Card(
        color: Colors.red[50],
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(Icons.medical_services, color: Colors.red[600], size: 48),
              SizedBox(height: 16),
              Text(
                rec['triage_alert'] ?? 'Medical Alert',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.red[800]),
              ),
              SizedBox(height: 12),
              Text(
                rec['message'] ?? 'Please seek medical attention.',
                style: TextStyle(fontSize: 16, color: Colors.red[700]),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => _showEmergencyOptions(context),
                icon: Icon(Icons.phone),
                label: Text('Emergency Contacts'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red[600], foregroundColor: Colors.white),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      color: Colors.green[50],
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildMedicationHeader(rec),
            SizedBox(height: 16),
            _buildDosageInfo(rec),
            SizedBox(height: 16),
            _buildSafetyInfo(rec),
            if (rec['timing_advice'] != null) ...[
              SizedBox(height: 16),
              _buildTimingAdvice(rec['timing_advice']),
            ],
            if (rec['ai_pharmacist'] != null) ...[
              SizedBox(height: 16),
              _buildAIRecommendation(rec['ai_pharmacist']),
            ],
            SizedBox(height: 16),
            _buildDisclaimer(rec['medical_disclaimer']),
          ],
        ),
      ),
    );
  }

  Widget _buildMedicationHeader(Map<String, dynamic> rec) {
    return Row(
      children: [
        Icon(Icons.medication, color: Colors.green[600], size: 32),
        SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Recommended Medication',
                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              ),
              Text(
                rec['drug_name'] ?? 'Unknown',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green[800]),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDosageInfo(Map<String, dynamic> rec) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Dosage Instructions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.local_pharmacy, color: Colors.blue[600], size: 20),
              SizedBox(width: 8),
              Expanded(child: Text(rec['dosage'] ?? 'See label', style: TextStyle(fontSize: 16))),
            ],
          ),
          SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.schedule, color: Colors.blue[600], size: 20),
              SizedBox(width: 8),
              Expanded(child: Text(rec['frequency'] ?? 'As needed', style: TextStyle(fontSize: 16))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSafetyInfo(Map<String, dynamic> rec) {
    final safety = rec['safety_validation'];
    final sideEffects = rec['side_effects'];
    
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: safety?['is_safe'] == true ? Colors.green[50] : Colors.orange[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: safety?['is_safe'] == true ? Colors.green[200]! : Colors.orange[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                safety?['is_safe'] == true ? Icons.check_circle : Icons.warning,
                color: safety?['is_safe'] == true ? Colors.green[600] : Colors.orange[600],
                size: 20,
              ),
              SizedBox(width: 8),
              Text('Safety Information', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          if (safety != null) ...[
            SizedBox(height: 8),
            Text(safety['warning'] ?? 'Dose validated and safe', style: TextStyle(fontSize: 14)),
            if (safety['dose_reduced'] == true) ...[
              SizedBox(height: 4),
              Text('✓ Dose adjusted for your safety', 
                style: TextStyle(fontSize: 12, color: Colors.green[700], fontWeight: FontWeight.w500)),
            ],
          ],
          if (sideEffects != null) ...[
            SizedBox(height: 12),
            Text('Possible Side Effects:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            SizedBox(height: 4),
            Text(sideEffects, style: TextStyle(fontSize: 13, color: Colors.grey[700])),
          ],
        ],
      ),
    );
  }

  Widget _buildTimingAdvice(String advice) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amber[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.access_time, color: Colors.amber[600], size: 20),
              SizedBox(width: 8),
              Text('Timing Advice', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          SizedBox(height: 8),
          Text(advice, style: TextStyle(fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildAIRecommendation(Map<String, dynamic> aiRec) {
    final medication = aiRec['medication_selected'];
    final education = aiRec['patient_education'];
    
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.purple[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: Colors.purple[600], size: 20),
              SizedBox(width: 8),
              Text('AI Pharmacist Insights', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          if (medication?['reasoning'] != null) ...[
            SizedBox(height: 8),
            Text('Selection Reasoning:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            Text(medication['reasoning'], style: TextStyle(fontSize: 13, color: Colors.grey[700])),
          ],
          if (education?['key_points'] != null) ...[
            SizedBox(height: 12),
            Text('Key Points:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            ...List<Widget>.from(education['key_points'].map<Widget>((point) => 
              Padding(
                padding: EdgeInsets.only(top: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• ', style: TextStyle(color: Colors.purple[600])),
                    Expanded(child: Text(point, style: TextStyle(fontSize: 13))),
                  ],
                ),
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _buildDisclaimer(String? disclaimer) {
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.info_outline, color: Colors.grey[600], size: 16),
              SizedBox(width: 8),
              Text('Medical Disclaimer', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
          SizedBox(height: 4),
          Text(
            disclaimer ?? 'This is not a substitute for professional medical advice.',
            style: TextStyle(fontSize: 11, color: Colors.grey[700]),
          ),
        ],
      ),
    );
  }

  void _showEmergencyOptions(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Emergency Contacts'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🚨 Emergency: 911'),
            Text('☎️ Poison Control: 1-800-222-1222'),
            Text('🏥 Urgent Care: Find nearest location'),
            SizedBox(height: 16),
            Text('Please seek immediate medical attention for your symptoms.',
              style: TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }
}