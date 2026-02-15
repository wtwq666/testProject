import ReactMarkdown from 'react-markdown'
import type { Message } from '../../types'
import styles from './MessageItem.module.css'

interface MessageItemProps {
  message: Message
  isStreaming?: boolean
}

export function MessageItem({ message, isStreaming }: MessageItemProps) {
  const isUser = message.role === 'user'

  return (
    <div className={isUser ? styles.wrapUser : styles.wrapAssistant}>
      <div className={isUser ? styles.bubbleUser : styles.bubbleAssistant}>
        {isUser ? (
          <div className={styles.text}>{message.content}</div>
        ) : (
          <>
            <div className={styles.markdown}>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
            {isStreaming && <span className={styles.cursor}>▋</span>}
          </>
        )}
      </div>
    </div>
  )
}
