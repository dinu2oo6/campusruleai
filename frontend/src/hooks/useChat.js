import { create } from 'zustand'

const API = 'http://localhost:8000'

const useChatStore = create((set, get) => ({
  messages: [],
  conversationId: null,
  isStreaming: false,
  thinkingTime: null,
  error: null,

  setConversationId: (id) => set({ conversationId: id }),

  clearMessages: () => set({ messages: [], conversationId: null, thinkingTime: null, error: null }),

  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),

  updateLastBotMessage: (update) =>
    set((state) => {
      const msgs = [...state.messages]
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === 'assistant') {
          msgs[i] = { ...msgs[i], ...update }
          break
        }
      }
      return { messages: msgs }
    }),

  appendToLastBotMessage: (token) =>
    set((state) => {
      const msgs = [...state.messages]
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === 'assistant') {
          msgs[i] = { ...msgs[i], content: msgs[i].content + token }
          break
        }
      }
      return { messages: msgs }
    }),

  sendMessage: async (query) => {
    const { conversationId, messages } = get()
    const convId = conversationId || crypto.randomUUID()

    set({
      conversationId: convId,
      error: null,
      isStreaming: true,
      thinkingTime: null,
    })

    // Add user message
    const userMsg = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    }
    set((state) => ({ messages: [...state.messages, userMsg] }))

    // Add placeholder bot message
    const botMsg = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      sources: [],
      confidence: 0,
      followUps: [],
      intent: 'general',
      isStreaming: true,
    }
    set((state) => ({ messages: [...state.messages, botMsg] }))

    try {
      const response = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          conversation_id: convId,
          stream: true,
        }),
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed.startsWith('data: ')) continue

          try {
            const data = JSON.parse(trimmed.slice(6))

            if (data.type === 'meta') {
              get().updateLastBotMessage({
                sources: data.sources || [],
                confidence: data.confidence || 0,
                intent: data.intent || 'general',
                citedDocuments: data.cited_documents || [],
              })
            } else if (data.type === 'token') {
              get().appendToLastBotMessage(data.content)
            } else if (data.type === 'done') {
              get().updateLastBotMessage({
                isStreaming: false,
                followUps: data.follow_ups || [],
              })
              set({ thinkingTime: data.thinking_time, isStreaming: false })
            } else if (data.type === 'error') {
              get().updateLastBotMessage({
                content: `Error: ${data.content}`,
                isStreaming: false,
              })
              set({ isStreaming: false, error: data.content })
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }

      // Finalize if stream ended without done message
      set((state) => {
        const msgs = [...state.messages]
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === 'assistant' && msgs[i].isStreaming) {
            msgs[i] = { ...msgs[i], isStreaming: false }
            break
          }
        }
        return { messages: msgs, isStreaming: false }
      })
    } catch (err) {
      // On error, try non-streaming fallback
      try {
        const res = await fetch(`${API}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query,
            conversation_id: convId,
            stream: false,
          }),
        })
        if (res.ok) {
          const data = await res.json()
          get().updateLastBotMessage({
            content: data.answer || 'No answer received.',
            sources: (data.sources || []).map(s => ({
              text: s.text,
              document: s.document,
              page: s.page,
              category: s.category,
              section: s.section,
              score: s.score,
            })),
            confidence: data.confidence || 0,
            followUps: data.follow_ups || [],
            intent: data.intent || 'general',
            citedDocuments: data.cited_documents || [],
            isStreaming: false,
          })
          set({ isStreaming: false, thinkingTime: data.thinking_time })
          return
        }
      } catch {
        // Both streaming and non-streaming failed
      }

      get().updateLastBotMessage({
        content: 'Sorry, I couldn\'t connect to the server. Please make sure the backend is running on port 8000.',
        isStreaming: false,
      })
      set({ isStreaming: false, error: err.message })
    }
  },

  // Load conversation from server
  loadConversation: async (convId) => {
    try {
      const res = await fetch(`${API}/api/conversation/${convId}`)
      if (res.ok) {
        const data = await res.json()
        const messages = (data.messages || []).map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
          sources: m.sources || [],
          confidence: m.confidence || 0,
          followUps: m.follow_ups || [],
          intent: m.intent || 'general',
          isStreaming: false,
        }))
        set({ messages, conversationId: convId, error: null })
      }
    } catch {
      // Silently fail
    }
  },
}))

export default useChatStore
