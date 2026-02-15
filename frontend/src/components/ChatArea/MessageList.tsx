import { useRef, useEffect } from 'react'
import { useChatStore } from '../../store/chatStore'
import { MessageItem } from './MessageItem'
import styles from './MessageList.module.css'

export function MessageList() {
  const { messages, currentSessionId, isStreaming } = useChatStore()
  const endRef = useRef<HTMLDivElement>(null)

  const list = currentSessionId ? messages.filter((m) => m.session_id === currentSessionId) : []
  const sessions = useChatStore((s) => s.sessions)
  const lastMsgContent = list[list.length - 1]?.content ?? ''

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [list.length, isStreaming, lastMsgContent.length])

  return (
    <div className={styles.scroll}>
      <div className={styles.inner}>
        {!currentSessionId && sessions.length > 0 ? (
          <div className={styles.empty}>请从左侧选择或新建一个会话</div>
        ) : list.length === 0 ? (
          <div className={styles.empty}>暂无消息，在下方输入问题开始分析</div>
        ) : (
          list.map((m) => (
            <MessageItem
              key={m.id}
              message={m}
              isStreaming={isStreaming && m.role === 'assistant' && m.id === list[list.length - 1]?.id}
            />
          ))
        )}
        <div ref={endRef} />
      </div>
    </div>
  )
}
