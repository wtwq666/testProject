import { useState, useRef } from 'react'
import { Button, Input } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { useChatStore } from '../../store/chatStore'
import styles from './InputArea.module.css'

const { TextArea } = Input

export function InputArea() {
  const [value, setValue] = useState('')
  const { sendMessage, currentSessionId, isStreaming } = useChatStore()
  const textRef = useRef<any>(null)

  const handleSend = () => {
    const v = value.trim()
    if (!v || isStreaming) return
    sendMessage(v)
    setValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.wrap}>
      <TextArea
        ref={textRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入自然语言问题，例如：各部门销售额对比"
        autoSize={{ minRows: 2, maxRows: 4 }}
        disabled={!currentSessionId || isStreaming}
        className={styles.input}
      />
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={handleSend}
        disabled={!value.trim() || !currentSessionId || isStreaming}
        className={styles.btn}
      >
        发送
      </Button>
    </div>
  )
}
