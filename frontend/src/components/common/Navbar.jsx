import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck, User, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <Link to="/dashboard" className="flex items-center space-x-2 text-brand-600 font-bold text-lg">
          <ShieldCheck className="w-7 h-7 text-brand-600" />
          <span>FilingAuditor <span className="text-xs bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full border border-brand-200">HITL Agent</span></span>
        </Link>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          <User className="w-4 h-4 text-slate-500" />
          <span className="font-semibold text-slate-800">{user?.full_name || user?.email || 'Lead Auditor'}</span>
          <span className="text-[10px] bg-brand-100 text-brand-800 px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">
            {user?.role || 'AUDITOR'}
          </span>
        </div>

        <button
          onClick={handleLogout}
          className="text-slate-500 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition-colors"
          title="Sign out of auditor session"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
