import { useEffect, useState } from 'react';
import { api, BAND_COLOR } from '../api.js';

function Pill({ band }) {
  return <span className="pill" style={{ background: BAND_COLOR[band] }}>{band}</span>;
}

export function MunicipalView() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState('');
  useEffect(() => {
    api.municipal().then(setData).catch(() => setErr('Backend down. Start it on :8000.'));
  }, []);
  if (err) return <div className="card down">{err}</div>;
  if (!data) return <div className="card">Loading…</div>;
  if (!data.ranking.length) return <div className="card">No zone data yet.</div>;
  const top = data.ranking[0];
  const hot = data.ranking.filter((r) => r.band === 'High' || r.band === 'Extreme').length;
  return (
    <div>
      <div className="card hero anim">
        <h3>Officer view: where to act first</h3>
        <p className="small">Zones ranked by live risk score, with satellite heat context
          and nearby cooling and water points for each one.</p>
      </div>
      <div className="statrow anim d1">
        <div className="stat"><b>{top.name}</b><span className="small">highest risk right now</span></div>
        <div className="stat"><b>{top.score}</b><span className="small">top zone score</span></div>
        <div className="stat"><b>{hot}/{data.ranking.length}</b><span className="small">zones high or above</span></div>
      </div>
      <div className="card anim d2">
        <h3>Zone ranking</h3>
        <table>
          <thead><tr><th>Zone</th><th>WBGT</th><th>Score</th><th>Band</th><th>LST+</th><th>Cooling and water</th></tr></thead>
          <tbody>
            {data.ranking.map((r) => (
              <tr key={r.zone}>
                <td>{r.name}</td><td>{r.wbgt}</td><td>{r.score}</td><td><Pill band={r.band} /></td>
                <td>{r.lst_offset_c}</td>
                <td className="small">{r.pois.map((p) => p.name).join('; ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function HealthcareView() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState('');
  useEffect(() => {
    api.healthcare().then(setData).catch(() => setErr('Backend down. Start it on :8000.'));
  }, []);
  if (err) return <div className="card down">{err}</div>;
  if (!data) return <div className="card">Loading…</div>;
  if (!data.zones.length) return <div className="card">No zone data yet.</div>;
  const top = data.zones.reduce((a, b) => (b.degree_hours > a.degree_hours ? b : a));
  return (
    <div>
      <div className="card hero anim">
        <h3>Clinic view: plan ahead, not panic</h3>
        <p className="small">Aggregated environmental outlook per zone. No patient
          predictions here, only heat exposure and vulnerable areas first.</p>
      </div>
      <div className="statrow anim d1">
        <div className="stat"><b>{top.name}</b><span className="small">longest heat stretch</span></div>
        <div className="stat"><b>{top.degree_hours}</b><span className="small">peak degree hours</span></div>
        <div className="stat"><b>{data.vulnerable_first.length}</b><span className="small">zones watched</span></div>
      </div>
      <div className="card anim d2">
        <h3>72 hour outlook by zone</h3>
        <p className="small">Most vulnerable first: {data.vulnerable_first.join(', ')}</p>
        <table>
          <thead><tr><th>Zone</th><th>+24h</th><th>+48h</th><th>+72h</th><th>Degree hours</th></tr></thead>
          <tbody>
            {data.zones.map((z) => (
              <tr key={z.zone}>
                <td>{z.name}</td><td>{z.forecast_wbgt['+24h']}</td>
                <td>{z.forecast_wbgt['+48h']}</td><td>{z.forecast_wbgt['+72h']}</td>
                <td>{z.degree_hours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
