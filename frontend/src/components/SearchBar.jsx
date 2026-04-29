import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSearch, FiLoader } from 'react-icons/fi'

const SUGGESTIONS = [
  'What GPA do I need to remain in good academic standing?',
  'How many unexcused absences are allowed per semester?',
  'How do I request a makeup exam?',
  'What happens if I plagiarize an assignment?',
  'When is the last day to withdraw from a course?',
  'How do I apply for a medical leave of absence?',
  'Can I use AI tools for my assignments?',
  'What is the Pass/Fail grading option?',
  'How do I appeal a financial aid suspension?',
  'What are the requirements for an Incomplete grade?',
  'How many credits do I need to graduate?',
  'What is the tuition refund policy for withdrawals?',
]

export default function SearchBar({ onSearch, loading, initialQuery = '' }) {
  const [value, setValue]       = useState(initialQuery)
  const [showSugg, setShowSugg] = useState(false)
  const [focused, setFocused]   = useState(false)
  const inputRef  = useRef(null)
  const wrapperRef = useRef(null)

  const filtered = SUGGESTIONS.filter(s =>
    value.trim().length > 1 && s.toLowerCase().includes(value.toLowerCase())
  ).slice(0, 5)

  useEffect(() => {
    setValue(initialQuery)
  }, [initialQuery])

  useEffect(() => {
    const handleClick = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowSugg(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const submit = (q = value) => {
    if (!q.trim() || loading) return
    setShowSugg(false)
    onSearch(q.trim())
  }

  const handleKey = (e) => {
    if (e.key === 'Enter') submit()
    if (e.key === 'Escape') { setShowSugg(false); inputRef.current?.blur() }
  }

  return (
    <div ref={wrapperRef} className="relative">
      {/* Input row */}
      <motion.div
        animate={{ boxShadow: focused ? '0 0 0 2px rgba(99,102,241,0.35)' : '0 0 0 0px transparent' }}
        transition={{ duration: 0.2 }}
        className="flex items-center gap-3 bg-surface-700/60 border border-surface-600 rounded-2xl px-4 py-3.5 transition-colors"
        style={{ borderColor: focused ? 'rgb(99,102,241)' : undefined }}
      >
        {loading
          ? <FiLoader className="text-brand-400 animate-spin flex-shrink-0" size={20} />
          : <FiSearch className="text-slate-400 flex-shrink-0" size={20} />
        }

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={e => { setValue(e.target.value); setShowSugg(true) }}
          onFocus={() => { setFocused(true); setShowSugg(true) }}
          onBlur={() => setFocused(false)}
          onKeyDown={handleKey}
          placeholder="Ask about any academic policy…"
          disabled={loading}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-base outline-none disabled:opacity-60"
        />

        <button
          onClick={() => submit()}
          disabled={!value.trim() || loading}
          className="btn-primary text-sm px-5 py-2 rounded-xl flex-shrink-0"
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </motion.div>

      {/* Suggestions dropdown */}
      <AnimatePresence>
        {showSugg && filtered.length > 0 && (
          <motion.ul
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 top-full left-0 right-0 mt-2 glass-card py-1 shadow-2xl"
          >
            {filtered.map((s, i) => (
              <li
                key={i}
                onMouseDown={() => { setValue(s); submit(s) }}
                className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-brand-500/10 transition-colors group"
              >
                <FiSearch size={14} className="text-slate-500 group-hover:text-brand-400 flex-shrink-0" />
                <span className="text-slate-300 text-sm group-hover:text-slate-100 transition-colors">{s}</span>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>

      {/* Quick suggestion pills (shown when empty) */}
      {!value.trim() && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-wrap gap-2 mt-3"
        >
          {SUGGESTIONS.slice(0, 4).map((s, i) => (
            <button
              key={i}
              onClick={() => { setValue(s); submit(s) }}
              className="text-xs text-slate-400 hover:text-slate-200 px-3 py-1.5 bg-surface-700/50 hover:bg-surface-700 border border-surface-600/60 rounded-full transition-all hover:border-brand-500/40"
            >
              {s.length > 50 ? s.slice(0, 50) + '…' : s}
            </button>
          ))}
        </motion.div>
      )}
    </div>
  )
}
