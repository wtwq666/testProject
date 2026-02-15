import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div style={{ padding: 24, textAlign: 'center' }}>
        <h1>智能数据分析助理</h1>
        <p>Phase1 前端已就绪，请先启动后端：<code>uvicorn app.main:app --reload --port 8000</code></p>
      </div>
    </ConfigProvider>
  )
}

export default App
