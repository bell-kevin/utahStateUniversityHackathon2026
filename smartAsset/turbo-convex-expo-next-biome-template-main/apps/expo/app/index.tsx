import { Link } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Expo + Next + Convex</Text>
      <Text style={styles.subtitle}>
        Starter template wired for Turborepo & Biome.
      </Text>
      <Link href="/about" style={styles.link}>
        Go to About →
      </Link>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    gap: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
  },
  subtitle: {
    fontSize: 16,
    textAlign: "center",
    color: "#475569",
  },
  link: {
    fontSize: 16,
    color: "#2563eb",
    fontWeight: "600",
  },
});
