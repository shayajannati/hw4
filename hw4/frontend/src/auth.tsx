import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

/** What the backend sends about a user. Never includes the password hash. */
export interface User {
  id: number
  first_name: string
  last_name: string
  name: string
  email: string
}

export interface SignupData {
  first_name: string
  last_name: string
  email: string
  password: string
}

interface AuthState {
  user: User | null
  checking: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

async function request<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, {
    method: body === undefined && path.endsWith('/me') ? 'GET' : 'POST',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'same-origin',
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const detail = typeof data.detail === 'string' ? data.detail : 'Please check the form and try again.'
    throw new Error(detail)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

/** Keeps track of who is logged in. The session itself lives in an HttpOnly cookie set by the backend. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    // On page load, ask the backend whether the session cookie is still valid.
    request<User>('/api/auth/me')
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setUser(await request<User>('/api/auth/login', { email, password }))
  }, [])
  const signup = useCallback(async (data: SignupData) => {
    setUser(await request<User>('/api/auth/signup', data))
  }, [])
  const logout = useCallback(async () => {
    await request<void>('/api/auth/logout', {})
    setUser(null)
  }, [])

  return <AuthContext.Provider value={{ user, checking, login, signup, logout }}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
