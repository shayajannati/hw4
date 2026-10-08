import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useAuth } from '../auth'
import { fetchHistory, getBoundary, sendChat, setBoundary, type ChatMessage } from '../chat'
import { useSelectedProductId } from '../router'
import { ChatMessages } from './ChatMessages'
import { HandsomeDan } from './HandsomeDan'

const WELCOME: ChatMessage = {
  role: 'assistant',
  content: "Hi! I'm the Campus Customs shopping assistant. Ask me about our hoodies, crewnecks, tees and more.",
}

/** Floating chat button + panel connected to POST /api/chat. */
export function ChatWidget() {
  const { user, checking } = useAuth()
  const currentProductId = useSelectedProductId() // product page being viewed, sent as context
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hiddenCount, setHiddenCount] = useState(0) // saved messages hidden by "New chat" (logged-in only)
  const [historyVersion, setHistoryVersion] = useState(0)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Logged in: show that user's saved conversation (after any "New chat" boundary). Logged out: start
  // fresh (guest chat isn't saved), so the next person on this browser never sees the previous user's messages.
  const userId = user?.id ?? null
  useEffect(() => {
    if (checking) return
    setError(null)
    setHiddenCount(0)
    if (userId === null) {
      setMessages([WELCOME])
      return
    }
    let cancelled = false
    fetchHistory()
      .then((saved) => {
        if (cancelled) return
        const boundary = getBoundary(userId)
        setHiddenCount(saved.filter((m) => (m.id ?? 0) <= boundary).length)
        setMessages([WELCOME, ...saved.filter((m) => (m.id ?? 0) > boundary)])
      })
      .catch((e: Error) => !cancelled && setError(e.message))
    return () => {
      cancelled = true
    }
  }, [userId, checking, historyVersion])

  /** "New chat": guests lose the in-memory conversation; logged-in history stays saved but is set aside. */
  function newChat() {
    if (loading) return
    setError(null)
    setInput('')
    if (userId !== null) {
      const lastId = Math.max(0, getBoundary(userId), ...messages.map((m) => m.id ?? 0))
      setBoundary(userId, lastId)
      setHiddenCount((n) => n + messages.filter((m) => m.id !== undefined).length)
    }
    setMessages([WELCOME])
  }

  function showEarlier() {
    if (userId === null) return
    setBoundary(userId, 0)
    setHistoryVersion((v) => v + 1)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, error])
  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  async function send(e?: FormEvent) {
    e?.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    const earlier = messages.filter((m) => m !== WELCOME) // the greeting isn't part of the real conversation
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    setError(null)
    setLoading(true)
    try {
      const res = await sendChat(text, earlier, currentProductId, userId !== null ? getBoundary(userId) : null)
      const id = res.last_message_id ?? undefined
      setMessages((prev) => {
        const next = [...prev]
        // Give the just-saved user message its id too (it's saved right before the reply).
        if (id !== undefined) next[next.length - 1] = { ...next[next.length - 1], id: id - 1 }
        return [...next, { id, role: 'assistant', content: res.reply, products: res.products }]
      })
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Campus Customs shopping assistant">
          <header className="chat-panel__header">
            <HandsomeDan size={34} className="chat-panel__mascot" />
            <div className="chat-panel__title">
              <strong>Shopping assistant</strong>
              <small>{user ? `Chatting as ${user.first_name} · history saved` : 'Guest chat · not saved'}</small>
            </div>
            <div className="chat-panel__actions">
              <button type="button" className="chat-new" onClick={newChat} disabled={loading} title="Start a new conversation">
                New chat
              </button>
              <button type="button" className="chat-panel__close" onClick={() => setOpen(false)} aria-label="Close chat">
                ×
              </button>
            </div>
          </header>
          <div className="chat-panel__messages">
            {user && hiddenCount > 0 && (
              <div className="chat-notice" role="status">
                New conversation started. Your {hiddenCount} earlier message{hiddenCount === 1 ? ' is' : 's are'} still saved
                to your account.{' '}
                <button type="button" onClick={showEarlier}>
                  Show earlier messages
                </button>
              </div>
            )}
            <ChatMessages messages={messages} loading={loading} />
            {error && (
              <div className="chat-error" role="alert">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <form className="chat-panel__form" onSubmit={send}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) send(e)
              }}
              placeholder="Ask about products…"
              rows={1}
              maxLength={2000}
              aria-label="Your message"
            />
            <button type="submit" className="btn btn--primary chat-send" disabled={loading || !input.trim()}>
              {loading ? '…' : 'Send'}
            </button>
          </form>
        </section>
      )}
      <button type="button" className="chat-launcher" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        {open ? 'Close chat' : '💬 Ask our assistant'}
      </button>
    </div>
  )
}
