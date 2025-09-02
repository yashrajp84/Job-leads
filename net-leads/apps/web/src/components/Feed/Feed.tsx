import { useEffect } from 'react'
import { useFeedStore } from '../../store/useFeedStore'
import { JobCard } from '../Cards/JobCard'
import { PersonCard } from '../Cards/PersonCard'
import { PostCard } from '../Cards/PostCard'

export function Feed({ q, tab }: { q?: string, tab: 'all'|'people'|'jobs'|'posts' }) {
  const { items, loading, load } = useFeedStore()
  useEffect(()=>{ load(q) }, [q])
  const filtered = items.filter(it => tab==='all' || it.kind===tab)
  return (
    <div className="space-y-3">
      {loading && <div className="text-sm text-gray-500">Loading…</div>}
      {filtered.map((item, idx) => {
        if (item.kind==='person') return <PersonCard key={idx} person={item} />
        if (item.kind==='post') return <PostCard key={idx} post={item} />
        return <JobCard key={idx} job={item} />
      })}
      {!loading && filtered.length===0 && <div className="text-sm text-gray-500">No items</div>}
    </div>
  )
}

