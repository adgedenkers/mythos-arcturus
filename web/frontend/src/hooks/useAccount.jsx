import { createContext, useContext, useState } from 'react'

const AccountContext = createContext()

export function AccountProvider({ children }) {
  const [account, setAccount] = useState('combined') // 'combined' | 'usaa' | 'sun'

  return (
    <AccountContext.Provider value={{ account, setAccount }}>
      {children}
    </AccountContext.Provider>
  )
}

export function useAccount() {
  const ctx = useContext(AccountContext)
  if (!ctx) throw new Error('useAccount must be used within AccountProvider')
  return ctx
}

export function accountLabel(account) {
  if (account === 'combined') return 'USAA + Sunmark'
  if (account === 'usaa') return 'USAA Only'
  if (account === 'sun') return 'Sunmark Only'
  return account
}
