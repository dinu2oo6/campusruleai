import { motion, AnimatePresence } from 'framer-motion'
import { FiTrendingUp, FiSearch } from 'react-icons/fi'

const CATEGORY_STYLES = {
  academics: { color: 'text-blue-400', bg: 'bg-blue-500/15', border: 'border-blue-500/30' },
  deadlines: { color: 'text-green-400', bg: 'bg-green-500/15', border: 'border-green-500/30' },
  violations: { color: 'text-orange-400', bg: 'bg-orange-500/15', border: 'border-orange-500/30' },
  financial: { color: 'text-purple-400', bg: 'bg-purple-500/15', border: 'border-purple-500/30' },
  general: { color: 'text-slate-400', bg: 'bg-slate-500/15', border: 'border-slate-500/30' },
}

export default function AutoComplete({ suggestions, visible, selectedIndex, onSelect, loading }) {
  if (!visible || suggestions.length === 0) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 8, scale: 0.98 }}
        transition={{ duration: 0.15 }}
        className="absolute bottom-full left-0 right-0 mb-2 z-50 glass-card py-2 shadow-2xl max-h-[320px] overflow-y-auto"
      >
        {loading && (
          <div className="px-4 py-2">
            <div className="skeleton h-3 w-2/3 mb-2" />
            <div className="skeleton h-3 w-1/2" />
          </div>
        )}

        {suggestions.map((suggestion, i) => {
          const styles = CATEGORY_STYLES[suggestion.category] || CATEGORY_STYLES.general
          const isSelected = i === selectedIndex

          return (
            <motion.button
              key={suggestion.text}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              onMouseDown={(e) => { e.preventDefault(); onSelect(suggestion) }}
              className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all group
                ${isSelected
                  ? 'bg-brand-500/15 border-l-2 border-l-brand-500'
                  : 'hover:bg-surface-700/50 border-l-2 border-l-transparent'
                }`}
            >
              {/* Category emoji */}
              <span className="text-base flex-shrink-0">{suggestion.emoji}</span>

              {/* Suggestion text */}
              <div className="flex-1 min-w-0">
                <p className={`text-sm truncate ${isSelected ? 'text-slate-100' : 'text-slate-300 group-hover:text-slate-100'}`}>
                  {suggestion.text}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${styles.bg} ${styles.color} ${styles.border}`}>
                    {suggestion.category}
                  </span>
                  {suggestion.trending && (
                    <span className="flex items-center gap-0.5 text-[10px] text-orange-400">
                      <FiTrendingUp size={10} /> Trending
                    </span>
                  )}
                  {suggestion.click_count > 5 && (
                    <span className="text-[10px] text-slate-500">
                      Popular with {suggestion.click_count} students
                    </span>
                  )}
                </div>
              </div>

              {/* Keyboard shortcut hint */}
              {isSelected && (
                <span className="text-[10px] text-brand-400 bg-brand-500/10 px-1.5 py-0.5 rounded">
                  Enter ↵
                </span>
              )}
            </motion.button>
          )
        })}
      </motion.div>
    </AnimatePresence>
  )
}
