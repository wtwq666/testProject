/** API 服务层：会话管理 + SSE 流式聊天 */
import type { EChartsOption } from 'echarts'

const BASE = '/api'

export interface SessionRes {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface MessageRes {
  id: string
  role: 'user' | 'assistant'
  content: string
  chart_data?: EChartsOption | null
  created_at: string
}

export async function createSession(title = '新对话'): Promise<SessionRes> {
  const res = await fetch(`${BASE}/sessions?title=${encodeURIComponent(title)}`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getSessions(): Promise<{ sessions: SessionRes[] }> {
  const res = await fetch(`${BASE}/sessions`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getSession(sessionId: string): Promise<{
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: MessageRes[]
}> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function renameSession(sessionId: string, title: string): Promise<void> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  if (!res.ok) throw new Error(await res.text())
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
}

export type ChatStreamEvent =
  | { event: 'message'; data: { content: string } }
  | { event: 'chart'; data: { option: EChartsOption } }
  | { event: 'done'; data: { message_id: string } }
  | { event: 'error'; data: { error: string } }

export async function streamChat(
  sessionId: string,
  message: string,
  onEvent: (e: ChatStreamEvent) => void
): Promise<void> {
  const res = await fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error(await res.text())
  const reader = res.body?.getReader()
  if (!reader) throw new Error('No response body')
  const dec = new TextDecoder()
  let buf = ''
  let currentEvent = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    const lines = buf.split(/\r?\n/)
    buf = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('event: ')) currentEvent = line.slice(7).trim()
      else if (line.startsWith('data: ') && currentEvent) {
        const data = line.slice(6)
        try {
          const parsed = JSON.parse(data) as Record<string, unknown>
          onEvent({ event: currentEvent as ChatStreamEvent['event'], data: parsed } as ChatStreamEvent)
        } catch {
          /* ignore invalid json */
        }
        currentEvent = ''
      }
    }
  }
}
