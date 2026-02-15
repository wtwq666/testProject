import styles from './ChatArea.module.css'
import { MessageList } from './MessageList'
import { InputArea } from './InputArea'

export function ChatArea() {
  return (
    <div className={styles.wrap}>
      <MessageList />
      <InputArea />
    </div>
  )
}
