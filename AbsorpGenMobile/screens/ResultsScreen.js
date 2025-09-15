import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

export default function ResultsScreen({ route }) {
  const { recommendation } = route.params;

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Recommended Medication</Text>
      <Text style={styles.label}>Drug:</Text>
      <Text>{recommendation.drug_name}</Text>
      <Text style={styles.label}>Dosage:</Text>
      <Text>{recommendation.dosage}</Text>
      <Text style={styles.label}>Frequency:</Text>
      <Text>{recommendation.frequency}</Text>
      <Text style={styles.label}>Side Effects:</Text>
      <Text>{recommendation.side_effects}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
  label: { marginTop: 10, fontWeight: 'bold' },
});
