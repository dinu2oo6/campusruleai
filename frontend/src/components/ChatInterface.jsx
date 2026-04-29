import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSend, FiLoader } from 'react-icons/fi'
import { RiSparklingLine } from 'react-icons/ri'
import useChatStore from '../hooks/useChat'
import useAutoComplete from '../hooks/useAutoComplete'
import MessageBubble from './MessageBubble'
import AutoComplete from './AutoComplete'
import FollowUpSuggestions from './FollowUpSuggestions'
import SourceCitation from './SourceCitation'

const QUICK_QUESTIONS = [
  { text: "What GPA do I need for good standing?", emoji: "🎓" },
  { text: "How many absences are allowed?", emoji: "📅" },
  { text: "What happens if I plagiarize?", emoji: "⚠️" },
  { text: "How do I withdraw from a course?", emoji: "📋" },
  { text: "What is the scholarship eligibility?", emoji: "💰" },
  { text: "How do I appeal a grade?", emoji: "📝" },
]

export default function ChatInterface() {
  const [input, setInput] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef(null)
  const messagesEndRef = useRef(null)
  const containerRef = useRef(null)

  const { messages, isStreaming, thinkingTime, sendMessage } = useChatStore()
  const autocomplete = useAutoComplete()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (query = input) => {
    const q = query.trim()
    if (!q || isStreaming) return
    sendMessage(q)
    setInput('')
    autocomplete.hide()
  }

  const handleKeyDown = (e) => {
    // Handle autocomplete keyboard nav first
    if (autocomplete.handleKeyNav(e)) return

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      const selected = autocomplete.getSelected()
      if (selected) {
        setInput(selected.text)
        autocomplete.recordClick(selected.text)
        handleSubmit(selected.text)
      } else {
        handleSubmit()
      }
    }
  }

  const handleInputChange = (e) => {
    const val = e.target.value
    setInput(val)
    autocomplete.fetchSuggestions(val)
  }

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion.text)
    autocomplete.recordClick(suggestion.text)
    handleSubmit(suggestion.text)
  }

  const handleFollowUp = (text) => {
    setInput(text)
    handleSubmit(text)
  }

  const lastBotMessage = [...messages].reverse().find(m => m.role === 'assistant')
  const hasMessages = messages.length > 0

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div ref={containerRef} className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
        <div className="max-w-3xl mx-auto">
          {/* Empty state */}
          {!hasMessages && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center pt-12 pb-8"
            >
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-brand-500/20 to-purple-500/20 border border-brand-500/30 rounded-3xl mb-6"
              >
                <RiSparklingLine className="text-brand-400 text-4xl" />
              </motion.div>

              <h2 className="text-3xl font-bold text-slate-100 mb-3">
                Ask about any <span className="text-gradient">university policy</span>
              </h2>
              <p className="text-slate-400 text-sm max-w-md mx-auto mb-8">
                Powered by AI with RAG — answers are grounded in Westbrook University's official academic policy documents.
              </p>

              {/* Quick question pills */}
              <div className="flex flex-wrap justify-center gap-2">
                {QUICK_QUESTIONS.map((q, i) => (
                  <motion.button
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * i }}
                    onClick={() => handleSubmit(q.text)}
                    className="suggestion-pill bg-surface-800/60 border-surface-600/50 text-slate-300
                               hover:text-slate-100 hover:border-brand-500/40 hover:bg-surface-700/60"
                  >
                    <span className="mr-1">{q.emoji}</span> {q.text}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Messages */}
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <div key={msg.id || idx}>
                <MessageBubble message={msg} />

                {/* Source citations for bot messages */}
                {msg.role === 'assistant' && !msg.isStreaming && msg.sources?.length > 0 && (
                  <SourceCitation
                    sources={msg.sources}
                    confidence={msg.confidence}
                    thinkingTime={thinkingTime}
                  />
                )}

                {/* Follow-up suggestions after last bot message */}
                {msg.role === 'assistant' && !msg.isStreaming && msg === lastBotMessage && msg.followUps?.length > 0 && (
                  <FollowUpSuggestions
                    suggestions={msg.followUps}
                    onSelect={handleFollowUp}
                  />
                )}
              </div>
            ))}
          </AnimatePresence>

          {/* Typing indicator */}
          <AnimatePresence>
            {isStreaming && messages[messages.length - 1]?.role === 'assistant' && messages[messages.length - 1]?.content === '' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-3 px-4 py-3 mb-4"
              >
                <div className="flex items-center gap-1.5 bg-surface-800/60 px-4 py-3 rounded-2xl rounded-bl-md border border-surface-600/30">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
                <span className="text-slate-500 text-xs">Searching policies...</span>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="flex-shrink-0 border-t border-surface-600/30 bg-surface-900/80 backdrop-blur-xl px-4 md:px-6 py-4">
        <div className="max-w-3xl mx-auto relative">
          {/* Autocomplete dropdown */}
          <AutoComplete
            suggestions={autocomplete.suggestions}
            visible={autocomplete.visible}
            selectedIndex={autocomplete.selectedIndex}
            onSelect={handleSuggestionClick}
            loading={autocomplete.loading}
          />

          <motion.div
            animate={{
              boxShadow: focused
                ? '0 0 0 2px rgba(99,102,241,0.3), 0 0 20px rgba(99,102,241,0.1)'
                : '0 0 0 0px transparent',
            }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-3 bg-surface-800/60 border border-surface-600/50 rounded-2xl px-4 py-3 backdrop-blur-sm"
            style={{ borderColor: focused ? 'rgba(99,102,241,0.5)' : undefined }}
          >
            <RiSparklingLine className={`flex-shrink-0 transition-colors ${focused ? 'text-brand-400' : 'text-slate-500'}`} size={20} />

            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={handleInputChange}
              onFocus={() => { setFocused(true); autocomplete.setVisible(autocomplete.suggestions.length > 0) }}
              onBlur={() => { setFocused(false); setTimeout(() => autocomplete.hide(), 200) }}
              onKeyDown={handleKeyDown}
              placeholder="Ask about any academic policy…"
              disabled={isStreaming}
              className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-base outline-none disabled:opacity-60"
            />

            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isStreaming}
              className="btn-primary text-sm px-4 py-2 rounded-xl flex-shrink-0 flex items-center gap-2"
            >
              {isStreaming ? (
                <>
                  <FiLoader className="animate-spin" size={16} />
                  <span className="hidden sm:inline">Thinking…</span>
                </>
              ) : (
                <>
                  <FiSend size={16} />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </motion.div>

          {/* Thinking time display */}
          <AnimatePresence>
            {thinkingTime && !isStreaming && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center mt-2"
              >
                <span className="text-xs text-slate-600">
                  ⚡ Response generated in {thinkingTime}s
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
