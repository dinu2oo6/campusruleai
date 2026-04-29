import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiMessageSquare, FiSearch, FiTrash2, FiBookmark, FiPlus, FiClock } from 'react-icons/fi'
import { RiRobot2Line } from 'react-icons/ri'
import useChatStore from '../hooks/useChat'

const API = 'http://localhost:8000'

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const secs = Math.floor((Date.now() - new Date(dateStr)) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return new Date(dateStr).toLocaleDateString()
}

export default function ConversationSidebar({ onNavigate, currentPage }) {
  const [conversations, setConversations] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const { conversationId, clearMessages, loadConversation, setConversationId } = useChatStore()

  const fetchConversations = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/conversations?limit=20`)
      if (res.ok) {
        const data = await res.json()
        setConversations(data.conversations || [])
      }
    } catch {
      // Offline
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConversations()
    const interval = setInterval(fetchConversations, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleNewChat = () => {
    clearMessages()
    onNavigate('chat')
  }

  const handleSelectConversation = (conv) => {
    loadConversation(conv.conversation_id)
    onNavigate('chat')
  }

  const handleDelete = async (e, convId) => {
    e.stopPropagation()
    try {
      await fetch(`${API}/api/conversation/${convId}`, { method: 'DELETE' })
      setConversations(prev => prev.filter(c => c.conversation_id !== convId))
      if (convId === conversationId) clearMessages()
    } catch {
      // Silent
    }
  }

  const handlePin = async (e, convId) => {
    e.stopPropagation()
    const conv = conversations.find(c => c.conversation_id === convId)
    const newPinned = !conv?.pinned
    try {
      await fetch(`${API}/api/conversation/${convId}/pin?pinned=${newPinned}`, { method: 'POST' })
      setConversations(prev =>
        prev.map(c =>
          c.conversation_id === convId ? { ...c, pinned: newPinned } : c
        ).sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0))
      )
    } catch {
      // Silent
    }
  }

  const filtered = conversations.filter(c =>
    !search.trim() || (c.title || '').toLowerCase().includes(search.toLowerCase())
  )

  const pinned = filtered.filter(c => c.pinned)
  const recent = filtered.filter(c => !c.pinned)

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-surface-600/30">
        <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl flex items-center justify-center shadow-lg glow-brand flex-shrink-0">
          <RiRobot2Line className="text-white text-lg" />
        </div>
        <div>
          <h1 className="font-bold text-slate-100 text-sm leading-tight">CampusRule AI</h1>
          <p className="text-slate-500 text-xs">v2.0 · Westbrook University</p>
        </div>
      </div>

      {/* New Chat button */}
      <div className="px-3 pt-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-500/10 border border-brand-500/20
                     text-brand-400 text-sm font-medium hover:bg-brand-500/15 hover:border-brand-500/30
                     transition-all active:scale-[0.98]"
        >
          <FiPlus size={16} />
          New Conversation
        </button>
      </div>

      {/* Nav tabs */}
      <div className="flex gap-1 px-3 py-3">
        {['chat', 'analytics', 'settings'].map(page => (
          <button
            key={page}
            onClick={() => onNavigate(page)}
            className={`flex-1 py-2 rounded-lg text-xs font-medium capitalize transition-all ${
              currentPage === page
                ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-surface-700/50'
            }`}
          >
            {page}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="px-3 pb-2">
        <div className="flex items-center gap-2 bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2">
          <FiSearch size={13} className="text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search conversations…"
            className="flex-1 bg-transparent text-slate-300 placeholder-slate-600 text-xs outline-none"
          />
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 space-y-1 pb-3">
        {loading && conversations.length === 0 && (
          <div className="px-3 py-8 text-center">
            <div className="skeleton h-3 w-2/3 mx-auto mb-2" />
            <div className="skeleton h-3 w-1/2 mx-auto" />
          </div>
        )}

        {!loading && conversations.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <FiMessageSquare className="text-slate-600 mb-3" size={28} />
            <p className="text-slate-500 text-xs">Start a conversation to see it here.</p>
          </div>
        )}

        {pinned.length > 0 && (
          <>
            <p className="text-slate-600 text-[10px] uppercase tracking-wider px-3 pt-2">Pinned</p>
            {pinned.map(conv => (
              <ConvItem
                key={conv.conversation_id}
                conv={conv}
                isActive={conv.conversation_id === conversationId}
                onSelect={() => handleSelectConversation(conv)}
                onDelete={(e) => handleDelete(e, conv.conversation_id)}
                onPin={(e) => handlePin(e, conv.conversation_id)}
              />
            ))}
          </>
        )}

        {recent.length > 0 && (
          <>
            <p className="text-slate-600 text-[10px] uppercase tracking-wider px-3 pt-2">Recent</p>
            {recent.map(conv => (
              <ConvItem
                key={conv.conversation_id}
                conv={conv}
                isActive={conv.conversation_id === conversationId}
                onSelect={() => handleSelectConversation(conv)}
                onDelete={(e) => handleDelete(e, conv.conversation_id)}
                onPin={(e) => handlePin(e, conv.conversation_id)}
              />
            ))}
          </>
        )}
      </div>

      {/* Status bar */}
      <div className="px-4 py-3 border-t border-surface-600/30">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-slate-500">Online · RAG + LLM ready</span>
        </div>
      </div>
    </div>
  )
}

function ConvItem({ conv, isActive, onSelect, onDelete, onPin }) {
  return (
    <motion.button
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      onClick={onSelect}
      className={`w-full text-left px-3 py-2.5 rounded-xl transition-all group flex items-start gap-2.5 ${
        isActive
          ? 'bg-brand-500/15 border border-brand-500/25'
          : 'hover:bg-surface-700/50 border border-transparent'
      }`}
    >
      <FiMessageSquare size={13} className={`flex-shrink-0 mt-0.5 ${isActive ? 'text-brand-400' : 'text-slate-500'}`} />
      <div className="min-w-0 flex-1">
        <p className={`text-xs font-medium line-clamp-2 ${isActive ? 'text-slate-100' : 'text-slate-300'}`}>
          {conv.title || 'New conversation'}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <FiClock size={10} className="text-slate-600" />
          <span className="text-slate-600 text-[10px]">{timeAgo(conv.updated_at)}</span>
          <span className="text-slate-600 text-[10px]">· {conv.message_count || 0} msgs</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={onPin} className="p-1 rounded hover:bg-surface-600/50" title={conv.pinned ? 'Unpin' : 'Pin'}>
          <FiBookmark size={11} className={conv.pinned ? 'text-brand-400 fill-brand-400' : 'text-slate-500'} />
        </button>
        <button onClick={onDelete} className="p-1 rounded hover:bg-red-500/10" title="Delete">
          <FiTrash2 size={11} className="text-slate-500 hover:text-red-400" />
        </button>
      </div>
    </motion.button>
  )
}
