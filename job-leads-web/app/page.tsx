"use client";
import { useEffect, useMemo, useState } from "react";
import Filters from "../components/Filters";
import JobsTable from "../components/JobsTable";
import LeadEditor from "../components/LeadEditor";
import { Filters as F, Job } from "../lib/types";
import { bulkStatus, fetchJobs, rescore, runScrape, updateLead } from "../lib/api";

export default function Page() {
  const [filters, setFilters] = useState<F>({});
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string | undefined>(undefined);
  const selectedJob = useMemo(() => jobs.find(j => j.id === selected), [jobs, selected]);

  async function load() {
    setLoading(true);
    try {
      const data = await fetchJobs(filters);
      setJobs(data);
      if (!selected && data.length) setSelected(data[0].id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [JSON.stringify(filters)]);

  async function saveLead(fields: any) {
    if (!selectedJob) return;
    await updateLead(selectedJob.id, fields);
    await load();
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12 }}>
      <div>
        <div style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
          <Filters value={filters} onChange={setFilters} />
          <button onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</button>
          <button onClick={async () => { await runScrape(); await load(); }}>Run Scrape</button>
          <button onClick={async () => { const ids = jobs.map(j => j.id); await rescore(ids); await load(); }}>Rescore</button>
          <button onClick={async () => { const ids = selected ? [selected] : jobs.map(j => j.id); await bulkStatus(ids, 'Applied'); await load(); }}>Mark Applied</button>
        </div>
        <JobsTable jobs={jobs} selectedId={selected} onSelect={setSelected} />
      </div>
      <div>
        {selectedJob ? (
          <LeadEditor job={selectedJob} onSave={saveLead} />
        ) : (
          <div style={{ border: '1px dashed #ccc', padding: 12 }}>Select a job to edit lead</div>
        )}
      </div>
    </div>
  );
}

