"use client";
import { Job } from "../lib/types";

export default function JobsTable({ jobs, selectedId, onSelect }: { jobs: Job[]; selectedId?: string; onSelect: (id: string) => void; }) {
  return (
    <div style={{ maxHeight: 420, overflow: "auto", border: "1px solid #e2e2e2" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", position: "sticky", top: 0, background: "#fafafa" }}>
            <th style={{ padding: 8 }}>Title</th>
            <th style={{ padding: 8 }}>Company</th>
            <th style={{ padding: 8 }}>Location</th>
            <th style={{ padding: 8 }}>Source</th>
            <th style={{ padding: 8 }}>Posted</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((j) => (
            <tr key={j.id} onClick={() => onSelect(j.id)} style={{ cursor: "pointer", background: selectedId === j.id ? "#eef6ff" : undefined }}>
              <td style={{ padding: 8 }}>
                <a href={j.url} target="_blank" rel="noreferrer">{j.title}</a>
              </td>
              <td style={{ padding: 8 }}>{j.company}</td>
              <td style={{ padding: 8 }}>{j.location}</td>
              <td style={{ padding: 8 }}>{j.source}</td>
              <td style={{ padding: 8 }}>{j.posted_at || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

