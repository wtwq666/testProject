import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Skeleton } from 'antd'
import type { Message } from '../../types'
import styles from './MessageItem.module.css'

const TYPING_INTERVAL_MS = 20

interface MessageItemProps {
  message: Message
  isStreaming?: boolean
}

export function MessageItem({ message, isStreaming }: MessageItemProps) {
  const isUser = message.role === 'user'
  const [visibleLength, setVisibleLength] = useState(0)
  const content = message.content ?? ''

  useEffect(() => {
    if (!isStreaming || isUser) {
      setVisibleLength(content.length)
      return
    }
    if (content.length === 0) {
      setVisibleLength(0)
      return
    }
    setVisibleLength(0)
    const len = content.length
    const step = Math.max(1, Math.floor(len / 30))
    let n = 0
    const t = setInterval(() => {
      n += step
      setVisibleLength(Math.min(n, len))
      if (n >= len) clearInterval(t)
    }, TYPING_INTERVAL_MS)
    return () => clearInterval(t)
  }, [content, isStreaming, isUser])

  const displayContent = isStreaming && !isUser && content.length > 0 ? content.slice(0, visibleLength) : content

  return (
    <div className={isUser ? styles.wrapUser : styles.wrapAssistant}>
      <div className={isUser ? styles.bubbleUser : styles.bubbleAssistant}>
        {isUser ? (
          <div className={styles.text}>{message.content}</div>
        ) : isStreaming && content.length === 0 ? (
          <Skeleton active paragraph={{ rows: 2 }} />
        ) : (
          <>
            <div className={styles.markdown}>
              <ReactMarkdown>{displayContent}</ReactMarkdown>
            </div>
            {isStreaming && <span className={styles.cursor}>▋</span>}
          </>
        )}
      </div>
    </div>
  )
}
