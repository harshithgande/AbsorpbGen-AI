import React, { useState } from 'react';
import { View, Text, TextInput, Button, ScrollView, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';

export default function PatientFormScreen() {
  const navigation = useNavigation();
  const [form, setForm] = useState({
    age: '',
    sex: '',
    height_cm: '',
    weight_kg: '',
    symptoms: '',
    allergies: '',
    conditions: '',
    pain_level: '0',
    notes: '',
  });

  const handleChange = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async () => {
    const payload = {
      ...form,
      age: parseInt(form.age),
      height_cm: parseFloat(form.height_cm),
      weight_kg: parseFloat(form.weight_kg),
      pain_level: parseInt(form.pain_level),
      symptoms: form.symptoms.split(',').map(s => s.trim()),
      allergies: form.allergies.split(',').map(s => s.trim()),
      conditions: form.conditions.split(',').map(s => s.trim()),
    };

    try {
      const res = await fetch('http://localhost:5000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.triage_alert) {
        navigation.navigate('Triage', { message: data.message });
      } else {
        navigation.navigate('Results', { recommendation: data });
      }
    } catch (err) {
      console.error('Error:', err);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>AbsorpGen AI</Text>
      {['age', 'sex', 'height_cm', 'weight_kg', 'symptoms', 'allergies', 'conditions', 'pain_level', 'notes'].map(key => (
        <TextInput
          key={key}
          style={styles.input}
          placeholder={key.replace('_', ' ')}
          value={form[key]}
          onChangeText={text => handleChange(key, text)}
        />
      ))}
      <Button title="Get Recommendation" onPress={handleSubmit} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 10, borderRadius: 5 },
});
