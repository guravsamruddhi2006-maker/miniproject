import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Check, XCircle, ShieldAlert, CheckCircle2, RotateCcw, Loader2, ArrowLeft, AlertCircle } from 'lucide-react'
import { api } from '../services/api'
import MetricCard from '../components/audit/MetricCard'
import ReviewModal from '../components/audit/ReviewModal'

export default function AuditReviewPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const auditId = searchParams.get('id')

  const [audit, setAudit] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const [selectedMetric, setSelectedMetric] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    async function fetchAudit() {
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
      } catch (err) {
        setError(err.message || 'Failed to fetch audit data.')
      } finally {
        setLoading(false)
      }
    }
    fetchAudit()
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
        reviewer_notes: m.validation_notes || 'Approved by human reviewer',
      }))

      const payload = {
        overall_decision: 'APPROVE',
        metric_updates: updates,
        comments: 'All 8 metrics validated and confirmed against filing.',
      }

      const updated = await api.audit.submitReview(audit.id, payload)
      setAudit(updated)
      setMetrics(updated.metrics || [])
      setSuccessMsg('Audit approved successfully! Changes saved to the permanent audit trail.')
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
        comments: 'Filing rejected due to unresolvable accounting inconsistencies.',
      }
      const updated = await api.audit.submitReview(audit.id, payload)
      setAudit(updated)
      setMetrics(updated.metrics || [])
      setSuccessMsg('Filing has been marked as REJECTED.')
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
          <div className="flex items-center space-x-3">
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
          <p className="text-sm text-slate-500 mt-1">
            Audit ID #{audit?.id} • Overall Confidence: {(audit?.confidence_overall * 100).toFixed(0)}% • Human-in-the-Loop Console
          </p>
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
              <span>View Audit History</span>
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
            <p className="font-bold">Human Intervention Checkpoint Triggered</p>
            <p className="text-amber-800 mt-0.5">
              {flaggedCount} metric(s) have confidence scores below 85% or triggered an accounting equation variance. Click <strong>Modify</strong> to inspect filing snippets and correct values.
            </p>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {metrics.map((metric, idx) => (
          <MetricCard
            key={idx}
            metric={metric}
            onEdit={handleEditClick}
          />
        ))}
      </div>

      <ReviewModal
        isOpen={isModalOpen}
        metric={selectedMetric}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveMetric}
      />
    </div>
  )
}
