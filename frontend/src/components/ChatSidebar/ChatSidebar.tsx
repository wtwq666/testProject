import { Button, List, Dropdown, message } from 'antd'
import { PlusOutlined, MoreOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useChatStore } from '../../store/chatStore'
import type { Session } from '../../types'
import type { MenuProps } from 'antd'
import styles from './ChatSidebar.module.css'

interface ChatSidebarProps {
  className?: string
}

export function ChatSidebar({ className }: ChatSidebarProps) {
  const { sessions, currentSessionId, createSession, switchSession, deleteSession, renameSession } = useChatStore()

  const sortedSessions = [...sessions].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )

  const handleMenuClick = async (key: string, session: Session) => {
    if (key === 'delete') {
      await deleteSession(session.id)
      message.success('已删除')
    }
    if (key === 'rename') {
      const title = prompt('新标题', session.title)
      if (title?.trim()) await renameSession(session.id, title.trim())
    }
  }

  const menuItems = (session: Session): MenuProps['items'] => [
    { key: 'rename', icon: <EditOutlined />, label: '重命名', onClick: () => handleMenuClick('rename', session) },
    { key: 'delete', icon: <DeleteOutlined />, label: '删除', danger: true, onClick: () => handleMenuClick('delete', session) },
  ]

  return (
    <div className={`${styles.wrap} ${className ?? ''}`}>
      <div className={styles.header}>
        <Button type="primary" icon={<PlusOutlined />} block onClick={() => createSession()}>
          新建对话
        </Button>
      </div>
      <List
        className={styles.list}
        dataSource={sortedSessions}
        renderItem={(item) => (
          <List.Item
            className={currentSessionId === item.id ? styles.itemActive : styles.item}
            onClick={() => switchSession(item.id)}
            actions={[
              <Dropdown key="more" menu={{ items: menuItems(item) }} trigger={['click']} placement="bottomRight">
                <Button type="text" size="small" icon={<MoreOutlined />} onClick={(e) => e.stopPropagation()} />
              </Dropdown>,
            ]}
          >
            <List.Item.Meta title={item.title} />
          </List.Item>
        )}
      />
      <div className={styles.footer}>智能数据分析助理 · Phase3</div>
    </div>
  )
}
