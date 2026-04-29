import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiMenu, FiX, FiDownload } from 'react-icons/fi'
import ConversationSidebar from './components/ConversationSidebar'
import ThemeToggle from './components/ThemeToggle'
import ExportDialog from './components/ExportDialog'
import Chat from './pages/Chat'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import useTheme from './hooks/useTheme'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentPage, setCurrentPage] = useState('chat')
  const [exportOpen, setExportOpen] = useState(false)
  const { theme, toggle: toggleTheme } = useTheme()

  // Responsive sidebar
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 768px)')
    if (mq.matches) setSidebarOpen(false)
    const handler = (e) => { if (e.matches) setSidebarOpen(false) }
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  const handleNavigate = (page) => {
    setCurrentPage(page)
    // Close sidebar on mobile
    if (window.innerWidth < 768) setSidebarOpen(false)
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'analytics': return <Analytics />
      case 'settings': return <Settings />
      default: return <Chat />
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-surface-950 bg-mesh">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            {/* Mobile overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/50 z-30 md:hidden"
            />

            <motion.aside
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="fixed md:relative w-72 flex-shrink-0 flex flex-col
                         border-r border-surface-600/30
                         bg-surface-900/95 backdrop-blur-2xl
                         z-40 h-full"
            >
              <ConversationSidebar
                onNavigate={handleNavigate}
                currentPage={currentPage}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between gap-3 px-4 md:px-6 py-3 border-b border-surface-600/30 bg-surface-900/50 backdrop-blur-xl flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(v => !v)}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-surface-700/50 transition-all"
            >
              {sidebarOpen ? <FiX size={18} /> : <FiMenu size={18} />}
            </button>
            <div>
              <h2 className="text-sm font-semibold text-slate-200 capitalize">
                {currentPage === 'chat' ? 'Chat' : currentPage === 'analytics' ? 'Analytics' : 'Settings & Tools'}
              </h2>
              <p className="text-[10px] text-slate-500">Westbrook University · Academic Policy AI</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setExportOpen(true)}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-surface-700/50 transition-all"
              title="Export conversation"
            >
              <FiDownload size={16} />
            </button>
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
          </div>
        </header>

        {/* Page Content */}
        <motion.main
          key={currentPage}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="flex-1 overflow-hidden flex flex-col"
        >
          {renderPage()}
        </motion.main>
      </div>

      {/* Export Dialog */}
      <ExportDialog isOpen={exportOpen} onClose={() => setExportOpen(false)} />
    </div>
  )
}
