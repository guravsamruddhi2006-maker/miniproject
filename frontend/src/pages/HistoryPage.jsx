import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, Clock, Eye, AlertTriangle, Loader2, ArrowRight } from 'lucide-react'
import { api } from '../services/api'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await api.audit.history()
        setHistory(data)
      } catch (err) {
        setError(err.message || 'Failed to load audit history.')
      } finally {
        setLoading(false)
      }
    }
    loadHistory()
  }, [])

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center space-x-1 bg-emerald-50 text-emerald-700 text-xs px-2.5 py-1 rounded-full font-semibold border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Approved</span>
          </span>
        )
      case 'PENDING_REVIEW':
        return (
          <span className="inline-flex items-center space-x-1 bg-amber-50 text-amber-700 text-xs px-2.5 py-1 rounded-full font-semibold border border-amber-200">
            <Clock className="w-3.5 h-3.5" />
            <span>Pending Review</span>
          </span>
        )
      case 'REJECTED':
        return (
          <span className="inline-flex items-center space-x-1 bg-red-50 text-red-700 text-xs px-2.5 py-1 rounded-full font-semibold border border-red-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Rejected</span>
          </span>
        )
      default:
        return <span className="text-xs font-semibold text-slate-600">{status}</span>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Audit History & Trail</h1>
          <p className="text-sm text-slate-500">Permanent record of audited financial filings and human decisions</p>
        </div>
        <Link
          to="/audit/new"
          className="inline-flex items-center space-x-2 bg-brand-600 hover:bg-brand-700 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm shadow-sm"
        >
          <span>New Audit</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
          <p className="text-sm text-slate-500 font-medium">Fetching historical audit records...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
          {error}
        </div>
      ) : history.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3">
          <p className="text-slate-600 font-medium">No financial filings have been audited yet.</p>
          <Link
            to="/audit/new"
            className="inline-block px-4 py-2 bg-brand-600 text-white text-sm font-semibold rounded-lg"
          >
            Run Your First Audit
          </Link>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-xs uppercase tracking-wider text-left">
              <tr>
                <th className="px-6 py-3.5">Filing / Ticker</th>
                <th className="px-6 py-3.5">Fiscal Year</th>
                <th className="px-6 py-3.5">Audit Status</th>
                <th className="px-6 py-3.5">AI Confidence</th>
                <th className="px-6 py-3.5">Metrics Extracted</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-bold text-slate-900">{item.ticker} ({item.filing_type})</div>
                    <div className="text-xs text-slate-400">Audit #{item.id}</div>
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-700">{item.year}</td>
                  <td className="px-6 py-4">{getStatusBadge(item.status)}</td>
                  <td className="px-6 py-4 font-mono font-medium text-slate-700">
                    {Math.round(item.confidence_overall * 100)}%
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-600">
                    {item.metrics?.length || 8} metrics
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/audit/review?id=${item.id}`}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-600 hover:text-brand-800 bg-brand-50 hover:bg-brand-100 px-3 py-1.5 rounded-lg transition-colors border border-brand-200"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect</span>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
