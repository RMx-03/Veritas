import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

const StatusIcon = ({ status }) => {
  const map = {
    verified: { Icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' },
    misleading: { Icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100' },
    false: { Icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-100' },
    unknown: { Icon: Info, color: 'text-neutral-600', bg: 'bg-neutral-50', border: 'border-neutral-200' }
  };
  const cfg = map[status] || map.unknown;
  const { Icon } = cfg;
  return <Icon className={`w-5 h-5 ${cfg.color}`} />;
};

const StatusBadge = ({ status }) => {
  const map = {
    verified: { label: 'Verified', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    misleading: { label: 'Misleading', color: 'bg-amber-100 text-amber-800 border-amber-200' },
    false: { label: 'False', color: 'bg-red-100 text-red-800 border-red-200' },
    unknown: { label: 'Unknown', color: 'bg-neutral-100 text-neutral-800 border-neutral-200' }
  };
  const cfg = map[status] || map.unknown;
  return (
    <span className={`text-xs font-semibold px-2 py-1 rounded-full border ${cfg.color}`}>
      {cfg.label}
    </span>
  );
};

const ClaimsAnalysis = ({ claims = [] }) => {
  const hasClaims = Array.isArray(claims) && claims.length > 0;

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-neutral-900 mb-6">Label Claims Verification</h2>

      {!hasClaims && (
        <div className="text-center py-10">
          <div className="w-12 h-12 rounded-full bg-neutral-100 mx-auto flex items-center justify-center mb-3">
            <Info className="w-6 h-6 text-neutral-400" />
          </div>
          <p className="text-sm text-neutral-600">No label claims detected on this product.</p>
        </div>
      )}

      {hasClaims && (
        <div className="space-y-3">
          {claims.map((item, idx) => {
            const status = (item.status || 'unknown').toLowerCase();
            const source = item.source || 'Internal analysis';
            const explanation = item.explanation || 'No explanation provided.';
            return (
              <div key={idx} className={`p-4 rounded-2xl border ${status === 'verified' ? 'border-emerald-100 bg-emerald-50' : status === 'misleading' ? 'border-amber-100 bg-amber-50' : status === 'false' ? 'border-red-100 bg-red-50' : 'border-neutral-200 bg-neutral-50'}`}>
                <div className="flex items-start gap-3">
                  <div className="mt-0.5"><StatusIcon status={status} /></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-neutral-900 truncate">{item.claim || 'Unspecified claim'}</h3>
                      <StatusBadge status={status} />
                      <span className="text-xs text-neutral-500">Source: {source}</span>
                    </div>
                    <p className="text-sm text-neutral-800 mt-1 leading-relaxed">
                      {explanation.length > 280 ? `${explanation.slice(0, 280)}…` : explanation}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ClaimsAnalysis;
