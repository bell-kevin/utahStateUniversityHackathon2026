"use client";

import { useMemo, useState } from "react";
import {
  ASSETS,
  USERS,
  evaluateInspection,
  recommendedMaintainer,
  roleActions,
  type AiResponse,
} from "@/lib/smartAsset";

export default function Home() {
  const [activeAssetId, setActiveAssetId] = useState(ASSETS[0]?.id ?? "");
  const [activeUserId, setActiveUserId] = useState(USERS[0]?.id ?? "");
  const [note, setNote] = useState("");
  const [assessment, setAssessment] = useState<AiResponse | null>(null);

  const asset = useMemo(
    () => ASSETS.find((item) => item.id === activeAssetId) ?? ASSETS[0],
    [activeAssetId]
  );
  const user = useMemo(
    () => USERS.find((item) => item.id === activeUserId) ?? USERS[0],
    [activeUserId]
  );

  if (!asset || !user) {
    return <main className="wrapper">Unable to load smart asset data.</main>;
  }

  const actions = roleActions(user.role);
  const maintainer = recommendedMaintainer(asset);

  async function runAssessment() {
    if (!note.trim()) {
      return;
    }

    const response = await fetch("/api/assess", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ note }),
    });

    if (response.ok) {
      const payload = (await response.json()) as AiResponse;
      setAssessment(payload);
      return;
    }

    setAssessment(evaluateInspection(note));
  }

  return (
    <main className="wrapper">
      <section className="hero">
        <h1>Smart Asset Intelligence OS</h1>
        <p>
          Hackathon MVP for NFC-tagged university assets. Scan an asset, collect
          issue context, and use AI to prioritize risk and assign maintenance.
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>1) Simulate NFC Asset Scan</h2>
          <label>
            Active user
            <select value={activeUserId} onChange={(e) => setActiveUserId(e.target.value)}>
              {USERS.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.name} ({candidate.role})
                </option>
              ))}
            </select>
          </label>
          <label>
            Asset tag
            <select value={activeAssetId} onChange={(e) => setActiveAssetId(e.target.value)}>
              {ASSETS.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.tagId} — {candidate.name}
                </option>
              ))}
            </select>
          </label>

          <div className="pillRow">
            {actions.map((action) => (
              <span key={action} className="pill">
                {action}
              </span>
            ))}
          </div>

          <ul>
            <li>
              <strong>Location:</strong> {asset.location}
            </li>
            <li>
              <strong>Current Risk:</strong> {asset.riskScore}/100 ({asset.status})
            </li>
            <li>
              <strong>Maintainer:</strong> {maintainer?.name ?? "Unassigned"}
            </li>
          </ul>
        </article>

        <article className="card">
          <h2>2) Report Problem / Inspect Item</h2>
          <textarea
            rows={7}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Example: Noticed corrosion and a small leak near the pump housing..."
          />
          <button type="button" onClick={runAssessment}>
            Analyze with AI inspection layer
          </button>
          <p className="hint">
            The payload mirrors your requested structure and can feed Convex
            mutations to update asset risk and create work orders.
          </p>
        </article>
      </section>

      {assessment ? (
        <section className="card">
          <h2>3) AI Risk Output</h2>
          <pre>{JSON.stringify(assessment, null, 2)}</pre>
        </section>
      ) : null}
    </main>
  );
}
