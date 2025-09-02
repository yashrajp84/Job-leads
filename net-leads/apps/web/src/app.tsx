import { useEffect, useMemo, useState } from 'react'
import { Feed } from './components/Feed/Feed'
import { Composer } from './components/Feed/Composer'
import { Filters } from './components/Feed/Filters'

export default function App() {
  const [q, setQ] = useState('')
  const [tab, setTab] = useState<'all'|'people'|'jobs'|'posts'>('all')
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-6xl p-4 grid grid-cols-12 gap-4">
        <aside className="col-span-2">
          <div className="sticky top-4 space-y-2">
            <div className="text-xl font-bold">Net-Leads</div>
            <nav className="flex flex-col gap-1">
              {['Home','People','Jobs','Posts','Templates'].map(x => (
                <a key={x} className="rounded px-2 py-1 hover:bg-gray-200" href="#">{x}</a>
              ))}
            </nav>
          </div>
        </aside>
        <main className="col-span-7 space-y-3">
          <Composer />
          <Filters value={{q, tab}} onChange={(v)=>{setQ(v.q||''); setTab((v.tab||'all') as any)}} />
          <Feed q={q} tab={tab} />
        </main>
        <aside className="col-span-3 space-y-3">
          <div className="rounded border bg-white p-3">Smart suggestions (LLM)</div>
          <div className="rounded border bg-white p-3">Templates</div>
          <div className="rounded border bg-white p-3">Today</div>
        </aside>
      </div>
    </div>
  )
}

