import { useEffect, useMemo } from 'react'
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from 'react-leaflet'
import ClientOnlyMap from './ClientOnlyMap'
import MapErrorBoundary from './MapErrorBoundary'
import '../map/leafletSetup'
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, PICKER_ZOOM } from '../map/leafletSetup'
import { formatCoordinate } from '../utils/coordinates'
import 'leaflet/dist/leaflet.css'

type Props = {
  latitude: string
  longitude: string
  onCoordinatesChange: (lat: string, lng: string) => void
}

function MapClickHandler({ onPick }: { onPick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

function MapRecenter({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, zoom, { animate: true })
  }, [center, zoom, map])
  return null
}

function parseCoord(value: string, fallback: number): number {
  const n = Number.parseFloat(value)
  return Number.isNaN(n) ? fallback : n
}

export default function VenueMapPicker({ latitude, longitude, onCoordinatesChange }: Props) {
  const hasPoint = latitude.trim() !== '' && longitude.trim() !== ''

  const center = useMemo<[number, number]>(
    () => [
      parseCoord(latitude, DEFAULT_MAP_CENTER[0]),
      parseCoord(longitude, DEFAULT_MAP_CENTER[1]),
    ],
    [latitude, longitude],
  )

  const zoom = hasPoint ? PICKER_ZOOM : DEFAULT_MAP_ZOOM

  const handlePick = (lat: number, lng: number) => {
    onCoordinatesChange(formatCoordinate(lat), formatCoordinate(lng))
  }

  return (
    <div className="map-panel map-panel-picker">
      <p className="filter-label" style={{ marginBottom: '0.5rem' }}>
        Мінікарта — клікни, щоб поставити точку
      </p>
      <MapErrorBoundary>
        <ClientOnlyMap className="map-leaflet skeleton">
          <MapContainer center={center} zoom={zoom} scrollWheelZoom className="map-leaflet">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapClickHandler onPick={handlePick} />
            <MapRecenter center={center} zoom={zoom} />
            {hasPoint && <Marker position={center} />}
          </MapContainer>
        </ClientOnlyMap>
      </MapErrorBoundary>
    </div>
  )
}
