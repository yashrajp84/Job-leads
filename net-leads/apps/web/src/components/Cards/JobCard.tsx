export function JobCard({ job }: { job: any }) {
  return (
    <div className="rounded border bg-white p-3">
      <div className="flex justify-between items-start">
        <div>
          <a href={job.url} target="_blank" className="font-medium hover:underline">{job.title}</a>
          <div className="text-sm text-gray-600">{job.company} · {job.location}</div>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100">{job.source}</span>
      </div>
      {job.description ? <p className="text-sm mt-2 line-clamp-3">{job.description}</p> : null}
      <div className="mt-2 text-sm text-gray-500">Actions: Open · Mark Applied</div>
    </div>
  )
}

