import Markdown from 'react-markdown'
import type { ChatMessage } from '../chat'
import { ProductCard } from './ProductCard'

/**
 * The conversation: customer messages on the right, assistant replies (Markdown) on the left.
 * Each assistant reply shows ITS OWN `products` (from that /api/chat response) as clickable cards.
 */
export function ChatMessages({ messages, loading }: { messages: ChatMessage[]; loading: boolean }) {
  return (
    <>
      {messages.map((m, i) => (
        <div key={i} className={`chat-turn chat-turn--${m.role}`}>
          <div className={`chat-msg chat-msg--${m.role}`} data-role={m.role}>
            {m.role === 'assistant' ? <Markdown>{m.content}</Markdown> : m.content}
          </div>
          {m.role === 'assistant' && m.products && m.products.length > 0 && (
            <div className="chat-cards" data-message-index={i} aria-label="Products from this answer">
              {m.products.map((p) => (
                <ProductCard key={p.product_id} product={p} compact />
              ))}
            </div>
          )}
        </div>
      ))}
      {loading && (
        <div className="chat-msg chat-msg--assistant chat-msg--typing" aria-live="polite">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
          <span className="sr-only">The assistant is typing…</span>
        </div>
      )}
    </>
  )
}
