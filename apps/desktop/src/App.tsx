import { ThemeProvider } from './contexts/ThemeContext'
import { MainLayout } from './components/layout'
import ChatContainer from './components/chat/ChatContainer'

function App() {
  return (
    <ThemeProvider>
      <MainLayout>
        <div className="h-full flex flex-col">
          <ChatContainer />
        </div>
      </MainLayout>
    </ThemeProvider>
  )
}

export default App
