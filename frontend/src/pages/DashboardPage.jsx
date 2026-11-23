import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileCheck, AlertTriangle, TrendingUp, Users, ArrowRight, Eye, Sparkles } from 'lucide-react'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.audit.history()
        setHistory(data)
      } catch (err) {
        console.error('Failed to load dashboard history:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const totalAudits = history.length
  const pendingCount = history.filter((h) => h.status === 'PENDING_REVIEW').length
  const approvedCount = history.filter((h) => h.status === 'APPROVED' || h.status === 'COMPLETED').length
  const approvalRate = totalAudits > 0 ? `${Math.round((approvedCount / totalAudits) * 100)}%` : '100%'

  const stats = [
    { label: 'Total Filings Audited', value: totalAudits.toString(), icon: FileCheck, color: 'text-blue-600 bg-blue-50' },
    { label: 'Pending Human Review', value: pendingCount.toString(), icon: AlertTriangle, color: 'text-amber-600 bg-amber-50' },
    { label: 'Reviewer Approval Rate', value: approvalRate, icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50' },
    { label: 'Active Auditor Role', value: user?.role?.toUpperCase() || 'AUDITOR', icon: Users, color: 'text-purple-600 bg-purple-50' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Welcome back, {user?.full_name || 'Auditor'}
          </h1>
          <p className="text-sm text-slate-500">
            Human-in-the-Loop Financial Filing Verification Console • Agentic AI Layer
          </p>
        </div>
        <Link
          to="/audit/new"
          className="inline-flex items-center space-x-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-4 py-2.5 rounded-lg transition-colors text-sm shadow-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>Start New Audit</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon
          return (
            <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex items-center space-x-4">
              <div className={`p-3 rounded-xl ${stat.color}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
                <div className="text-xs font-medium text-slate-500">{stat.label}</div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Recent Filing Audits</h2>
          <Link to="/history" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
            View All ({totalAudits})
          </Link>
        </div>

        {history.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-500">
            No audits recorded yet. Click "Start New Audit" to evaluate a company filing.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {history.slice(0, 5).map((item) => (
              <div key={item.id} className="py-3.5 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-900 text-sm">{item.ticker} ({item.year} {item.filing_type})</div>
                  <div className="text-xs text-slate-400">
                    Confidence: {Math.round(item.confidence_overall * 100)}% • Status: {item.status}
                  </div>
                </div>
                <Link
                  to={`/audit/review?id=${item.id}`}
                  className="inline-flex items-center space-x-1 text-xs font-medium text-brand-600 hover:text-brand-800 bg-brand-50 px-2.5 py-1.5 rounded-lg border border-brand-200"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Inspect</span>
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
