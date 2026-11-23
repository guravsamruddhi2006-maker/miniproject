import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Calendar, FileText, Play, Sparkles, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '../services/api'

export default function AuditNewPage() {
  const navigate = useNavigate()
  const [ticker, setTicker] = useState('AAPL')
  const [year, setYear] = useState('2023')
  const [filingType, setFilingType] = useState('10-K')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const quickPicks = [
    { ticker: 'AAPL', label: 'Apple Inc.', defaultYear: '2023' },
    { ticker: 'MSFT', label: 'Microsoft Corp.', defaultYear: '2023' },
    { ticker: 'TSLA', label: 'Tesla, Inc.', defaultYear: '2023' },
    { ticker: 'NVDA', label: 'NVIDIA Corp.', defaultYear: '2024' },
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const audit = await api.audit.create(ticker, year, filingType)
      navigate(`/audit/review?id=${audit.id}`)
    } catch (err) {
      setError(err.message || 'Failed to initiate audit extraction.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Initiate Financial Filing Audit</h1>
        <p className="text-sm text-slate-500">
          Agentic intake fetches corporate 10-K / 10-Q filings, parses structured metrics, and evaluates accounting rules.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        {error && (
          <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-xs text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Select Company</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
              {quickPicks.map((pick) => (
                <button
                  type="button"
                  key={pick.ticker}
                  onClick={() => {
                    setTicker(pick.ticker)
                    setYear(pick.defaultYear)
                  }}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    ticker === pick.ticker
                      ? 'border-brand-600 bg-brand-50 text-brand-900 ring-1 ring-brand-500'
                      : 'border-slate-200 hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <div className="font-bold text-sm">{pick.ticker}</div>
                  <div className="text-[11px] text-slate-500 truncate">{pick.label}</div>
                </button>
              ))}
            </div>

            <div className="relative rounded-lg shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Building2 className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Or type any US ticker (e.g. GOOG, AMZN, META)"
                className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm font-semibold text-slate-900 uppercase focus:ring-brand-500 focus:border-brand-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Fiscal Year</label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Calendar className="w-5 h-5" />
                </div>
                <select
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 focus:ring-brand-500 focus:border-brand-500"
                >
                  <option value="2024">2024 (Annual 10-K)</option>
                  <option value="2023">2023 (Annual 10-K)</option>
                  <option value="2022">2022 (Annual 10-K)</option>
                  <option value="2021">2021 (Annual 10-K)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Document Type</label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <FileText className="w-5 h-5" />
                </div>
                <select
                  value={filingType}
                  onChange={(e) => setFilingType(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 focus:ring-brand-500 focus:border-brand-500"
                >
                  <option value="10-K">10-K (Annual Audited Report)</option>
                  <option value="10-Q">10-Q (Quarterly Unaudited Report)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="p-4 bg-brand-50/70 border border-brand-200 rounded-xl space-y-1.5 text-xs text-brand-900">
            <div className="flex items-center space-x-1.5 font-bold text-brand-800">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <span>Autonomous Agentic Processing</span>
            </div>
            <p className="text-brand-700">
              The agent extracts 8 core metrics, cross-references XBRL facts, checks the Balance Sheet equation, and flags high-volatility YoY figures for human review.
            </p>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running Agent Extraction & Validation...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Launch Agent Audit</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
