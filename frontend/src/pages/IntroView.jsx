export default function IntroView({ onStart }) {
  return (
    <div>
      <div className="card hero anim">
        <h2>Heat risk for your street, not one number for the whole city</h2>
        <p>
          City alerts report a single temperature for all of Pune. Yet heat stress
          grows with humidity, wind, and sun. It also lands harder in some
          neighborhoods than others. This platform blends live weather, satellite
          heat data, and local vulnerability into zone level risk you can act on.
        </p>
        <button className="primary" onClick={onStart}>Open live map</button>
      </div>
      <div className="statrow anim d1">
        <div className="stat"><b>6</b><span className="small">Pune zones</span></div>
        <div className="stat"><b>72h</b><span className="small">forecast outlook</span></div>
        <div className="stat"><b>3</b><span className="small">views for people, officers, clinics</span></div>
      </div>
      <div className="row">
        <div className="card anim d1">
          <h3>1. Now</h3>
          <p className="small">Wet Bulb Globe Temperature as the primary signal, plus Heat
            Index for your zone. Each reading is checked against this season history,
            so unusually high values get flagged.</p>
        </div>
        <div className="card anim d2">
          <h3>2. Next 72 hours</h3>
          <p className="small">An XGBoost model trained on local weather history forecasts
            zone WBGT at 24, 48, and 72 hours ahead, with the scores shown beside it.</p>
        </div>
        <div className="card anim d3">
          <h3>3. Advice for you</h3>
          <p className="small">Water, rest breaks, and cooling steps tuned to your age,
            activity, and time outdoors. Officers get ranked zones and relief points.
            Clinics get the aggregated outlook.</p>
        </div>
      </div>
      <div className="card anim d4">
        <h3>What goes in</h3>
        <p className="small">Live and forecast weather from Open Meteo. Land surface heat
          from satellite data. Population and elderly vulnerability. Zone maps.
          Vulnerability changes a zone rank, never its temperature reading.</p>
      </div>
    </div>
  );
}
