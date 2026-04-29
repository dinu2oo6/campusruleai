import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiChevronDown, FiChevronUp, FiFileText, FiBookOpen, FiClock } from 'react-icons/fi'

const CONFIDENCE_LEVELS = [
  { min: 80, label: 'Exact Match', badge: 'confidence-high', icon: '🟢' },
  { min: 50, label: 'High Confidence', badge: 'confidence-medium', icon: '🟡' },
  { min: 0, label: 'Needs Verification', badge: 'confidence-low', icon: '🟠' },
]

function getConfidenceLevel(score) {
  for (const level of CONFIDENCE_LEVELS) {
    if (score >= level.min) return level
  }
  return CONFIDENCE_LEVELS[2]
}

function SourceItem({ source, index }) {
  const [expanded, setExpanded] = useState(false)
  const scorePct = Math.round((source.score || 0) * 100)
  const level = getConfidenceLevel(scorePct)
  const docName = (source.document || '').replace('.pdf', '').replace(/_/g, ' ')

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glass-card overflow-hidden"
    >
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between gap-3 px-3 py-2.5 hover:bg-surface-700/30 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <FiFileText size={13} className="text-slate-500 flex-shrink-0" />
          <span className="text-slate-300 text-xs font-medium truncate capitalize">{docName}</span>
          {source.section && (
            <span className="text-slate-500 text-xs hidden sm:block truncate">› {source.section?.slice(0, 40)}</span>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`confidence-badge text-[10px] ${level.badge}`}>
            {level.icon} {scorePct}%
          </span>
          <span className="text-slate-600 text-xs">p.{source.page}</span>
          {expanded ? <FiChevronUp size={12} className="text-slate-500" /> : <FiChevronDown size={12} className="text-slate-500" />}
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-3 pb-3 pt-1 border-t border-surface-600/30">
              <p className="text-slate-400 text-xs leading-relaxed">{source.text}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-[10px] text-slate-600">Category: {source.category}</span>
                <span className="text-[10px] text-slate-600">•</span>
                <span className="text-[10px] text-slate-600">{level.label}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function SourceCitation({ sources, confidence, thinkingTime }) {
  const [showAll, setShowAll] = useState(false)

  if (!sources || sources.length === 0) return null

  const confLevel = getConfidenceLevel(Math.round(confidence || 0))
  const displayed = showAll ? sources : sources.slice(0, 2)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="ml-11 mb-4 space-y-2"
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-1">
        <div className="flex items-center gap-1.5">
          <FiBookOpen size={12} className="text-slate-500" />
          <span className="text-xs text-slate-500 font-medium">Sources</span>
        </div>
        <span className={`confidence-badge text-[10px] ${confLevel.badge}`}>
          {confLevel.icon} {Math.round(confidence || 0)}% overall
        </span>
        {thinkingTime && (
          <span className="flex items-center gap-1 text-[10px] text-slate-600">
            <FiClock size={10} /> {thinkingTime}s
          </span>
        )}
      </div>

      {/* Source items */}
      <div className="space-y-1">
        {displayed.map((source, i) => (
          <SourceItem key={i} source={source} index={i} />
        ))}
      </div>

      {sources.length > 2 && (
        <button
          onClick={() => setShowAll(v => !v)}
          className="text-xs text-brand-400 hover:text-brand-300 px-1 transition-colors"
        >
          {showAll ? 'Show less' : `Show ${sources.length - 2} more sources`}
        </button>
      )}
    </motion.div>
  )
}
