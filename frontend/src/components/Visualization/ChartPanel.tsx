import { useRef } from 'react'
import { Empty, Button, List, Spin } from 'antd'
import { DownloadOutlined, BarChartOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { useChatStore } from '../../store/chatStore'
import styles from './ChartPanel.module.css'

interface ChartPanelProps {
  className?: string
}

export function ChartPanel({ className }: ChartPanelProps) {
  const chartRef = useRef<any>(null)
  const { charts, currentSessionId, currentChartId, setCurrentChartId, chartLoading } = useChatStore()

  const sessionCharts = currentSessionId ? charts.filter((c) => c.session_id === currentSessionId) : []
  const currentChart = sessionCharts.find((c) => c.id === currentChartId) ?? sessionCharts[0]
  const showChartLoading = chartLoading

  const handleDownload = () => {
    if (!currentChart?.option) return
    const instance = chartRef.current?.getEchartsInstance?.()
    if (instance) {
      const url = instance.getDataURL({ type: 'png' })
      const a = document.createElement('a')
      a.href = url
      a.download = `chart-${currentChart.id}.png`
      a.click()
    }
  }

  return (
    <div className={`${styles.wrap} ${className ?? ''}`}>
      <div className={styles.header}>
        <span>图表</span>
      </div>
      <div className={styles.main}>
        {!currentChart ? (
          <Empty
            image={<BarChartOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            description="暂无图表"
            imageStyle={{ height: 80 }}
          >
            在对话中提问涉及数据对比、趋势时，将在此展示可视化图表
          </Empty>
        ) : (
          <>
            <div style={{ height: 280, width: '100%', position: 'relative' }}>
              {showChartLoading && (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.7)', zIndex: 1 }}>
                  <Spin tip="图表生成中..." />
                </div>
              )}
              <ReactECharts ref={chartRef} option={currentChart.option} style={{ height: '100%', width: '100%' }} notMerge />
            </div>
            <div className={styles.actions}>
              <Button size="small" icon={<DownloadOutlined />} onClick={handleDownload}>
                下载
              </Button>
            </div>
          </>
        )}
      </div>
      {sessionCharts.length > 1 && (
        <div className={styles.history}>
          <div className={styles.historyTitle}>图表历史</div>
          <List
            size="small"
            dataSource={sessionCharts}
            renderItem={(item) => (
              <List.Item
                className={currentChartId === item.id ? styles.historyItemActive : styles.historyItem}
                onClick={() => setCurrentChartId(item.id)}
              >
                图表 #{item.id.slice(1)}
              </List.Item>
            )}
          />
        </div>
      )}
    </div>
  )
}
