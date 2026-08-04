import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import ClientOnlyMap from './ClientOnlyMap'
import MapErrorBoundary from './MapErrorBoundary'
import '../map/leafletSetup'
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM } from '../map/leafletSetup'
import type { Venue } from '../types/api'
import 'leaflet/dist/leaflet.css'

type Props = {
  venues: Venue[]
  selectedId: number | null
  onSelect: (id: number) => void
}

function FitVenueBounds({ venues }: { venues: Venue[] }) {
  const map = useMap()

  useEffect(() => {
    const points: [number, number][] = []
    for (const v of venues) {
      const lat = Number.parseFloat(v.latitude)
      const lng = Number.parseFloat(v.longitude)
      if (!Number.isNaN(lat) && !Number.isNaN(lng)) {
        points.push([lat, lng])
      }
    }
    if (points.length === 0) {
      map.setView(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM)
      return
    }
    if (points.length === 1) {
      map.setView(points[0], 14)
      return
    }
    map.fitBounds(L.latLngBounds(points), { padding: [32, 32], maxZoom: 14 })
  }, [venues, map])

  return null
}

function parsePosition(v: Venue): [number, number] | null {
  const lat = Number.parseFloat(v.latitude)
  const lng = Number.parseFloat(v.longitude)
  if (Number.isNaN(lat) || Number.isNaN(lng)) return null
  return [lat, lng]
}

export default function VenuesBrowseMap({ venues, selectedId, onSelect }: Props) {
  const mappable = venues.filter((v) => parsePosition(v) !== null)

  return (
    <div className="map-panel map-panel-browse">
      <p className="filter-label" style={{ marginBottom: '0.5rem' }}>
        Карта закладів — обери маркер
      </p>
      <MapErrorBoundary>
        <ClientOnlyMap className="map-leaflet skeleton">
          <MapContainer
            center={DEFAULT_MAP_CENTER}
            zoom={DEFAULT_MAP_ZOOM}
            scrollWheelZoom
            className="map-leaflet"
          >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitVenueBounds venues={mappable} />
        {mappable.map((v) => {
          const pos = parsePosition(v)!
          const isSelected = selectedId === v.id
          return (
            <Marker
              key={v.id}
              position={pos}
              eventHandlers={{
                click: () => onSelect(v.id),
              }}
              opacity={isSelected ? 1 : 0.85}
            >
              <Popup>
                <strong>{v.name}</strong>
                <p style={{ margin: '0.35rem 0', fontSize: '0.85rem' }}>{v.address}</p>
                <Link to={`/venues/${v.id}`} className="btn btn-primary" style={{ display: 'inline-block' }}>
                  Відкрити
                </Link>
              </Popup>
            </Marker>
          )
        })}
          </MapContainer>
        </ClientOnlyMap>
      </MapErrorBoundary>
      {mappable.length === 0 && (
        <p className="muted map-empty-hint">Немає закладів з координатами для карти.</p>
      )}
    </div>
  )
}
