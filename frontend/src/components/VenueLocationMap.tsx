import { useMemo } from 'react'
import { MapContainer, Marker, TileLayer } from 'react-leaflet'
import ClientOnlyMap from './ClientOnlyMap'
import MapErrorBoundary from './MapErrorBoundary'
import '../map/leafletSetup'
import { PICKER_ZOOM } from '../map/leafletSetup'
import 'leaflet/dist/leaflet.css'

type Props = {
  latitude: string
  longitude: string
  label?: string
}

export default function VenueLocationMap({ latitude, longitude, label }: Props) {
  const center = useMemo(() => {
    const lat = Number.parseFloat(latitude)
    const lng = Number.parseFloat(longitude)
    if (Number.isNaN(lat) || Number.isNaN(lng)) return null
    return [lat, lng] as [number, number]
  }, [latitude, longitude])

  if (!center) return null

  return (
    <div className="map-panel">
      {label && (
        <p className="filter-label" style={{ marginBottom: '0.5rem' }}>
          {label}
        </p>
      )}
      <MapErrorBoundary>
        <ClientOnlyMap className="map-leaflet skeleton">
          <MapContainer center={center} zoom={PICKER_ZOOM} scrollWheelZoom={false} className="map-leaflet">
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={center} />
          </MapContainer>
        </ClientOnlyMap>
      </MapErrorBoundary>
    </div>
  )
}
