import React, { useState, useEffect } from 'react'
import { X, Check, AlertTriangle } from 'lucide-react'

export default function ReviewModal({ isOpen, metric, onClose, onSave }) {
  const [value, setValue] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (metric) {
      setValue(metric.value.toString())
      setNotes(metric.validation_notes || '')
    }
  }, [metric])

  if (!isOpen || !metric) return null

  const handleSave = (e) => {
    e.preventDefault()
    onSave({
      ...metric,
      value: parseFloat(value) || metric.value,
      validation_notes: notes,
      status: 'MANUALLY_EDITED',
    })
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Modify Financial Metric</h3>
            <p className="text-xs text-slate-500">Human-in-the-Loop Override</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Metric Name
            </label>
            <input
              type="text"
              value={metric.name}
              disabled
              className="w-full bg-slate-100 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-600 font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Corrected Numerical Value ({metric.unit})
            </label>
            <input
              type="number"
              step="any"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono font-bold text-slate-900 focus:ring-brand-500 focus:border-brand-500"
              required
            />
          </div>

          {metric.source_snippet && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600">
              <span className="font-semibold block text-slate-700 mb-1">Filing Evidence Snippet:</span>
              <p className="italic font-serif">"{metric.source_snippet}"</p>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Auditor Justification / Notes
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Corrected against Consolidated Statement of Operations Footnote 12."
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center space-x-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold rounded-lg shadow-xs"
            >
              <Check className="w-4 h-4" />
              <span>Apply Modification</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
