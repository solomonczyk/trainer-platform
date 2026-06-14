'use client';

import { tl } from '@/lib/i18n';

interface StatusMeterProps {
  state: Record<string, number>;
  showLabel?: boolean;
}

const METER_BARS = [
  { key: 'risk', label: 'quest.risk', color: 'bg-danger-500', invert: true },
  { key: 'time_remaining', label: 'quest.time_remaining', color: 'bg-primary-500' },
  { key: 'team_trust', label: 'quest.team_trust', color: 'bg-success-500' },
  { key: 'client_trust', label: 'quest.client_trust', color: 'bg-emerald-500' },
  { key: 'evidence_quality', label: 'quest.evidence_quality', color: 'bg-purple-500' },
  { key: 'decision_quality', label: 'quest.decision_quality', color: 'bg-warning-500' },
];

export default function StatusMeter({ state, showLabel = true }: StatusMeterProps) {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
      {METER_BARS.map((bar) => {
        const val = state[bar.key] ?? 0;
        const displayVal = bar.invert ? 100 - val : val;
        return (
          <div key={bar.key} className="text-center">
            <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden shadow-inner">
              <div
                className={`h-full rounded-full transition-all duration-500 ${bar.color}`}
                style={{ width: `${Math.max(0, Math.min(100, displayVal))}%` }}
              />
            </div>
            {showLabel && (
              <p className="mt-1.5 text-caption font-medium text-text-secondary truncate">
                {tl(bar.label)}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
