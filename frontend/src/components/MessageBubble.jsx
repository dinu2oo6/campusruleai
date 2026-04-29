import { useState } from 'react'
import { motion } from 'framer-motion'
import { FiCopy, FiCheck, FiUser } from 'react-icons/fi'
import { RiRobot2Line } from 'react-icons/ri'
import ReactMarkdown from 'react-markdown'

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center mt-1
        ${isUser
          ? 'bg-gradient-to-br from-brand-500 to-brand-600'
          : 'bg-gradient-to-br from-surface-700 to-surface-600 border border-surface-500/30'
        }`}
      >
        {isUser
          ? <FiUser className="text-white" size={14} />
          : <RiRobot2Line className="text-brand-400" size={14} />
        }
      </div>

      {/* Message content */}
      <div className={`max-w-[85%] md:max-w-[75%] group relative ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={isUser ? 'message-user' : 'message-bot'}>
          {isUser ? (
            <p className="text-sm leading-relaxed">{message.content}</p>
          ) : (
            <div className="text-sm leading-relaxed text-slate-200 prose prose-invert prose-sm max-w-none
                          prose-p:my-1 prose-li:my-0.5 prose-ul:my-1 prose-ol:my-1
                          prose-headings:text-slate-100 prose-strong:text-slate-100
                          prose-code:text-brand-300 prose-code:bg-surface-700/50 prose-code:px-1 prose-code:rounded">
              {message.isStreaming ? (
                <span>
                  {message.content}
                  <span className="cursor-blink text-brand-400">▋</span>
                </span>
              ) : (
                <ReactMarkdown>{message.content || ''}</ReactMarkdown>
              )}
            </div>
          )}
        </div>

        {/* Meta row */}
        <div className={`flex items-center gap-2 mt-1.5 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-slate-600">{formatTime(message.timestamp)}</span>

          {!isUser && message.content && !message.isStreaming && (
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-surface-700/50"
              title="Copy to clipboard"
            >
              {copied
                ? <FiCheck size={12} className="text-green-400" />
                : <FiCopy size={12} className="text-slate-500" />
              }
            </button>
          )}

          {!isUser && message.confidence > 0 && !message.isStreaming && (
            <span className={`confidence-badge text-[10px] ${
              message.confidence >= 80 ? 'confidence-high' :
              message.confidence >= 50 ? 'confidence-medium' : 'confidence-low'
            }`}>
              {Math.round(message.confidence)}% confidence
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}
