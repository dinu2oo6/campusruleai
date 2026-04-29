import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiDownload, FiX, FiFile, FiFileText } from 'react-icons/fi'
import useChatStore from '../hooks/useChat'

const API = 'http://localhost:8000'

const FORMATS = [
  { id: 'txt', label: 'Plain Text', icon: '📄', desc: 'Simple text format' },
  { id: 'md', label: 'Markdown', icon: '📝', desc: 'Formatted markdown' },
  { id: 'pdf', label: 'PDF', icon: '📕', desc: 'Professional document' },
  { id: 'docx', label: 'Word Doc', icon: '📘', desc: 'Editable Word format' },
]

export default function ExportDialog({ isOpen, onClose }) {
  const [exporting, setExporting] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState('md')
  const [success, setSuccess] = useState(false)
  const { conversationId } = useChatStore()

  const handleExport = async () => {
    if (!conversationId) return
    setExporting(true)
    setSuccess(false)

    try {
      const res = await fetch(`${API}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          format: selectedFormat,
        }),
      })

      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `campusrule_${conversationId.slice(0, 8)}.${selectedFormat}`
        a.click()
        window.URL.revokeObjectURL(url)
        setSuccess(true)
        setTimeout(() => { setSuccess(false); onClose() }, 1500)
      }
    } catch {
      // Error handling
    } finally {
      setExporting(false)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            onClick={e => e.stopPropagation()}
            className="glass-card p-6 w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <FiDownload className="text-brand-400" />
                Export Conversation
              </h3>
              <button onClick={onClose} className="p-2 rounded-lg hover:bg-surface-700/50 transition-colors">
                <FiX size={18} className="text-slate-400" />
              </button>
            </div>

            {!conversationId ? (
              <p className="text-sm text-slate-400 text-center py-8">
                Start a conversation first to export it.
              </p>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-2 mb-4">
                  {FORMATS.map(fmt => (
                    <button
                      key={fmt.id}
                      onClick={() => setSelectedFormat(fmt.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        selectedFormat === fmt.id
                          ? 'border-brand-500/40 bg-brand-500/10'
                          : 'border-surface-600/40 hover:border-surface-500/50 bg-surface-800/30'
                      }`}
                    >
                      <span className="text-lg">{fmt.icon}</span>
                      <p className="text-xs font-medium text-slate-200 mt-1">{fmt.label}</p>
                      <p className="text-[10px] text-slate-500">{fmt.desc}</p>
                    </button>
                  ))}
                </div>

                <button
                  onClick={handleExport}
                  disabled={exporting}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {success ? (
                    <>✓ Downloaded!</>
                  ) : exporting ? (
                    <>Exporting…</>
                  ) : (
                    <><FiDownload size={16} /> Export as {FORMATS.find(f => f.id === selectedFormat)?.label}</>
                  )}
                </button>
              </>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
