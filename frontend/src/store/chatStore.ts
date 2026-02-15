import { create } from 'zustand'
import type { Session, Message, ChartData } from '../types'

// Mock 数据
const mockSessions: Session[] = [
  { id: 's1', title: '销售数据分析', created_at: '2025-02-15T10:00:00Z', updated_at: '2025-02-15T10:30:00Z' },
  { id: 's2', title: '部门人数统计', created_at: '2025-02-15T09:00:00Z', updated_at: '2025-02-15T09:45:00Z' },
  { id: 's3', title: '新对话', created_at: '2025-02-15T08:00:00Z', updated_at: '2025-02-15T08:00:00Z' },
]

const mockMessages: Message[] = [
  { id: 'm1', session_id: 's1', role: 'user', content: '查询各部门的销售额对比', created_at: '2025-02-15T10:05:00Z' },
  {
    id: 'm2',
    session_id: 's1',
    role: 'assistant',
    content: '根据数据库查询，各部门销售额如下：\n\n| 部门 | 销售额 |\n|------|--------|\n| 技术部 | 125万 |\n| 销售部 | 320万 |\n| 市场部 | 88万 |',
    created_at: '2025-02-15T10:05:15Z',
  },
  { id: 'm3', session_id: 's1', role: 'user', content: '用柱状图展示一下', created_at: '2025-02-15T10:06:00Z' },
  {
    id: 'm4',
    session_id: 's1',
    role: 'assistant',
    content: '已生成柱状图，请查看右侧图表区域。',
    chart_data: {
      xAxis: { type: 'category', data: ['技术部', '销售部', '市场部', '人事部', '财务部'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [125, 320, 88, 45, 200] }],
    },
    created_at: '2025-02-15T10:06:20Z',
  },
  { id: 'm5', session_id: 's2', role: 'user', content: '各部门员工人数', created_at: '2025-02-15T09:10:00Z' },
  {
    id: 'm6',
    session_id: 's2',
    role: 'assistant',
    content: '查询结果：技术部 12 人，销售部 8 人，市场部 6 人，人事部 4 人，财务部 5 人。',
    created_at: '2025-02-15T09:10:12Z',
  },
]

const mockCharts: ChartData[] = [
  {
    id: 'c1',
    message_id: 'm4',
    session_id: 's1',
    option: {
      title: { text: '各部门销售额' },
      xAxis: { type: 'category', data: ['技术部', '销售部', '市场部', '人事部', '财务部'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [125, 320, 88, 45, 200] }],
    },
    created_at: '2025-02-15T10:06:20Z',
  },
]

interface ChatState {
  sessions: Session[]
  currentSessionId: string | null
  messages: Message[]
  charts: ChartData[]
  isStreaming: boolean
  createSession: () => void
  switchSession: (id: string) => void
  deleteSession: (id: string) => void
  renameSession: (id: string, title: string) => void
  sendMessage: (content: string) => void
  setStreaming: (v: boolean) => void
  appendChart: (option: ChartData['option']) => void
  setCurrentChartId: (id: string | null) => void
  currentChartId: string | null
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: mockSessions,
  currentSessionId: 's1',
  messages: mockMessages,
  charts: mockCharts,
  isStreaming: false,
  currentChartId: 'c1',

  createSession: () => {
    const id = 's' + Date.now()
    const now = new Date().toISOString()
    set((s) => ({
      sessions: [{ id, title: '新对话', created_at: now, updated_at: now }, ...s.sessions],
      currentSessionId: id,
      messages: s.messages.filter((m) => m.session_id !== id),
      charts: s.charts.filter((c) => c.session_id !== id),
    }))
  },

  switchSession: (id) => {
    const firstChart = get().charts.find((c) => c.session_id === id)
    set({
      currentSessionId: id,
      currentChartId: firstChart?.id ?? null,
    })
  },

  deleteSession: (id) => {
    const { currentSessionId, sessions } = get()
    const next = sessions.filter((s) => s.id !== id)[0]
    set({
      sessions: sessions.filter((s) => s.id !== id),
      messages: get().messages.filter((m) => m.session_id !== id),
      charts: get().charts.filter((c) => c.session_id !== id),
      currentSessionId: currentSessionId === id ? (next?.id ?? null) : currentSessionId,
      currentChartId: currentSessionId === id ? null : get().currentChartId,
    })
  },

  renameSession: (id, title) => {
    set((s) => ({
      sessions: s.sessions.map((x) => (x.id === id ? { ...x, title, updated_at: new Date().toISOString() } : x)),
    }))
  },

  sendMessage: (content) => {
    const { currentSessionId, messages } = get()
    if (!currentSessionId || !content.trim()) return
    const mid = 'm' + Date.now()
    const now = new Date().toISOString()
    const userMsg: Message = {
      id: mid,
      session_id: currentSessionId,
      role: 'user',
      content: content.trim(),
      created_at: now,
    }
    set({
      messages: [...messages, userMsg],
      isStreaming: true,
    })
    // Mock: 1.5s 后追加一条 AI 回复
    setTimeout(() => {
      const aid = 'm' + (Date.now() + 1)
      set((s) => ({
        messages: [
          ...s.messages,
          {
            id: aid,
            session_id: currentSessionId!,
            role: 'assistant',
            content: '这是 Mock 回复。Phase3 接入后端后将返回真实分析结果。',
            created_at: new Date().toISOString(),
          },
        ],
        isStreaming: false,
      }))
    }, 1500)
  },

  setStreaming: (v) => set({ isStreaming: v }),
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
}))
