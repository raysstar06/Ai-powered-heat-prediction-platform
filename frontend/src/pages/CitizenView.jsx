import { useEffect, useState } from 'react';
import ZoneMap from '../components/ZoneMap.jsx';
import { RiskGauge, WhyRisk, ForecastChart } from '../components/widgets.jsx';
import { api, BAND_COLOR } from '../api.js';

export default function CitizenView({ zones, zone, setZone }) {
  const [cur, setCur] = useState(null);
  const [fc, setFc] = useState(null);
  const [adv, setAdv] = useState(null);
  const [err, setErr] = useState('');
  const [bands, setBands] = useState({});
  const [p, setP] = useState({ age: 30, weight: 60, activity: 'rest', duration: 30, exertion: 'light' });

  useEffect(() => {
    setErr('');
    api.current(zone).then(setCur).catch(() => setErr('Backend down. Start it on :8000.'));
    api.forecast(zone).then(setFc).catch(() => {});
  }, [zone]);

  useEffect(() => {
    api.municipal().then((d) => {
      const m = {};
      d.ranking.forEach((r) => { m[r.zone] = r.band; });
      setBands(m);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    api.advisory(zone, p).then(setAdv).catch(() => {});
  }, [zone, cur]);
  const zoneName = (zones.find((z) => z.zone_id === zone) || {}).name || zone;
  return (
    <div>
      {err && <div className="card down">{err}</div>}
      <div className="card hero anim">
        <h3>1. Pick your zone</h3>
        <select value={zone} onChange={(e) => setZone(e.target.value)}>
          {zones.map((z) => <option key={z.zone_id} value={z.zone_id}>{z.name}</option>)}
        </select>
        <p className="small">Tap a map dot or use the list. Every number below follows this zone.</p>
      </div>
      <div className="card anim d1">
        <ZoneMap zones={zones} risks={bands} selected={zone} onSelect={setZone} />
      </div>
      <div className="row">
        <div className="card anim d1">
          <h3>2. Right now in {zoneName}</h3>
          {cur && (<>
            <p>WBGT {cur.wbgt} °C · Heat Index {cur.heat_index} °C</p>
            <p className="small">History p90: {cur.percentiles.p90} °C ·
              {cur.unusual ? ' Unusually high for this period.' : ' Within normal range.'}</p>
            <RiskGauge score={cur.risk.score} band={cur.risk.band} />
            <WhyRisk parts={cur.risk.parts} />
          </>)}
        </div>
        <div className="card anim d2">
          <h3>3. Next 72 hours</h3>
          {fc && (<><ForecastChart fc={fc.forecast_wbgt} />
            <p className="small">Risk {fc.risk.score} ({fc.risk.band}) ·
              Degree-hours {fc.degree_hours}</p></>)}
        </div>
      </div>
      <div className="card anim d3">
        <h3>4. Your heat-safety advisory</h3>
        <p className="small">Same weather, different people, different advice. Try a preset:</p>
        <div className="presets">
          <button onClick={() => setP({ age: 25, weight: 70, activity: 'rest', duration: 15, exertion: 'light' })}>
            Student, brief outing</button>
          <button onClick={() => setP({ age: 65, weight: 62, activity: 'outdoor_work', duration: 240, exertion: 'heavy' })}>
            Elderly outdoor worker</button>
        </div>
        <div className="formgrid">
          <label>Age
            <input type="number" value={p.age} min="1" max="100"
              onChange={(e) => setP({ ...p, age: +e.target.value })} /></label>
          <label>Weight (kg)
            <input type="number" value={p.weight} min="20" max="150"
              onChange={(e) => setP({ ...p, weight: +e.target.value })} /></label>
          <label>Activity
            <select value={p.activity}
              onChange={(e) => setP({ ...p, activity: e.target.value })}>
              <option value="rest">Rest</option><option value="walking">Walking</option>
              <option value="outdoor_work">Outdoor work</option><option value="sports">Sports</option>
            </select></label>
          <label>Minutes outdoors
            <input type="number" value={p.duration} min="5" max="600"
              onChange={(e) => setP({ ...p, duration: +e.target.value })} /></label>
          <label>Exertion
            <select value={p.exertion}
              onChange={(e) => setP({ ...p, exertion: e.target.value })}>
              <option value="light">Light</option><option value="heavy">Heavy</option>
            </select></label>
        </div>
        <button className="primary"
          onClick={() => api.advisory(zone, p).then(setAdv).catch(() => setErr('Backend down.'))}>
          Get advice</button>
        {adv && (
          <div className="adv-result">
            <div className="adv-head">
              <span className="pill" style={{ background: BAND_COLOR[adv.band] }}>{adv.band} risk</span>
              <span className="small">Zone WBGT {adv.wbgt} °C</span>
            </div>
            <div className="water">
              <span className="big">{adv.advisory.water_litres} L</span>
              <span className="small">drink every {adv.advisory.drink_every_min} min</span>
            </div>
            <p><strong>Rest plan.</strong> {adv.advisory.work_rest}</p>
            <p><strong>Cooling.</strong> {adv.advisory.cooling}</p>
            <p className="small"><strong>Warning signs.</strong> {adv.advisory.warning_signs}</p>
            <p className="small dim">{adv.advisory.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
