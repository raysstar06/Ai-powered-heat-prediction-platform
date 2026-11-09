const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

async function get(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

export const api = {
  zones: () => get('/zones'),
  current: (zone) => get(`/risk/current?zone=${zone}`),
  forecast: (zone) => get(`/risk/forecast?zone=${zone}`),
  advisory: (zone, p) =>
    get(`/advisory?zone=${zone}&age=${p.age}&weight=${p.weight}` +
        `&activity=${p.activity}&duration_min=${p.duration}&exertion=${p.exertion}`),
  municipal: () => get('/municipal'),
  healthcare: () => get('/healthcare'),
};

export const BAND_COLOR = { Low: '#2e7d32', Moderate: '#f9a825', High: '#ef6c00', Extreme: '#c62828' };
