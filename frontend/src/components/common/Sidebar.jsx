import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FileSearch, CheckSquare, History, Settings } from 'lucide-react'

export default function Sidebar() {
  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/audit/new', label: 'New Filing Audit', icon: FileSearch },
    { to: '/audit/review', label: 'Human Review', icon: CheckSquare },
    { to: '/history', label: 'Audit History', icon: History },
  ]

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Auditor Workspace
        </div>
        {links.map((link) => {
          const Icon = link.icon
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span>{link.label}</span>
            </NavLink>
          )
        })}
      </div>

      <div className="pt-4 border-t border-slate-800 text-xs text-slate-500 px-3">
        <p className="font-semibold text-slate-400">Agentic Filing Auditor</p>
        <p>Phase 1 Foundation</p>
      </div>
    </aside>
  )
}
