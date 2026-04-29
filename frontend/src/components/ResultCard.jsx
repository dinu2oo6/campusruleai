import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiChevronDown, FiChevronUp, FiFileText, FiExternalLink,
  FiCheckCircle, FiAlertCircle,
} from 'react-icons/fi'

const CATEGORY_COLORS = {
  grading:       { bg: 'bg-blue-500/15',    text: 'text-blue-400',    border: 'border-blue-500/30',    dot: 'bg-blue-400' },
  attendance:    { bg: 'bg-green-500/15',   text: 'text-green-400',   border: 'border-green-500/30',   dot: 'bg-green-400' },
  exam:          { bg: 'bg-purple-500/15',  text: 'text-purple-400',  border: 'border-purple-500/30',  dot: 'bg-purple-400' },
  disciplinary:  { bg: 'bg-red-500/15',     text: 'text-red-400',     border: 'border-red-500/30',     dot: 'bg-red-400' },
  integrity:     { bg: 'bg-orange-500/15',  text: 'text-orange-400',  border: 'border-orange-500/30',  dot: 'bg-orange-400' },
  financial:     { bg: 'bg-yellow-500/15',  text: 'text-yellow-400',  border: 'border-yellow-500/30',  dot: 'bg-yellow-400' },
  prerequisites: { bg: 'bg-teal-500/15',    text: 'text-teal-400',    border: 'border-teal-500/30',    dot: 'bg-teal-400' },
  withdrawal:    { bg: 'bg-pink-500/15',    text: 'text-pink-400',    border: 'border-pink-500/30',    dot: 'bg-pink-400' },
  general:       { bg: 'bg-slate-500/15',   text: 'text-slate-400',   border: 'border-slate-500/30',   dot: 'bg-slate-400' },
}

function ConfidenceBar({ score }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? 'bg-green-400' : pct >= 40 ? 'bg-yellow-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="confidence-bar w-20">
        <motion.div
          className={`confidence-fill ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        />
      </div>
      <span className={`text-xs font-semibold ${color.replace('bg-', 'text-')}`}>{pct}%</span>
    </div>
  )
}

function ChunkItem({ chunk, index }) {
  const [open, setOpen] = useState(false)
  const colors = CATEGORY_COLORS[chunk.category] || CATEGORY_COLORS.general
  const scorePct = Math.round(chunk.score * 100)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`rounded-xl border ${colors.border} bg-surface-900/50 overflow-hidden`}
    >
      {/* Chunk header */}
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 hover:bg-surface-700/30 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${colors.dot}`} />
          <span className="text-slate-300 text-xs font-medium truncate">{chunk.section}</span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <span className="text-slate-500 text-xs hidden sm:block">
            {chunk.document.replace('.pdf', '').replace(/_/g, ' ')}
          </span>
          <span className="text-slate-500 text-xs">p.{chunk.page}</span>
          <div className="flex items-center gap-1">
            <div className="w-8 h-1 bg-surface-600 rounded-full overflow-hidden">
              <div
                className={`h-full ${scorePct >= 70 ? 'bg-green-400' : 'bg-yellow-400'} rounded-full`}
                style={{ width: `${scorePct}%` }}
              />
            </div>
            <span className="text-slate-500 text-xs">{scorePct}%</span>
          </div>
          {open ? <FiChevronUp size={14} className="text-slate-400" /> : <FiChevronDown size={14} className="text-slate-400" />}
        </div>
      </button>

      {/* Expanded text */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 pb-4 pt-1 border-t border-surface-600/30">
              <p className="text-slate-300 text-sm leading-relaxed">{chunk.text}</p>
              <div className={`inline-flex items-center gap-1.5 mt-3 px-2 py-1 rounded-md text-xs font-medium ${colors.bg} ${colors.text} border ${colors.border}`}>
                {chunk.category.charAt(0).toUpperCase() + chunk.category.slice(1)}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function ResultCard({ results, query }) {
  const [showChunks, setShowChunks] = useState(false)
  const { answer, confidence, source_chunks = [], cited_documents = [] } = results

  const primaryCategory = source_chunks[0]?.category || 'general'
  const colors = CATEGORY_COLORS[primaryCategory] || CATEGORY_COLORS.general
  const isHighConfidence = confidence >= 0.6

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35 }}
      className="space-y-4"
    >
      {/* Main answer card */}
      <div className={`glass-card p-5 border-l-4 ${isHighConfidence ? colors.border.replace('border-', 'border-l-') : 'border-l-yellow-500/50'}`}>
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            {isHighConfidence
              ? <FiCheckCircle className="text-green-400 flex-shrink-0" size={17} />
              : <FiAlertCircle className="text-yellow-400 flex-shrink-0" size={17} />
            }
            <span className="text-slate-200 text-sm font-semibold">
              {isHighConfidence ? 'Answer found' : 'Partial match'}
            </span>
          </div>
          <ConfidenceBar score={confidence} />
        </div>

        {/* Answer text */}
        <p className="text-slate-100 text-base leading-relaxed font-medium">
          {answer}
        </p>

        {/* Category badge */}
        <div className="flex flex-wrap items-center gap-2 mt-4">
          <span className={`category-badge ${colors.bg} ${colors.text} border ${colors.border}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${colors.dot}`} />
            {primaryCategory}
          </span>
          {cited_documents.map((doc, i) => (
            <span key={i} className="inline-flex items-center gap-1 text-xs text-slate-400 bg-surface-700/50 px-2 py-1 rounded-lg border border-surface-600/40">
              <FiFileText size={11} />
              {doc.replace('.pdf', '').replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      </div>

      {/* Source chunks toggle */}
      {source_chunks.length > 0 && (
        <div>
          <button
            onClick={() => setShowChunks(v => !v)}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors mb-3"
          >
            {showChunks ? <FiChevronUp size={15} /> : <FiChevronDown size={15} />}
            {showChunks ? 'Hide' : 'Show'} {source_chunks.length} source excerpt{source_chunks.length !== 1 ? 's' : ''}
          </button>

          <AnimatePresence>
            {showChunks && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-2"
              >
                {source_chunks.map((chunk, i) => (
                  <ChunkItem key={i} chunk={chunk} index={i} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  )
}
