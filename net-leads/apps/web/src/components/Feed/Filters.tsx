export function Filters({ value, onChange }: { value: {q?: string, tab?: string}, onChange: (v: any) => void }) {
  const { q='', tab='all' } = value || {}
  return (
    <div className="rounded border bg-white p-2 flex items-center gap-2">
      <div className="inline-flex rounded border overflow-hidden">
        {['all','people','jobs','posts'].map(k => (
          <button key={k} onClick={()=>onChange({ q, tab: k })} className={`px-3 py-1 ${tab===k?'bg-black text-white':'bg-white'}`}>{k.toUpperCase()}</button>
        ))}
      </div>
      <input value={q} onChange={(e)=>onChange({ q: e.target.value, tab })} placeholder="Search…" className="border rounded px-2 py-1 flex-1" />
    </div>
  )
}

