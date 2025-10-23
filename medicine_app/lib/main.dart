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
      title: 'AbsorpGen AI',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: HomePage(),
    );
  }
}

// ===== PAGE 1: HOME PAGE =====
class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<Map<String, String>> medicationHistory = [
    {'name': 'Ibuprofen', 'dose': '400 mg'},
    {'name': 'Ibuprofen', 'dose': '400 mg'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome header
              Text(
                'Welcome',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 40),
              
              // Past History Section
              Text(
                'Past History',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 16),
              
              // Medication history list
              Expanded(
                child: ListView.builder(
                  itemCount: medicationHistory.length,
                  itemBuilder: (context, index) {
                    return Container(
                      margin: EdgeInsets.only(bottom: 12),
                      padding: EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            medicationHistory[index]['name']!,
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                          ),
                          Text(
                            medicationHistory[index]['dose']!,
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              
              SizedBox(height: 20),
              
              // Let AI Select Button
              Center(
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => MedicineForm()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.grey[300],
                    foregroundColor: Colors.black,
                    padding: EdgeInsets.symmetric(horizontal: 48, vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    'Let AI Select',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                  ),
                ),
              ),
              
              SizedBox(height: 20),
            ],
          ),
        ),
      ),
      
      // Bottom Navigation Bar
      bottomNavigationBar: Container(
        height: 70,
        decoration: BoxDecoration(
          color: Colors.teal[700],
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            IconButton(
              icon: Icon(Icons.home, color: Colors.white, size: 32),
              onPressed: () {},
            ),
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.black,
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.add, color: Colors.white, size: 32),
            ),
            IconButton(
              icon: Icon(Icons.settings, color: Colors.white, size: 32),
              onPressed: () {},
            ),
          ],
        ),
      ),
    );
  }
}

// ===== PAGE 2: MEDICINE FORM (DETAILS) =====
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
  
  // API config
  String _apiBaseUrl = 'http://127.0.0.1:5000';
  
  // Loading state
  bool _isLoading = false;
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

    if (_selectedSymptoms.isEmpty) {
      setState(() {
        _error = 'Please select at least one symptom';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final Map<String, dynamic> payload = {
        'symptoms': _selectedSymptoms,
        'allergies': _selectedAllergies,
        'conditions': _selectedConditions,
      };
      
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
          _isLoading = false;
        });
        
        // Navigate to results page
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultsPage(recommendation: data),
          ),
        );
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal[700],
      appBar: AppBar(
        title: Text('Details', style: TextStyle(color: Colors.white, fontSize: 24)),
        backgroundColor: Colors.teal[700],
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(30),
            topRight: Radius.circular(30),
          ),
        ),
        child: SingleChildScrollView(
          controller: _scrollController,
          padding: EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(height: 10),
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
                SizedBox(height: 100),
              ],
            ),
          ),
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
                      return null;
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
                      return null;
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
                      return null;
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
                  selectedColor: Colors.teal[100],
                  checkmarkColor: Colors.teal[800],
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
                    activeColor: Colors.teal[700],
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
            Text('Previous Medicine Taken', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Any recent medications or timing:', style: TextStyle(color: Colors.grey[600])),
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
        backgroundColor: Colors.teal[700],
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Text(
        _isLoading ? 'Getting Recommendation...' : 'Run AbsorpGen AI',
        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return Padding(
      padding: EdgeInsets.all(24),
      child: Column(
        children: [
          CircularProgressIndicator(color: Colors.teal[700]),
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
}

// ===== PAGE 3: RESULTS PAGE =====
class ResultsPage extends StatelessWidget {
  final Map<String, dynamic> recommendation;

  ResultsPage({required this.recommendation});

  @override
  Widget build(BuildContext context) {
    // Check if triage alert
    if (recommendation.containsKey('triage_alert')) {
      return Scaffold(
        backgroundColor: Colors.teal[700],
        appBar: AppBar(
          title: Text('Results', style: TextStyle(color: Colors.white, fontSize: 24)),
          backgroundColor: Colors.teal[700],
          elevation: 0,
          leading: IconButton(
            icon: Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(30),
              topRight: Radius.circular(30),
            ),
          ),
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.medical_services, color: Colors.red[600], size: 64),
                SizedBox(height: 24),
                Text(
                  recommendation['triage_alert'] ?? 'Medical Alert',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.red[800]),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 16),
                Text(
                  recommendation['message'] ?? 'Please seek medical attention.',
                  style: TextStyle(fontSize: 16, color: Colors.red[700]),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 32),
                ElevatedButton.icon(
                  onPressed: () => _showEmergencyOptions(context),
                  icon: Icon(Icons.phone),
                  label: Text('Emergency Contacts'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red[600],
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // Normal recommendation
    return Scaffold(
      backgroundColor: Colors.teal[700],
      appBar: AppBar(
        title: Text('Results', style: TextStyle(color: Colors.white, fontSize: 24)),
        backgroundColor: Colors.teal[700],
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(30),
            topRight: Radius.circular(30),
          ),
        ),
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: 10),
              _buildDosageCard(),
              SizedBox(height: 16),
              _buildSafetyInfo(),
              if (recommendation['timing_advice'] != null) ...[
                SizedBox(height: 16),
                _buildTimingAdvice(),
              ],
              if (recommendation['ai_pharmacist'] != null) ...[
                SizedBox(height: 16),
                _buildAIRecommendation(),
              ],
              SizedBox(height: 16),
              _buildDisclaimer(),
              SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDosageCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Dosage Recommendation',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  recommendation['drug_name']?.split('(')[0].trim() ?? 'Unknown',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                ),
                Text(
                  recommendation['dosage'] ?? 'See label',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Frequency',
                  style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                ),
                Text(
                  recommendation['frequency'] ?? 'As needed',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSafetyInfo() {
    final safety = recommendation['safety_validation'];
    final sideEffects = recommendation['side_effects'];
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  safety?['is_safe'] == true ? Icons.check_circle : Icons.warning,
                  color: safety?['is_safe'] == true ? Colors.green[600] : Colors.orange[600],
                  size: 24,
                ),
                SizedBox(width: 8),
                Text('Safety Information', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            if (safety != null) ...[
              SizedBox(height: 12),
              Text(safety['warning'] ?? 'Dose validated and safe', style: TextStyle(fontSize: 14)),
              if (safety['dose_reduced'] == true) ...[
                SizedBox(height: 8),
                Text('✓ Dose adjusted for your safety', 
                  style: TextStyle(fontSize: 12, color: Colors.green[700], fontWeight: FontWeight.w500)),
              ],
            ],
            if (sideEffects != null) ...[
              SizedBox(height: 16),
              Text('Possible Side Effects:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              SizedBox(height: 4),
              Text(sideEffects, style: TextStyle(fontSize: 13, color: Colors.grey[700])),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTimingAdvice() {
    return Card(
      color: Colors.amber[50],
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.access_time, color: Colors.amber[700], size: 24),
                SizedBox(width: 8),
                Text('Timing Advice', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            SizedBox(height: 12),
            Text(recommendation['timing_advice'], style: TextStyle(fontSize: 14)),
          ],
        ),
      ),
    );
  }

  Widget _buildAIRecommendation() {
    final aiRec = recommendation['ai_pharmacist'];
    final medication = aiRec?['medication_selected'];
    final education = aiRec?['patient_education'];
    
    return Card(
      color: Colors.purple[50],
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.psychology, color: Colors.purple[600], size: 24),
                SizedBox(width: 8),
                Text('AI Pharmacist Insights', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            if (medication?['reasoning'] != null) ...[
              SizedBox(height: 12),
              Text('Selection Reasoning:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              SizedBox(height: 4),
              Text(medication['reasoning'], style: TextStyle(fontSize: 13, color: Colors.grey[700])),
            ],
            if (education?['key_points'] != null) ...[
              SizedBox(height: 16),
              Text('Key Points:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              SizedBox(height: 8),
              ...List<Widget>.from(education['key_points'].map<Widget>((point) => 
                Padding(
                  padding: EdgeInsets.only(top: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('• ', style: TextStyle(color: Colors.purple[600], fontSize: 16)),
                      Expanded(child: Text(point, style: TextStyle(fontSize: 13))),
                    ],
                  ),
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDisclaimer() {
    return Card(
      color: Colors.grey[100],
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.info_outline, color: Colors.grey[600], size: 18),
                SizedBox(width: 8),
                Text('Medical Disclaimer', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
            SizedBox(height: 8),
            Text(
              recommendation['medical_disclaimer'] ?? 'This is not a substitute for professional medical advice.',
              style: TextStyle(fontSize: 11, color: Colors.grey[700]),
            ),
          ],
        ),
      ),
    );
  }

  static void _showEmergencyOptions(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Emergency Contacts'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🚨 Emergency: 911'),
            SizedBox(height: 8),
            Text('☎️ Poison Control: 1-800-222-1222'),
            SizedBox(height: 8),
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