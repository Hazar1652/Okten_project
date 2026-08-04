import FirstLaunchGate from './components/FirstLaunchGate'
import { AuthProvider } from './store/authContext'
import { AppRouter } from './router/index'

function App() {
  return (
    <AuthProvider>
      <FirstLaunchGate>
        <AppRouter />
      </FirstLaunchGate>
    </AuthProvider>
  )
}

export default App