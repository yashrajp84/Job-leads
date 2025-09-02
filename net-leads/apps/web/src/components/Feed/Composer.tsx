import { useState } from 'react'
import { api } from '../../lib/api'

function detectKind(url: string): 'person'|'post'|'job' {
  if (/linkedin\.com\/in\//.test(url)) return 'person'
  if (/linkedin\.com\/posts\//.test(url)) return 'post'
  return 'job'
}

export function Composer() {
  const [url, setUrl] = useState('')
  const [kind, setKind] = useState<'person'|'post'|'job'>('job')
  const [busy, setBusy] = useState(false)
  async function clip() {
    if (!url) return
    setBusy(true)
    try {
      const auto = detectKind(url)
      await api.clip({ kind: kind || auto, url })
      alert('Clipped to Net-Leads ✅')
    } catch (e) {
      alert('Clip failed')
    } finally { setBusy(false); setUrl('') }
  }
  return (
    <div className="rounded border bg-white p-3 flex gap-2 items-center">
      <select className="border rounded px-2 py-1" value={kind} onChange={(e)=>setKind(e.target.value as any)}>
        <option value="person">Person</option>
        <option value="post">Post</option>
        <option value="job">Job</option>
      </select>
      <input value={url} onChange={(e)=>setUrl(e.target.value)} placeholder="Paste a URL…" className="flex-1 border rounded px-2 py-1" />
      <button className="px-3 py-1 bg-black text-white rounded" onClick={clip} disabled={busy || !url}>{busy?'Clipping…':'Clip'}</button>
    </div>
  )
}

