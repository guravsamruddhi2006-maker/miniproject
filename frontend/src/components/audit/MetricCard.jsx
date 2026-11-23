import React from 'react'
import { AlertCircle, CheckCircle2, Edit3, FileText } from 'lucide-react'

export default function MetricCard({ metric, onEdit }) {
  const formatValue = (val, unit) => {
    if (val < 100) return `$${val.toFixed(2)}`
    if (val >= 1e9) return `$${(val / 1e9).toFixed(2)} Billion`
    if (val >= 1e6) return `$${(val / 1e6).toFixed(2)} Million`
    return `${val.toLocaleString()} ${unit}`
  }

  const getConfidenceBadge = (score) => {
    const pct = Math.round(score * 100)
    if (pct >= 85) {
      return (
        <span className="inline-flex items-center space-x-1 bg-emerald-50 text-emerald-700 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-emerald-200">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{pct}% High</span>
        </span>
      )
    }
    if (pct >= 70) {
      return (
        <span className="inline-flex items-center space-x-1 bg-amber-50 text-amber-700 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-amber-200">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{pct}% Review</span>
        </span>
      )
    }
    return (
      <span className="inline-flex items-center space-x-1 bg-red-50 text-red-700 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-red-200">
        <AlertCircle className="w-3.5 h-3.5" />
        <span>{pct}% Flagged</span>
      </span>
    )
  }

  return (
    <div className={`p-5 rounded-xl border transition-all ${
      metric.status === 'FLAGGED'
        ? 'bg-amber-50/40 border-amber-200 shadow-sm'
        : metric.status === 'MANUALLY_EDITED'
        ? 'bg-blue-50/40 border-blue-200'
        : 'bg-white border-slate-200 hover:border-slate-300'
    }`}>
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
            <h3 className="font-semibold text-slate-900 text-base">{metric.name}</h3>
            {getConfidenceBadge(metric.confidence_score)}
            {metric.status === 'FLAGGED' && (
              <span className="bg-red-100 text-red-800 text-[11px] font-bold px-2 py-0.5 rounded">
                Human Review Required
              </span>
            )}
            {metric.status === 'MANUALLY_EDITED' && (
              <span className="bg-blue-100 text-blue-800 text-[11px] font-bold px-2 py-0.5 rounded">
                Auditor Edited
              </span>
            )}
          </div>

          {metric.source_snippet && (
            <div className="flex items-start space-x-1.5 text-xs text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <FileText className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
              <p className="italic font-serif line-clamp-2">"{metric.source_snippet}"</p>
            </div>
          )}

          {metric.validation_notes && (
            <p className="text-xs text-amber-800 font-medium bg-amber-100/70 p-2 rounded border border-amber-200">
              ⚠️ {metric.validation_notes}
            </p>
          )}
        </div>

        <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 pt-2 sm:pt-0 border-t sm:border-0 border-slate-100">
          <div className="text-right">
            <div className="text-lg font-bold font-mono text-slate-900">
              {formatValue(metric.value, metric.unit)}
            </div>
            <div className="text-[11px] text-slate-400 uppercase font-medium">{metric.unit}</div>
          </div>

          <button
            onClick={() => onEdit(metric)}
            className="inline-flex items-center space-x-1 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-brand-50 hover:border-brand-300 hover:text-brand-600 transition-colors shadow-2xs"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Modify</span>
          </button>
        </div>
      </div>
    </div>
  )
}
