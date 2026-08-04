import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { placesApi, type PlaceDetails } from '../api/places.api'
import { formatCoordinate } from '../utils/coordinates'

export type PlaceFormPatch = {
  name?: string
  address: string
  latitude: string
  longitude: string
  phone_number?: string
}

type Props = {
  address: string
  onAddressChange: (address: string) => void
  onPlaceResolved: (patch: PlaceFormPatch) => void
  disabled?: boolean
}

function newSessionToken(): string {
  return crypto.randomUUID()
}

export default function PlacesAddressInput({
  address,
  onAddressChange,
  onPlaceResolved,
  disabled,
}: Props) {
  const listId = useId()
  const [sessionToken] = useState(newSessionToken)
  const [suggestions, setSuggestions] = useState<{ place_id: string; description: string }[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [resolving, setResolving] = useState(false)
  const [hint, setHint] = useState('')
  const [apiError, setApiError] = useState('')
  const wrapRef = useRef<HTMLDivElement>(null)

  const fetchSuggestions = useCallback(
    async (q: string) => {
      const trimmed = q.trim()
      if (trimmed.length < 2) {
        setSuggestions([])
        setOpen(false)
        return
      }
      setLoading(true)
      setApiError('')
      try {
        const { data } = await placesApi.autocomplete(trimmed, sessionToken)
        setSuggestions(data.suggestions)
        setOpen(data.suggestions.length > 0)
      } catch (err: unknown) {
        const status = (err as { response?: { status?: number; data?: { detail?: string } } })
          ?.response?.status
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail
        if (status === 503) {
          setHint('Google Places не налаштовано на сервері (GOOGLE_PLACES_API_KEY).')
        } else if (status === 502 && detail) {
          setApiError(detail)
        } else {
          setApiError(detail ?? 'Не вдалося отримати підказки.')
        }
        setSuggestions([])
        setOpen(false)
      } finally {
        setLoading(false)
      }
    },
    [sessionToken],
  )

  useEffect(() => {
    const t = window.setTimeout(() => fetchSuggestions(address), 350)
    return () => window.clearTimeout(t)
  }, [address, fetchSuggestions])

  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const selectPlace = async (placeId: string, description: string) => {
    setOpen(false)
    setResolving(true)
    setApiError('')
    onAddressChange(description)
    try {
      const { data } = await placesApi.details(placeId, sessionToken)
      applyDetails(data)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setApiError(detail ?? 'Не вдалося завантажити деталі місця.')
    } finally {
      setResolving(false)
    }
  }

  const applyDetails = (d: PlaceDetails) => {
    const patch: PlaceFormPatch = {
      address: d.address || address,
      latitude: formatCoordinate(d.latitude),
      longitude: formatCoordinate(d.longitude),
    }
    if (d.name) patch.name = d.name
    if (d.phone_number) patch.phone_number = d.phone_number
    onPlaceResolved(patch)
    setHint('Адресу та координати заповнено з Google Places.')
  }

  return (
    <div className="places-field" ref={wrapRef}>
      <label>
        Адреса * (Google Places)
        <input
          value={address}
          onChange={(e) => {
            onAddressChange(e.target.value)
            setHint('')
          }}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          required
          disabled={disabled || resolving}
          placeholder="Почніть вводити назву або адресу..."
          autoComplete="off"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
        />
      </label>
      {loading && <p className="muted places-hint">Пошук...</p>}
      {resolving && <p className="muted places-hint">Завантаження місця...</p>}
      {hint && <p className="muted places-hint">{hint}</p>}
      {apiError && <p className="error places-hint">{apiError}</p>}
      {open && suggestions.length > 0 && (
        <ul id={listId} className="places-suggestions" role="listbox">
          {suggestions.map((s) => (
            <li key={s.place_id}>
              <button
                type="button"
                role="option"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => selectPlace(s.place_id, s.description)}
              >
                {s.description}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
