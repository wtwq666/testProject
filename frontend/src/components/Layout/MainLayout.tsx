import { useEffect } from 'react'
import { Alert, Layout, Spin } from 'antd'
import { ChatSidebar } from '../ChatSidebar/ChatSidebar'
import { ChatArea } from '../ChatArea/ChatArea'
import { ChartPanel } from '../Visualization/ChartPanel'
import { useChatStore } from '../../store/chatStore'
import styles from './MainLayout.module.css'

const { Content } = Layout

export function MainLayout() {
  const loadSessions = useChatStore((s) => s.loadSessions)
  const loading = useChatStore((s) => s.loading)
  const error = useChatStore((s) => s.error)
  const clearError = useChatStore((s) => s.clearError)

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  return (
    <Layout className={styles.root}>
      {loading && (
        <div className={styles.loading}>
          <Spin tip="加载中..." size="large" />
        </div>
      )}
      {error && (
        <Alert
          type="error"
          message={error}
          closable
          onClose={clearError}
          style={{ position: 'fixed', top: 16, left: 270, right: 420, zIndex: 1000 }}
        />
      )}
      <ChatSidebar className={styles.sidebar} />
      <Content className={styles.center}>
        <ChatArea />
      </Content>
      <ChartPanel className={styles.chartPanel} />
    </Layout>
  )
}
