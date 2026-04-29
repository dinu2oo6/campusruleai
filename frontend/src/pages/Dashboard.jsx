import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import SearchBar from '../components/SearchBar'
import ResultCard from '../components/ResultCard'
import DocumentBrowser from '../components/DocumentBrowser'
import QueryHistory from '../components/QueryHistory'
import { FiBookOpen, FiClock, FiMenu, FiX, FiActivity } from 'react-icons/fi'
import { RiRobot2Line } from 'react-icons/ri'

const API = 'http://localhost:8000'

export default function Dashboard() {
  const [query, setQuery]               = useState('')
  const [results, setResults]           = useState(null)
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)
  const [queryHistory, setQueryHistory] = useState([])
  const [documents, setDocuments]       = useState([])
  const [docsLoading, setDocsLoading]   = useState(true)
  const [activeCategory, setActiveCategory] = useState('all')
  const [activeTab, setActiveTab]       = useState('search')  // 'search' | 'history'
  const [sidebarOpen, setSidebarOpen]   = useState(true)
  const [backendStatus, setBackendStatus] = useState('checking') // 'ok' | 'error' | 'checking'

  // ── Load documents on mount ──────────────────────────────────────────
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await axios.get(`${API}/api/documents`)
        setDocuments(res.data.documents || [])
        setBackendStatus('ok')
      } catch {
        setBackendStatus('error')
      } finally {
        setDocsLoading(false)
      }
    }
    fetchDocuments()
  }, [])

  // ── Search handler ───────────────────────────────────────────────────
  const handleSearch = useCallback(async (q) => {
    if (!q.trim()) return
    setQuery(q)
    setLoading(true)
    setError(null)
    setResults(null)
    setActiveTab('search')

    try {
      const res = await axios.post(`${API}/api/search`, { query: q, top_k: 5 })
      setResults(res.data)
      setQueryHistory(prev => [
        { id: Date.now(), query: q, results: res.data, timestamp: new Date() },
        ...prev.slice(0, 19),
      ])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to the backend. Make sure the server is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Restore from history ─────────────────────────────────────────────
  const handleHistorySelect = (item) => {
    setQuery(item.query)
    setResults(item.results)
    setError(null)
    setActiveTab('search')
  }

  return (
    <div className="flex h-screen bg-surface-900 overflow-hidden">

      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="w-72 flex-shrink-0 flex flex-col border-r border-surface-600/50 bg-surface-800/50 backdrop-blur-xl z-20"
          >
            {/* Logo */}
            <div className="flex items-center gap-3 px-5 py-5 border-b border-surface-600/40">
              <div className="w-9 h-9 bg-brand-500 rounded-xl flex items-center justify-center shadow-lg glow-brand flex-shrink-0">
                <RiRobot2Line className="text-white text-lg" />
              </div>
              <div>
                <h1 className="font-bold text-slate-100 text-sm leading-tight">CampusRule AI</h1>
                <p className="text-slate-500 text-xs">Westbrook University</p>
              </div>
            </div>

            {/* Nav tabs */}
            <div className="flex gap-1 p-3 border-b border-surface-600/40">
              <button
                onClick={() => setActiveTab('search')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'search'
                    ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                    : 'text-slate-400 hover:text-slate-300 hover:bg-surface-700/50'
                }`}
              >
                <FiActivity size={13} /> Search
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'history'
                    ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                    : 'text-slate-400 hover:text-slate-300 hover:bg-surface-700/50'
                }`}
              >
                <FiClock size={13} /> History {queryHistory.length > 0 && <span className="bg-brand-500/30 text-brand-300 px-1.5 rounded-full text-xs">{queryHistory.length}</span>}
              </button>
            </div>

            {/* Content area */}
            <div className="flex-1 overflow-hidden flex flex-col">
              {activeTab === 'history' ? (
                <QueryHistory
                  history={queryHistory}
                  onSelect={handleHistorySelect}
                  currentQuery={query}
                />
              ) : (
                <DocumentBrowser
                  documents={documents}
                  loading={docsLoading}
                  activeCategory={activeCategory}
                  onCategoryChange={setActiveCategory}
                />
              )}
            </div>

            {/* Status bar */}
            <div className="px-4 py-3 border-t border-surface-600/40">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${backendStatus === 'ok' ? 'bg-green-400' : backendStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400 animate-pulse'}`} />
                <span className="text-xs text-slate-500">
                  {backendStatus === 'ok'
                    ? `${documents.length} docs indexed`
                    : backendStatus === 'error'
                    ? 'Backend offline'
                    : 'Connecting...'}
                </span>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* ── Main content ────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top bar */}
        <header className="flex items-center gap-3 px-6 py-4 border-b border-surface-600/40 bg-surface-800/30 backdrop-blur-sm flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(v => !v)}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-surface-700/50 transition-all"
          >
            {sidebarOpen ? <FiX size={18} /> : <FiMenu size={18} />}
          </button>
          <div className="flex items-center gap-2">
            <FiBookOpen className="text-brand-400" size={16} />
            <span className="text-slate-300 text-sm font-medium">Academic Policy Retrieval</span>
          </div>
          {backendStatus === 'error' && (
            <div className="ml-auto flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-red-400" />
              <span className="text-red-400 text-xs">Backend offline — run <code className="font-mono bg-red-500/10 px-1 rounded">uvicorn main:app</code></span>
            </div>
          )}
        </header>

        {/* Scrollable body */}
        <main className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-3xl mx-auto space-y-6">

            {/* Hero / Search */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              {!results && !loading && queryHistory.length === 0 && (
                <div className="text-center mb-8">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-brand-500/10 border border-brand-500/20 rounded-2xl mb-4">
                    <RiRobot2Line className="text-brand-400 text-3xl" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-100 mb-2">
                    Ask about any <span className="text-gradient">university policy</span>
                  </h2>
                  <p className="text-slate-400 text-sm max-w-md mx-auto">
                    Answers are extracted directly from Westbrook University's official academic policy documents — no hallucination.
                  </p>
                </div>
              )}

              <SearchBar
                onSearch={handleSearch}
                loading={loading}
                initialQuery={query}
              />
            </motion.div>

            {/* Loading skeleton */}
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  {[1, 2, 3].map(i => (
                    <div key={i} className="glass-card p-5 space-y-3">
                      <div className="skeleton h-4 w-1/3" />
                      <div className="skeleton h-3 w-full" />
                      <div className="skeleton h-3 w-4/5" />
                      <div className="skeleton h-3 w-2/3" />
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error */}
            <AnimatePresence>
              {error && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="glass-card p-5 border-red-500/30 bg-red-500/5"
                >
                  <p className="text-red-400 text-sm font-medium">Error</p>
                  <p className="text-slate-400 text-sm mt-1">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Results */}
            <AnimatePresence>
              {results && !loading && (
                <ResultCard results={results} query={query} />
              )}
            </AnimatePresence>

            {/* Empty state */}
            {!results && !loading && !error && queryHistory.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12 text-slate-500"
              >
                <FiClock className="mx-auto mb-3 text-3xl opacity-40" />
                <p className="text-sm">Select a previous query from the sidebar to revisit it.</p>
              </motion.div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
