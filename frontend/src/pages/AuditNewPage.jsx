import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Calendar, FileText, Play, Sparkles, AlertCircle, Loader2, UploadCloud, FileCheck2 } from 'lucide-react'
import { api } from '../services/api'

export default function AuditNewPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('ticker') // 'ticker' | 'upload'
  const [ticker, setTicker] = useState('AAPL')
  const [year, setYear] = useState('2023')
  const [filingType, setFilingType] = useState('10-K')
  const [selectedFile, setSelectedFile] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const quickPicks = [
    { ticker: 'AAPL', label: 'Apple Inc.', defaultYear: '2023' },
    { ticker: 'MSFT', label: 'Microsoft Corp.', defaultYear: '2023' },
    { ticker: 'TSLA', label: 'Tesla, Inc.', defaultYear: '2023' },
    { ticker: 'NVDA', label: 'NVIDIA Corp.', defaultYear: '2024' },
  ]

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a valid PDF file (.pdf).')
        return
      }
      if (file.size > 50 * 1024 * 1024) {
        setError('File size exceeds the 50 MB limit.')
        return
      }
      setError('')
      setSelectedFile(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      let audit
      if (activeTab === 'upload') {
        if (!selectedFile) {
          setError('Please select a PDF financial filing to upload.')
          setIsSubmitting(false)
          return
        }
        const formData = new FormData()
        formData.append('file', selectedFile)
        formData.append('ticker', ticker)
        formData.append('year', year)
        formData.append('filing_type', filingType)

        audit = await api.audit.uploadPdf(formData)
      } else {
        audit = await api.audit.create(ticker, year, filingType)
      }
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
          Autonomous document processing extracts 8 key metrics, reconciles against SEC XBRL facts, and flags anomalies.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          type="button"
          onClick={() => setActiveTab('ticker')}
          className={`pb-3 px-4 font-semibold text-sm border-b-2 transition-colors ${
            activeTab === 'ticker'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          1. Direct EDGAR / Ticker Intake
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`pb-3 px-4 font-semibold text-sm border-b-2 transition-colors flex items-center space-x-1.5 ${
            activeTab === 'upload'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>2. Upload PDF Report (10-K / 10-Q)</span>
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        {error && (
          <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-xs text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {activeTab === 'upload' && (
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-700">
                Upload Corporate Filing (PDF)
              </label>
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-brand-500 transition-colors bg-slate-50">
                <input
                  type="file"
                  id="pdf-upload"
                  accept="application/pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center space-y-2">
                  {selectedFile ? (
                    <>
                      <FileCheck2 className="w-10 h-10 text-emerald-600" />
                      <span className="font-semibold text-sm text-slate-800">{selectedFile.name}</span>
                      <span className="text-xs text-slate-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • Ready for pdfplumber extraction
                      </span>
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-10 h-10 text-slate-400" />
                      <span className="font-semibold text-sm text-slate-700">
                        Click to upload or drag and drop filing PDF
                      </span>
                      <span className="text-xs text-slate-400">PDF up to 50 MB</span>
                    </>
                  )}
                </label>
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Company Information</label>
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
                placeholder="Or enter any ticker (e.g. AAPL, MSFT, TSLA, NVDA)"
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
              <label className="block text-sm font-semibold text-slate-700 mb-2">Filing Type</label>
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
              <span>Multi-Layer Automated Validation</span>
            </div>
            <p className="text-brand-700">
              The agent extracts 8 core metrics, verifies the Balance Sheet equation (Assets = Liabilities + Equity), tests YoY volatility, and performs ground-truth cross-checks against SEC EDGAR XBRL facts.
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
                <span>Extracting, Validating, and Reconciling with XBRL...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>{activeTab === 'upload' ? 'Process Document & Run Audit' : 'Launch Agent Audit'}</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
