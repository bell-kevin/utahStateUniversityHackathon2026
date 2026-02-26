import { Link } from "expo-router";
import { StyleSheet, Text, View } from "react-native";

export default function AboutScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>About This Template</Text>
      <Text style={styles.body}>
        This Expo app lives in a Turborepo alongside a Next.js web app and a
        Convex backend. Replace these screens with your own routes.
      </Text>
      <Link href="/" style={styles.link}>
        ← Back home
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    gap: 16,
    justifyContent: "center",
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
  },
  body: {
    fontSize: 16,
    lineHeight: 22,
    color: "#475569",
  },
  link: {
    fontSize: 16,
    color: "#2563eb",
    fontWeight: "600",
  },
});
