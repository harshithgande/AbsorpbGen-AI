import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import PatientFormScreen from './screens/PatientFormScreen';
import ResultsScreen from './screens/ResultsScreen';
import TriageScreen from './screens/TriageScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Form">
        <Stack.Screen name="Form" component={PatientFormScreen} />
        <Stack.Screen name="Results" component={ResultsScreen} />
        <Stack.Screen name="Triage" component={TriageScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
