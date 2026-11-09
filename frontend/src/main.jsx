import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import IntroView from './pages/IntroView.jsx';
import CitizenView from './pages/CitizenView.jsx';
import { MunicipalView, HealthcareView } from './pages/AuthorityViews.jsx';
import { api } from './api.js';
import './style.css';

function App() {
  const [tab, setTab] = useState('home');
  const [zones, setZones] = useState([]);
  const [zone, setZone] = useState('central');
  const [up, setUp] = useState(false);

  useEffect(() => {
    api.zones().then((z) => { setZones(z); setUp(true); }).catch(() => setUp(false));
  }, []);

  return (
    <div className="wrap">
      <header className="topbar">
        <div>
          <h2>Pune Heat Early Warning</h2>
          <p className="tagline">Hyper-local heat-risk guidance for every zone, for the next 72 hours</p>
        </div>
        {up ? <span className="live">LIVE</span> : <span className="down">BACKEND DOWN</span>}
      </header>
      <div className="tabs">
        <button className={tab === 'home' ? 'on' : ''} onClick={() => setTab('home')}>Home</button>
        <button className={tab === 'citizen' ? 'on' : ''} onClick={() => setTab('citizen')}>Citizen</button>
        <button className={tab === 'municipal' ? 'on' : ''} onClick={() => setTab('municipal')}>Municipal</button>
        <button className={tab === 'health' ? 'on' : ''} onClick={() => setTab('health')}>Healthcare</button>
      </div>
      {tab === 'home' && <IntroView onStart={() => setTab('citizen')} />}
      {tab === 'citizen' && <CitizenView zones={zones} zone={zone} setZone={setZone} />}
      {tab === 'municipal' && <MunicipalView />}
      {tab === 'health' && <HealthcareView />}
      <p className="small">Note: WBGT is an approximation; LST and vulnerability use sample values.
        Guidance is general heat safety, not medical advice.</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
