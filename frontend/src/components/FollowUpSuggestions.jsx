import { motion } from 'framer-motion'
import { FiArrowRight } from 'react-icons/fi'

export default function FollowUpSuggestions({ suggestions, onSelect }) {
  if (!suggestions || suggestions.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="ml-11 mb-6"
    >
      <p className="text-xs text-slate-500 mb-2 px-1">Related questions</p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((text, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 + i * 0.1 }}
            onClick={() => onSelect(text)}
            className="suggestion-pill bg-surface-800/40 border-surface-600/40 text-slate-400
                       hover:text-brand-300 hover:border-brand-500/30 hover:bg-brand-500/5
                       flex items-center gap-1.5 text-xs"
          >
            <FiArrowRight size={10} className="text-brand-500/50" />
            {text}
          </motion.button>
        ))}
      </div>
    </motion.div>
  )
}
