import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function SignUpScreen({ navigation }) {
  return (
    <View style={styles.container}>
      {/* Title and tagline */}
      <Text style={styles.title}>AbsorpGen AI</Text>
      <Text style={styles.subtitle}>Smarter Dosages for you</Text>

      {/* Buttons */}
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('PatientForm')}
      >
        <Text style={styles.buttonText}>Get Started</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.button, styles.secondaryButton]}
        onPress={() => navigation.navigate('Login')}
      >
        <Text style={styles.buttonText}>Log In</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
    marginBottom: 15,
  },
  secondaryButton: {
    backgroundColor: '#444',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
});

