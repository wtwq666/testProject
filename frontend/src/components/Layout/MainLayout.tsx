import { Layout } from 'antd'
import { ChatSidebar } from '../ChatSidebar/ChatSidebar'
import { ChatArea } from '../ChatArea/ChatArea'
import { ChartPanel } from '../Visualization/ChartPanel'
import styles from './MainLayout.module.css'

const { Content } = Layout

export function MainLayout() {
  return (
    <Layout className={styles.root}>
      <ChatSidebar className={styles.sidebar} />
      <Content className={styles.center}>
        <ChatArea />
      </Content>
      <ChartPanel className={styles.chartPanel} />
    </Layout>
  )
}
