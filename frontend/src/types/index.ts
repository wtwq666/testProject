import type { EChartsOption } from 'echarts'

export interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  chart_data?: EChartsOption | null
  created_at: string
}

export interface ChartData {
  id: string
  message_id: string
  session_id: string
  option: EChartsOption
  created_at: string
}
