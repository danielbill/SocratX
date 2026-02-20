import { ThemeProvider } from './contexts/ThemeContext'
import ChatContainer from './components/chat/ChatContainer'

function App() {
  return (
    <ThemeProvider>
      <div className="h-screen flex flex-col">
        <header className="border-b px-6 py-4">
          <h1 className="text-2xl font-bold">SocratX</h1>
          <p className="text-sm text-muted-foreground">AI 对话助手</p>
        </header>
        <ChatContainer />
      </div>
    </ThemeProvider>
  )
}

export default App
