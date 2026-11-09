import { BAND_COLOR } from '../api.js';

export function RiskGauge({ score, band }) {
  return (
    <div>
      <div className="big" style={{ color: BAND_COLOR[band] }}>{score} — {band}</div>
      <div className="bar"><div style={{ width: `${score}%`, background: BAND_COLOR[band] }} /></div>
    </div>
  );
}

export function WhyRisk({ parts }) {
  if (!parts) return null;
  const rows = [['Thermal hazard', parts.thermal_hazard], ['Historical anomaly', parts.historical_anomaly],
    ['Spatial UHI', parts.spatial_uhi], ['Vulnerability', parts.vulnerability]];
  return (
    <ul className="small">
      {rows.map(([k, v]) => <li key={k}>{k}: {v} pts</li>)}
    </ul>
  );
}

export function ForecastChart({ fc }) {
  if (!fc) return null;
  const vals = [fc['+24h'], fc['+48h'], fc['+72h']];
  const lo = Math.min(...vals) - 1, hi = Math.max(...vals) + 1;
  const X = (i) => 40 + i * 120, Y = (v) => 130 - ((v - lo) / (hi - lo)) * 110;
  return (
    <svg width="400" height="150">
      <polyline fill="none" stroke="#c62828" strokeWidth="2"
        points={vals.map((v, i) => `${X(i)},${Y(v)}`).join(' ')} />
      {vals.map((v, i) => (
        <g key={i}>
          <circle cx={X(i)} cy={Y(v)} r="4" fill="#c62828" />
          <text x={X(i) - 18} y={Y(v) - 10} fontSize="12">{v}°C</text>
          <text x={X(i) - 18} y={145} fontSize="12">+{[24, 48, 72][i]}h</text>
        </g>
      ))}
    </svg>
  );
}
