/** Types and API call for the chat widget. Mirrors backend/models.py (ChatRequest / ChatResponse). */

export interface ChatProduct {
  product_id: string
  name: string
  garment_type: string
  image: string
  price: number
}

export interface ChatMessage {
  /** chat_messages id, for saved messages of a logged-in user. */
  id?: number
  role: 'user' | 'assistant'
  content: string
  /** Products the assistant's reply referenced (kept for later use; not rendered as cards yet). */
  products?: ChatProduct[]
}

interface ChatResponse {
  reply: string
  products: ChatProduct[]
  current_product_id: string | null
  saved: boolean
  last_message_id: number | null
}

const MAX_HISTORY = 20 // backend accepts up to 20 earlier turns

/**
 * Send the new message to POST /api/chat, with the product page being viewed (if any).
 * `earlier` is only used by the backend for guests; logged-in history comes from the database.
 */
export async function sendChat(
  message: string,
  earlier: ChatMessage[],
  currentProductId: string | null = null,
  historyAfterId: number | null = null,
): Promise<ChatResponse> {
  const history = earlier.slice(-MAX_HISTORY).map(({ role, content }) => ({ role, content }))
  let res: Response
  try {
    res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, current_product_id: currentProductId, history_after_id: historyAfterId }),
      credentials: 'same-origin',
    })
  } catch {
    throw new Error("Can't reach the shopping assistant. Please check that the backend is running and try again.")
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    if (typeof data.detail === 'string') throw new Error(data.detail)
    // No message from FastAPI (e.g. the dev proxy couldn't reach the backend at all).
    throw new Error(
      res.status >= 500
        ? "Can't reach the shopping assistant. Please check that the backend is running and try again."
        : 'The shopping assistant had a problem. Please try again.',
    )
  }
  return res.json() as Promise<ChatResponse>
}

/** The logged-in user's saved conversation (GET /api/chat/history). Throws for guests. */
export async function fetchHistory(): Promise<ChatMessage[]> {
  const res = await fetch('/api/chat/history', { credentials: 'same-origin' })
  if (!res.ok) throw new Error(res.status === 401 ? 'Not logged in.' : 'Could not load your chat history.')
  const data = (await res.json()) as { messages: { id: number; role: string; content: string; products: ChatProduct[] }[] }
  return data.messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .map((m) => ({ id: m.id, role: m.role as ChatMessage['role'], content: m.content, products: m.products }))
}

/** "New chat" boundary for a logged-in user, kept for this browser tab: saved messages up to this id are hidden. */
const boundaryKey = (userId: number) => `cc_chat_boundary_${userId}`
export const getBoundary = (userId: number) => Number(sessionStorage.getItem(boundaryKey(userId))) || 0
export const setBoundary = (userId: number, id: number) =>
  id > 0 ? sessionStorage.setItem(boundaryKey(userId), String(id)) : sessionStorage.removeItem(boundaryKey(userId))
