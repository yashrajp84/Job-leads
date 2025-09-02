"use client";
import { useState } from "react";
import { Job, Lead } from "../lib/types";

export default function LeadEditor({ job, onSave }: { job: Job; onSave: (fields: Partial<Lead>) => Promise<void>; }) {
  const lead = job.lead || { id: job.id, status: "Saved", score: 0, favourite: false } as Lead;
  const [status, setStatus] = useState(lead.status || "Saved");
  const [score, setScore] = useState(lead.score || 0);
  const [favourite, setFavourite] = useState(!!lead.favourite);
  const [notes, setNotes] = useState(lead.notes || "");
  const [nextAction, setNextAction] = useState(lead.next_action || "");
  const [nextActionDate, setNextActionDate] = useState(lead.next_action_date || "");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await onSave({ status, score, favourite, notes, next_action: nextAction, next_action_date: nextActionDate });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ border: "1px solid #e2e2e2", padding: 12, borderRadius: 6 }}>
      <h3 style={{ marginTop: 0 }}>Lead — {job.title}</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 8 }}>
        <label>Status
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            {['Saved','Applied','Interview','Offer','Rejected','On hold'].map(s => <option key={s}>{s}</option>)}
          </select>
        </label>
        <label>Score
          <input type="number" value={score} onChange={(e) => setScore(parseInt(e.target.value || '0'))} />
        </label>
        <label>Favourite <input type="checkbox" checked={favourite} onChange={(e) => setFavourite(e.target.checked)} /></label>
        <label>Next Action
          <input value={nextAction} onChange={(e) => setNextAction(e.target.value)} />
        </label>
        <label>Next Action Date
          <input placeholder="YYYY-MM-DD" value={nextActionDate} onChange={(e) => setNextActionDate(e.target.value)} />
        </label>
        <label style={{ gridColumn: '1 / -1' }}>Notes
          <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>
      </div>
      <button onClick={save} disabled={saving} style={{ marginTop: 8 }}>{saving ? 'Saving...' : 'Save'}</button>
    </div>
  );
}

