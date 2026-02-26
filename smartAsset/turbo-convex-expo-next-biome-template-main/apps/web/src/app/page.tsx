import Link from "next/link";

export default function Home() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "1.2rem",
        padding: "2rem",
      }}
    >
      <div style={{ textAlign: "center", maxWidth: 620 }}>
        <h1 style={{ fontSize: "2.4rem", margin: 0 }}>Next + Expo + Convex</h1>
        <p style={{ color: "#475569", marginTop: "0.6rem" }}>
          Minimal starter web app living in a pnpm/Turborepo workspace. Replace
          this page and add routes as needed.
        </p>
      </div>
      <div style={{ display: "flex", gap: "1rem" }}>
        <Link href="https://expo.dev" target="_blank" rel="noreferrer">
          Expo docs →
        </Link>
        <Link href="https://nextjs.org/docs" target="_blank" rel="noreferrer">
          Next.js docs →
        </Link>
        <Link href="https://docs.convex.dev" target="_blank" rel="noreferrer">
          Convex docs →
        </Link>
      </div>
    </main>
  );
}
