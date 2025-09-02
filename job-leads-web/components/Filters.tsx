"use client";
import { useState } from "react";
import { Filters as F } from "../lib/types";

export default function Filters({ value, onChange }: { value: F; onChange: (f: F) => void }) {
  const [local, setLocal] = useState<F>(value);

  function set<K extends keyof F>(k: K, v: F[K]) {
    const next = { ...local, [k]: v };
    setLocal(next);
    onChange(next);
  }

  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
      <input placeholder="Keywords" value={local.q || ""} onChange={(e) => set("q", e.target.value)} />
      <input placeholder="Source" value={local.source || ""} onChange={(e) => set("source", e.target.value)} />
      <input placeholder="Location" value={local.location || ""} onChange={(e) => set("location", e.target.value)} />
      <select value={local.status || ""} onChange={(e) => set("status", e.target.value)}>
        <option value="">Any status</option>
        <option>Saved</option>
        <option>Applied</option>
        <option>Interview</option>
        <option>Offer</option>
        <option>Rejected</option>
        <option>On hold</option>
      </select>
    </div>
  );
}

