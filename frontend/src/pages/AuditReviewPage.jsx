import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import {
  Check,
  XCircle,
  ShieldAlert,
  CheckCircle2,
  RotateCcw,
  Loader2,
  ArrowLeft,
  AlertCircle,
  FileText,
  History,
  Scale,
  Award,
} from 'lucide-react'
import { api } from '../services/api'
import MetricCard from '../components/audit/MetricCard'
import ReviewModal from '../components/audit/ReviewModal'

export default function AuditReviewPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const auditId = searchParams.get('id')

  const [audit, setAudit] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [logs, setLogs] = useState([])
  const [xbrlReport, setXbrlReport] = useState(null)
  const [viewTab, setViewTab] = useState('metrics') // 'metrics' | 'xbrl' | 'logs'
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [reviewerComments, setReviewerComments] = useState('')
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const [selectedMetric, setSelectedMetric] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    async function fetchAuditData() {
      setLoading(true)
      setError('')
      try {
        let data
        if (auditId) {
          data = await api.audit.get(auditId)
        } else {
          data = await api.audit.getSample()
        }
        setAudit(data)
        setMetrics(data.metrics || [])
        setLogs(data.logs || [])

        // Fetch XBRL Reconciliation report
        try {
          const xbrl = await api.audit.getXbrlReconciliation(data.id)
          setXbrlReport(xbrl)
        } catch (e) {
          console.warn('XBRL report fetch error:', e)
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch audit data.')
      } finally {
        setLoading(false)
      }
    }
    fetchAuditData()
  }, [auditId])

  const handleEditClick = (metric) => {
    setSelectedMetric(metric)
    setIsModalOpen(true)
  }

  const handleSaveMetric = (updatedMetric) => {
    setMetrics((prev) =>
      prev.map((m) => (m.name === updatedMetric.name ? updatedMetric : m))
    )
  }

  const handleApprove = async () => {
    if (!audit) return
    setSubmitting(true)
    setError('')
    try {
      const updates = metrics.map((m) => ({
        metric_name: m.name,
        decision: m.status === 'MANUALLY_EDITED' ? 'EDIT' : 'APPROVE',
        corrected_value: m.value,
        reviewer_notes: m.validation_notes || 'Verified by human reviewer',
      }))

      const payload = {
        overall_decision: 'APPROVE',
        metric_updates: updates,
        comments: reviewerComments || 'All metrics confirmed and reconciled against filing.',
      }

      const updated = await api.audit.submitReview(audit.id, payload)
      setAudit(updated)
      setMetrics(updated.metrics || [])
      setLogs(updated.logs || [])
      setSuccessMsg('Audit approved successfully! Changes recorded in the append-only audit log.')
    } catch (err) {
      setError(err.message || 'Failed to submit review.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleReject = async () => {
    if (!audit) return
    setSubmitting(true)
    setError('')
    try {
      const payload = {
        overall_decision: 'REJECT',
        metric_updates: [],
        comments: reviewerComments || 'Filing rejected due to discrepancies.',
      }
      const updated = await api.audit.submitReview(audit.id, payload)
      setAudit(updated)
      setMetrics(updated.metrics || [])
      setLogs(updated.logs || [])
      setSuccessMsg('Filing has been marked as REJECTED in the audit trail.')
    } catch (err) {
      setError(err.message || 'Failed to reject filing.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Loading filing audit and metrics...</p>
      </div>
    )
  }

  if (error && !audit) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <div className="inline-flex p-3 bg-red-50 text-red-600 rounded-full">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-lg font-bold text-slate-900">Failed to Load Audit</h2>
        <p className="text-sm text-slate-500">{error}</p>
        <button
          onClick={() => navigate('/audit/new')}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Start a New Audit</span>
        </button>
      </div>
    )
  }

  const flaggedCount = metrics.filter((m) => m.status === 'FLAGGED').length
  const isApproved = audit?.status === 'APPROVED' || audit?.status === 'COMPLETED'
  const isRejected = audit?.status === 'REJECTED'

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 flex-wrap gap-y-1">
            <h1 className="text-2xl font-bold text-slate-900">
              Audit Review: {audit?.ticker} ({audit?.year} {audit?.filing_type})
            </h1>
            {audit?.status === 'PENDING_REVIEW' && (
              <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-full border border-amber-200">
                PAUSED FOR REVIEW
              </span>
            )}
            {isApproved && (
              <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded-full border border-emerald-200 flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>AUDIT APPROVED</span>
              </span>
            )}
            {isRejected && (
              <span className="bg-red-100 text-red-800 text-xs font-bold px-2.5 py-1 rounded-full border border-red-200">
                REJECTED
              </span>
            )}
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1 flex-wrap">
            <span>Audit #{audit?.id}</span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Scale className="w-3.5 h-3.5 text-brand-600" />
              <span>AI Confidence: {(audit?.confidence_overall * 100).toFixed(0)}%</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1 text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              <Award className="w-3.5 h-3.5 text-emerald-600" />
              <span>XBRL Ground-Truth Match: {audit?.xbrl_accuracy}%</span>
            </span>
            {audit?.document_filename && (
              <>
                <span>•</span>
                <span className="flex items-center space-x-1 text-slate-600 font-medium">
                  <FileText className="w-3.5 h-3.5" />
                  <span>Document: {audit.document_filename}</span>
                </span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {!isApproved && !isRejected ? (
            <>
              <button
                onClick={handleReject}
                disabled={submitting}
                className="inline-flex items-center space-x-1.5 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-red-50 hover:text-red-700 transition-colors disabled:opacity-50"
              >
                <XCircle className="w-4 h-4 text-red-500" />
                <span>Reject Filing</span>
              </button>
              <button
                onClick={handleApprove}
                disabled={submitting}
                className="inline-flex items-center space-x-1.5 px-4 py-2 border border-transparent rounded-lg text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm transition-colors disabled:opacity-50"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                <span>Approve & Finalize</span>
              </button>
            </>
          ) : (
            <button
              onClick={() => navigate('/history')}
              className="inline-flex items-center space-x-1.5 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-slate-50"
            >
              <span>Back to History</span>
            </button>
          )}
        </div>
      </div>

      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-3 text-emerald-900 shadow-xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div className="text-sm font-semibold">{successMsg}</div>
        </div>
      )}

      {audit?.status === 'PENDING_REVIEW' && flaggedCount > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start space-x-3 text-amber-900 shadow-xs">
          <ShieldAlert className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
          <div className="text-sm">
            <p className="font-bold">Human Review Checkpoint Active</p>
            <p className="text-amber-800 mt-0.5">
              {flaggedCount} metric(s) have confidence scores below 85% or triggered an accounting equation variance. Click <strong>Modify</strong> to inspect the filing snippet and adjust values before approving.
            </p>
          </div>
        </div>
      )}

      {/* Navigation sub-tabs */}
      <div className="flex border-b border-slate-200">
        <button
          type="button"
          onClick={() => setViewTab('metrics')}
          className={`pb-2.5 px-4 font-semibold text-sm border-b-2 transition-colors ${
            viewTab === 'metrics'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Extracted Financial Metrics ({metrics.length})
        </button>
        <button
          type="button"
          onClick={() => setViewTab('xbrl')}
          className={`pb-2.5 px-4 font-semibold text-sm border-b-2 transition-colors flex items-center space-x-1.5 ${
            viewTab === 'xbrl'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Award className="w-4 h-4" />
          <span>SEC XBRL Reconciliation</span>
        </button>
        <button
          type="button"
          onClick={() => setViewTab('logs')}
          className={`pb-2.5 px-4 font-semibold text-sm border-b-2 transition-colors flex items-center space-x-1.5 ${
            viewTab === 'logs'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Append-Only Audit Trail ({logs.length})</span>
        </button>
      </div>

      {viewTab === 'metrics' && (
        <div className="space-y-4">
          <div className="space-y-3">
            {metrics.map((metric, idx) => (
              <MetricCard
                key={idx}
                metric={metric}
                onEdit={handleEditClick}
              />
            ))}
          </div>

          {!isApproved && !isRejected && (
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Auditor Decision Notes (Will be permanently logged)
              </label>
              <textarea
                rows={2}
                value={reviewerComments}
                onChange={(e) => setReviewerComments(e.target.value)}
                placeholder="Enter sign-off comments or explanation for modifications..."
                className="w-full border border-slate-300 rounded-lg p-2.5 text-sm text-slate-900 focus:ring-brand-500 focus:border-brand-500"
              />
            </div>
          )}
        </div>
      )}

      {viewTab === 'xbrl' && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">
                SEC EDGAR XBRL Ground-Truth Comparison
              </h3>
              <p className="text-xs text-slate-500">
                Official XBRL facts pulled from SEC Form 10-K company facts API
              </p>
            </div>
            <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Overall Accuracy: {xbrlReport?.overall_accuracy_percentage || audit?.xbrl_accuracy}%
            </span>
          </div>

          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-xs uppercase tracking-wider text-left">
              <tr>
                <th className="px-6 py-3.5">Financial Metric</th>
                <th className="px-6 py-3.5">Extracted Value</th>
                <th className="px-6 py-3.5">SEC XBRL Fact</th>
                <th className="px-6 py-3.5">Variance</th>
                <th className="px-6 py-3.5">Reconciliation Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white font-mono text-xs">
              {xbrlReport?.items?.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="px-6 py-3.5 font-sans font-semibold text-slate-900">{item.metric_name}</td>
                  <td className="px-6 py-3.5 text-slate-800 font-bold">
                    ${(item.extracted_value / 1e9).toFixed(2)}B
                  </td>
                  <td className="px-6 py-3.5 text-slate-600">
                    {item.xbrl_value ? `$${(item.xbrl_value / 1e9).toFixed(2)}B` : 'N/A'}
                  </td>
                  <td className="px-6 py-3.5 text-slate-500 font-sans">
                    {item.percentage_diff.toFixed(2)}%
                  </td>
                  <td className="px-6 py-3.5 font-sans">
                    {item.verified ? (
                      <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded text-xs font-semibold border border-emerald-200">
                        {item.status}
                      </span>
                    ) : (
                      <span className="bg-amber-50 text-amber-700 px-2 py-0.5 rounded text-xs font-semibold border border-amber-200">
                        {item.status}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewTab === 'logs' && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
            <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">
              Immutable Append-Only Audit Trail
            </h3>
            <p className="text-xs text-slate-500">
              Permanent chronological record of automated ingestion, checkpoint triggers, and human decisions
            </p>
          </div>

          <div className="divide-y divide-slate-200">
            {logs.map((log) => (
              <div key={log.id} className="p-4 sm:p-5 hover:bg-slate-50/50 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold bg-slate-100 text-slate-800 px-2 py-0.5 rounded border border-slate-200">
                        {log.action}
                      </span>
                      {log.metric_name && (
                        <span className="text-xs font-semibold text-slate-700">
                          {log.metric_name}
                        </span>
                      )}
                      {log.previous_value !== null && log.new_value !== null && (
                        <span className="text-xs font-mono text-slate-500">
                          (${log.previous_value?.toLocaleString()} → ${log.new_value?.toLocaleString()})
                        </span>
                      )}
                    </div>
                    {log.comments && (
                      <p className="text-xs text-slate-600 italic">"{log.comments}"</p>
                    )}
                  </div>
                  <div className="text-right text-xs text-slate-400">
                    <div>{log.reviewer_email || 'system@agent'}</div>
                    <div>{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <ReviewModal
        isOpen={isModalOpen}
        metric={selectedMetric}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveMetric}
      />
    </div>
  )
}
