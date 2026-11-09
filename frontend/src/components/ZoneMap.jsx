import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { BAND_COLOR } from '../api.js';

export default function ZoneMap({ zones, risks, selected, onSelect }) {
  return (
    <MapContainer center={[18.52, 73.85]} zoom={11} style={{ height: 380 }}>
      <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {zones.map((z) => (
        <CircleMarker
          key={z.zone_id}
          center={[Number(z.lat), Number(z.lon)]}
          radius={selected === z.zone_id ? 16 : 11}
          pathOptions={{
            color: BAND_COLOR[risks[z.zone_id] || 'Low'],
            fillOpacity: 0.7,
          }}
          eventHandlers={{ click: () => onSelect(z.zone_id) }}
        >
          <Tooltip>{z.name}: {risks[z.zone_id] || '?'}</Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
