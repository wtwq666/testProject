import { create } from 'zustand'
import type { Session, Message, ChartData } from '../types'
import * as api from '../services/api'

interface ChatState {
  sessions: Session[]
  currentSessionId: string | null
  messages: Message[]
  charts: ChartData[]
  isStreaming: boolean
  currentChartId: string | null
  chartLoading: boolean
  loading: boolean
  error: string | null
  loadSessions: () => Promise<void>
  loadSession: (id: string) => Promise<void>
  createSession: () => void
  switchSession: (id: string) => void
  deleteSession: (id: string) => void
  renameSession: (id: string, title: string) => void
  sendMessage: (content: string) => void
  setStreaming: (v: boolean) => void
  appendChart: (option: ChartData['option']) => void
  setCurrentChartId: (id: string | null) => void
  setChartLoading: (v: boolean) => void
  clearError: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  charts: [],
  isStreaming: false,
  currentChartId: null,
  chartLoading: false,
  loading: false,
  error: null,

  loadSessions: async () => {
    set({ loading: true, error: null })
    try {
      const { sessions } = await api.getSessions()
      set({ sessions, loading: false })
      const { currentSessionId } = get()
      if (currentSessionId && sessions.some((s) => s.id === currentSessionId)) {
        await get().loadSession(currentSessionId)
      } else if (sessions.length > 0) {
        get().switchSession(sessions[0].id)
      } else {
        get().createSession()
      }
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },

  loadSession: async (id: string) => {
    set({ loading: true, error: null })
    try {
      const data = await api.getSession(id)
      const charts: ChartData[] = data.messages
        .filter((m) => m.chart_data)
        .map((m) => ({
          id: m.id,
          message_id: m.id,
          session_id: id,
          option: m.chart_data!,
          created_at: m.created_at,
        }))
      set({
        messages: data.messages,
        charts,
        currentSessionId: id,
        currentChartId: charts.length > 0 ? charts[charts.length - 1].id : null,
        loading: false,
      })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },

  createSession: async () => {
    try {
      const s = await api.createSession()
      const session: Session = {
        id: s.id,
        title: s.title,
        created_at: s.created_at,
        updated_at: s.updated_at,
      }
      set((state) => ({
        sessions: [session, ...state.sessions],
        currentSessionId: s.id,
        messages: [],
        charts: [],
        currentChartId: null,
        error: null,
      }))
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },

  switchSession: (id: string) => {
    set({ currentSessionId: id })
    get().loadSession(id)
  },

  deleteSession: async (id: string) => {
    try {
      await api.deleteSession(id)
      const { currentSessionId, sessions } = get()
      const next = sessions.filter((s) => s.id !== id)[0]
      set({
        sessions: sessions.filter((s) => s.id !== id),
        messages: get().messages.filter((m) => m.session_id !== id),
        charts: get().charts.filter((c) => c.session_id !== id),
        currentSessionId: currentSessionId === id ? (next?.id ?? null) : currentSessionId,
        currentChartId: currentSessionId === id ? null : get().currentChartId,
        error: null,
      })
      if (currentSessionId === id && next) {
        get().loadSession(next.id)
      }
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },

  renameSession: async (id: string, title: string) => {
    try {
      await api.renameSession(id, title)
      set((s) => ({
        sessions: s.sessions.map((x) =>
          x.id === id ? { ...x, title, updated_at: new Date().toISOString() } : x
        ),
        error: null,
      }))
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },

  sendMessage: (content: string) => {
    const { currentSessionId, messages } = get()
    if (!currentSessionId || !content.trim()) return
    set({ error: null })

    const userMsg: Message = {
      id: 'temp-u-' + Date.now(),
      session_id: currentSessionId,
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    }
    set({ messages: [...messages, userMsg], isStreaming: true })

    const tempAiId = 'temp-ai-' + Date.now()
    const aiMsg: Message = {
      id: tempAiId,
      session_id: currentSessionId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }
    set((s) => ({ messages: [...s.messages, aiMsg] }))

    api
      .streamChat(currentSessionId, content.trim(), (e) => {
        if (e.event === 'message') {
          const txt = (e.data as { content?: string }).content ?? ''
          set((s) => ({
            messages: s.messages.map((m) =>
              m.id === tempAiId ? { ...m, content: txt } : m
            ),
          }))
        }
        if (e.event === 'chart') {
          set({ chartLoading: true })
          const opt = (e.data as { option?: ChartData['option'] }).option
          if (opt) get().appendChart(opt)
        }
        if (e.event === 'done') {
          const mid = (e.data as { message_id?: string }).message_id ?? tempAiId
          set((s) => ({
            messages: s.messages.map((m) =>
              m.id === tempAiId ? { ...m, id: mid } : m
            ),
            isStreaming: false,
            chartLoading: false,
          }))
        }
        if (e.event === 'error') {
          set({
            isStreaming: false,
            chartLoading: false,
            error: (e.data as { error?: string }).error ?? '请求失败',
          })
          set((s) => ({ messages: s.messages.filter((m) => m.id !== tempAiId) }))
        }
      })
      .catch((e) => {
        set({
          isStreaming: false,
          chartLoading: false,
          error: (e as Error).message,
          messages: get().messages.filter((m) => m.id !== tempAiId),
        })
      })
  },

  setStreaming: (v) => set({ isStreaming: v }),
  setChartLoading: (v) => set({ chartLoading: v }),
  appendChart: (option) => {
    const { currentSessionId, charts } = get()
    if (!currentSessionId) return
    const id = 'c' + Date.now()
    set({
      charts: [...charts, { id, message_id: '', session_id: currentSessionId, option, created_at: new Date().toISOString() }],
      currentChartId: id,
    })
  },
  setCurrentChartId: (id) => set({ currentChartId: id }),
  clearError: () => set({ error: null }),
}))
