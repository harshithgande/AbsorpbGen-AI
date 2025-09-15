import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function TriageScreen({ route }) {
  const { message } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>⚠️ Triage Alert</Text>
      <Text style={styles.message}>{message}</Text>
      <Text style={styles.disclaimer}>
        Please seek medical attention. This app does not replace professional care.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, justifyContent: 'center', flex: 1 },
  title: { fontSize: 24, fontWeight: 'bold', color: 'red', marginBottom: 10 },
  message: { fontSize: 16, marginBottom: 20 },
  disclaimer: { fontSize: 12, color: '#666' },
});
