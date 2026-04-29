import { motion, AnimatePresence } from 'framer-motion'
import { FiClock, FiSearch, FiTrash2 } from 'react-icons/fi'

const CAT_DOT = {
  grading:       'bg-blue-400',
  attendance:    'bg-green-400',
  exam:          'bg-purple-400',
  disciplinary:  'bg-red-400',
  integrity:     'bg-orange-400',
  financial:     'bg-yellow-400',
  prerequisites: 'bg-teal-400',
  withdrawal:    'bg-pink-400',
  general:       'bg-slate-400',
}

function timeAgo(date) {
  const secs = Math.floor((Date.now() - new Date(date)) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return new Date(date).toLocaleDateString()
}

export default function QueryHistory({ history, onSelect, currentQuery }) {
  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-4 text-center">
        <FiClock className="text-slate-600 mb-3" size={28} />
        <p className="text-slate-500 text-xs leading-relaxed">
          Your search history will appear here after your first query.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2">
        <span className="text-slate-500 text-xs">Recent searches</span>
        <span className="text-slate-600 text-xs">{history.length}</span>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-1 pb-3">
        <AnimatePresence>
          {history.map((item, i) => {
            const primaryCat = item.results?.source_chunks?.[0]?.category || 'general'
            const dotColor = CAT_DOT[primaryCat] || CAT_DOT.general
            const isActive = item.query === currentQuery
            const confidence = item.results?.confidence || 0
            const confPct = Math.round(confidence * 100)

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ delay: i * 0.03 }}
              >
                <button
                  onClick={() => onSelect(item)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl transition-all group ${
                    isActive
                      ? 'bg-brand-500/15 border border-brand-500/25'
                      : 'hover:bg-surface-700/50 border border-transparent'
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    <FiSearch
                      size={13}
                      className={`flex-shrink-0 mt-0.5 ${isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-400'}`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className={`text-xs font-medium leading-snug line-clamp-2 ${isActive ? 'text-slate-100' : 'text-slate-300'}`}>
                        {item.query}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotColor}`} />
                        <span className="text-slate-600 text-xs">{primaryCat}</span>
                        {confPct > 0 && (
                          <span className={`text-xs ${confPct >= 60 ? 'text-green-500' : 'text-yellow-500'}`}>
                            {confPct}%
                          </span>
                        )}
                        <span className="text-slate-600 text-xs ml-auto">{timeAgo(item.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </button>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}
