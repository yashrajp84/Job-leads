import { create } from 'zustand'
import { api } from '../lib/api'

type State = {
  items: any[]
  loading: boolean
  load: (q?: string) => Promise<void>
}

export const useFeedStore = create<State>((set, get) => ({
  items: [],
  loading: false,
  load: async (q?: string) => {
    set({loading: true})
    try {
      const data = q ? await api.search(q) : await api.feed()
      set({items: data})
    } finally { set({loading:false}) }
  }
}))

