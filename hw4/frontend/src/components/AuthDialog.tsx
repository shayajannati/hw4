import { useState, type FormEvent } from 'react'
import { useAuth } from '../auth'

type Mode = 'login' | 'signup'

/** Log-in / create-account dialog. */
export function AuthDialog({ initialMode, onClose }: { initialMode: Mode; onClose: () => void }) {
  const { login, signup } = useAuth()
  const [mode, setMode] = useState<Mode>(initialMode)
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const update = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  async function submit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (mode === 'signup') {
      if (form.password.length < 8) return setError('Password must be at least 8 characters.')
      if (form.password !== form.confirm) return setError('Passwords do not match.')
    }
    setBusy(true)
    try {
      if (mode === 'login') await login(form.email, form.password)
      else await signup({ first_name: form.first_name, last_name: form.last_name, email: form.email, password: form.password })
      onClose()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const switchTo = (m: Mode) => {
    setMode(m)
    setError(null)
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="auth-title" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="modal__close" onClick={onClose} aria-label="Close">
          ×
        </button>
        <h2 id="auth-title">{mode === 'login' ? 'Log in' : 'Create your account'}</h2>
        <form onSubmit={submit} className="auth-form">
          {mode === 'signup' && (
            <div className="auth-form__row">
              <label>
                First name
                <input name="first_name" value={form.first_name} onChange={update('first_name')} required autoComplete="given-name" />
              </label>
              <label>
                Last name
                <input name="last_name" value={form.last_name} onChange={update('last_name')} required autoComplete="family-name" />
              </label>
            </div>
          )}
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={update('email')} required autoComplete="email" />
          </label>
          <label>
            Password
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={update('password')}
              required
              minLength={mode === 'signup' ? 8 : undefined}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </label>
          {mode === 'signup' && (
            <label>
              Confirm password
              <input name="confirm" type="password" value={form.confirm} onChange={update('confirm')} required autoComplete="new-password" />
            </label>
          )}
          {error && <p className="auth-form__error" role="alert">{error}</p>}
          <button type="submit" className="btn btn--primary" disabled={busy}>
            {busy ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>
        <p className="auth-switch">
          {mode === 'login' ? (
            <>New to Campus Customs? <button type="button" onClick={() => switchTo('signup')}>Create an account</button></>
          ) : (
            <>Already have an account? <button type="button" onClick={() => switchTo('login')}>Log in</button></>
          )}
        </p>
      </div>
    </div>
  )
}
