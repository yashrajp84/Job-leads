export function PersonCard({ person }: { person: any }) {
  return (
    <div className="rounded border bg-white p-3">
      <div className="flex justify-between items-start">
        <div>
          <a href={person.profile_url} target="_blank" className="font-medium hover:underline">{person.full_name}</a>
          <div className="text-sm text-gray-600">{person.headline} · {person.company}</div>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100">{person.platform}</span>
      </div>
      <div className="mt-2 text-sm text-gray-500">Actions: Invite text · Save · Next action</div>
    </div>
  )
}

