import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiFile, FiSearch } from 'react-icons/fi'

const CATEGORIES = [
  { id: 'all',           label: 'All',           color: 'text-slate-400',   dot: 'bg-slate-400' },
  { id: 'grading',       label: 'Grading',        color: 'text-blue-400',    dot: 'bg-blue-400' },
  { id: 'attendance',    label: 'Attendance',     color: 'text-green-400',   dot: 'bg-green-400' },
  { id: 'exam',          label: 'Exams',          color: 'text-purple-400',  dot: 'bg-purple-400' },
  { id: 'disciplinary',  label: 'Disciplinary',   color: 'text-red-400',     dot: 'bg-red-400' },
  { id: 'integrity',     label: 'Integrity',      color: 'text-orange-400',  dot: 'bg-orange-400' },
  { id: 'financial',     label: 'Financial Aid',  color: 'text-yellow-400',  dot: 'bg-yellow-400' },
  { id: 'prerequisites', label: 'Prerequisites',  color: 'text-teal-400',    dot: 'bg-teal-400' },
  { id: 'withdrawal',    label: 'Withdrawal',     color: 'text-pink-400',    dot: 'bg-pink-400' },
]

const CAT_COLOR = {
  grading:       'bg-blue-500/15 text-blue-400 border-blue-500/30',
  attendance:    'bg-green-500/15 text-green-400 border-green-500/30',
  exam:          'bg-purple-500/15 text-purple-400 border-purple-500/30',
  disciplinary:  'bg-red-500/15 text-red-400 border-red-500/30',
  integrity:     'bg-orange-500/15 text-orange-400 border-orange-500/30',
  financial:     'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  prerequisites: 'bg-teal-500/15 text-teal-400 border-teal-500/30',
  withdrawal:    'bg-pink-500/15 text-pink-400 border-pink-500/30',
  general:       'bg-slate-500/15 text-slate-400 border-slate-500/30',
}

function DocItem({ doc }) {
  const cls = CAT_COLOR[doc.category] || CAT_COLOR.general
  const niceName = doc.name.replace('.pdf', '').replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className="px-3 py-2.5 rounded-lg hover:bg-surface-700/50 cursor-pointer group transition-colors"
    >
      <div className="flex items-start gap-2.5">
        <FiFile size={14} className="text-slate-500 group-hover:text-slate-400 flex-shrink-0 mt-0.5" />
        <div className="min-w-0">
          <p className="text-slate-300 text-xs font-medium leading-snug group-hover:text-slate-100 transition-colors truncate">
            {niceName}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-1.5 py-0.5 rounded border ${cls}`}>
              {doc.category}
            </span>
            <span className="text-slate-600 text-xs">{doc.max_page}p · {doc.size_kb}KB</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function SkeletonDoc() {
  return (
    <div className="px-3 py-2.5">
      <div className="flex gap-2.5">
        <div className="skeleton w-4 h-4 rounded flex-shrink-0 mt-0.5" />
        <div className="flex-1 space-y-1.5">
          <div className="skeleton h-3 w-4/5" />
          <div className="skeleton h-3 w-1/2" />
        </div>
      </div>
    </div>
  )
}

export default function DocumentBrowser({ documents, loading, activeCategory, onCategoryChange }) {
  const [search, setSearch] = useState('')

  const filtered = documents.filter(doc => {
    const matchCat = activeCategory === 'all' || doc.category === activeCategory
    const matchSearch = !search.trim() ||
      doc.name.toLowerCase().includes(search.toLowerCase()) ||
      doc.category.includes(search.toLowerCase())
    return matchCat && matchSearch
  })

  const counts = documents.reduce((acc, doc) => {
    acc[doc.category] = (acc[doc.category] || 0) + 1
    return acc
  }, {})

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Search input */}
      <div className="px-3 pt-3 pb-2">
        <div className="flex items-center gap-2 bg-surface-700/50 border border-surface-600/50 rounded-lg px-3 py-2">
          <FiSearch size={13} className="text-slate-500 flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Filter documents…"
            className="flex-1 bg-transparent text-slate-300 placeholder-slate-600 text-xs outline-none"
          />
        </div>
      </div>

      {/* Category pills */}
      <div className="px-3 pb-2 flex flex-wrap gap-1">
        {CATEGORIES.map(cat => {
          const count = cat.id === 'all' ? documents.length : (counts[cat.id] || 0)
          if (cat.id !== 'all' && count === 0) return null
          return (
            <button
              key={cat.id}
              onClick={() => onCategoryChange(cat.id)}
              className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full border transition-all ${
                activeCategory === cat.id
                  ? `${cat.color} bg-surface-600/80 border-surface-500`
                  : 'text-slate-500 border-surface-700/50 hover:text-slate-300 hover:border-surface-600'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cat.dot}`} />
              {cat.label}
              <span className="opacity-60">{count}</span>
            </button>
          )
        })}
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-1">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => <SkeletonDoc key={i} />)
        ) : filtered.length === 0 ? (
          <div className="text-center py-8 text-slate-600 text-xs">
            No documents match your filter.
          </div>
        ) : (
          <AnimatePresence>
            {filtered.map((doc, i) => (
              <motion.div key={doc.name} transition={{ delay: i * 0.02 }}>
                <DocItem doc={doc} />
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Footer count */}
      {!loading && (
        <div className="px-4 py-2 border-t border-surface-600/30">
          <p className="text-slate-600 text-xs">
            {filtered.length} of {documents.length} documents
          </p>
        </div>
      )}
    </div>
  )
}
