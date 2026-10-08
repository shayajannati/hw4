import { useState } from 'react'
import { useAuth } from '../auth'
import { AuthDialog } from './AuthDialog'

/** Header controls: "Log in / Sign up" when logged out, greeting + "Log out" when logged in. */
export function AccountMenu() {
  const { user, checking, logout } = useAuth()
  const [dialog, setDialog] = useState<'login' | 'signup' | null>(null)

  if (checking) return null
  return (
    <div className="account">
      {user ? (
        <>
          <span className="account__greeting">Hi, {user.first_name}</span>
          <button type="button" className="btn btn--ghost" onClick={() => logout()}>
            Log out
          </button>
        </>
      ) : (
        <>
          <button type="button" className="btn btn--ghost" onClick={() => setDialog('login')}>
            Log in
          </button>
          <button type="button" className="btn btn--light" onClick={() => setDialog('signup')}>
            Sign up
          </button>
        </>
      )}
      {dialog && <AuthDialog initialMode={dialog} onClose={() => setDialog(null)} />}
    </div>
  )
}
