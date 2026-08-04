import type { CreateVenuePayload } from '../api/venues.api'
import type { Tag, VenueFeature } from '../types/api'
import { VENUE_TYPES } from '../utils/venueTypes'
import PlacesAddressInput, { type PlaceFormPatch } from './PlacesAddressInput'
import VenueMapPicker from './VenueMapPicker'

type Props = {
  form: CreateVenuePayload
  onChange: (
    key: keyof CreateVenuePayload,
  ) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => void
  onPlaceResolved?: (patch: PlaceFormPatch) => void
  onAddressChange?: (address: string) => void
  onCoordinatesChange?: (lat: string, lng: string) => void
  workTimeDisplay?: string
  onWorkTimeChange?: (value: string) => void
  tags?: Tag[]
  features?: VenueFeature[]
  selectedTagIds?: number[]
  selectedFeatureIds?: number[]
  onToggleTag?: (id: number) => void
  onToggleFeature?: (id: number) => void
}

export default function VenueFormFields({
  form,
  onChange,
  onPlaceResolved,
  onAddressChange,
  onCoordinatesChange,
  workTimeDisplay = '',
  onWorkTimeChange,
  tags = [],
  features = [],
  selectedTagIds = [],
  selectedFeatureIds = [],
  onToggleTag,
  onToggleFeature,
}: Props) {
  const handleAddress = onAddressChange ?? ((value: string) => {
    onChange('address')({ target: { value } } as React.ChangeEvent<HTMLInputElement>)
  })

  return (
    <>
      <label>
        Назва *
        <input value={form.name} onChange={onChange('name')} required />
      </label>

      <label>
        Тип закладу
        <select value={form.venue_type ?? ''} onChange={onChange('venue_type')}>
          {VENUE_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </label>

      {onPlaceResolved ? (
        <PlacesAddressInput
          address={form.address}
          onAddressChange={handleAddress}
          onPlaceResolved={onPlaceResolved}
        />
      ) : (
        <label>
          Адреса *
          <input value={form.address} onChange={onChange('address')} required />
        </label>
      )}

      <label>
        Опис
        <textarea rows={3} value={form.description} onChange={onChange('description')} />
      </label>

      {onWorkTimeChange && (
        <label>
          Графік роботи
          <input
            value={workTimeDisplay}
            onChange={(e) => onWorkTimeChange(e.target.value)}
            placeholder="Пн–Пт 10:00–22:00, Сб–Нд 12:00–00:00"
          />
        </label>
      )}

      <label>
        Широта *
        <input
          value={form.latitude}
          onChange={onChange('latitude')}
          placeholder="заповниться з Google Places"
          required
        />
      </label>
      <label>
        Довгота *
        <input
          value={form.longitude}
          onChange={onChange('longitude')}
          placeholder="заповниться з Google Places"
          required
        />
      </label>
      <p className="muted" style={{ margin: 0 }}>
        Оберіть місце зі списку Google або клікни на мінікарті нижче.
      </p>
      {onCoordinatesChange && (
        <VenueMapPicker
          latitude={form.latitude}
          longitude={form.longitude}
          onCoordinatesChange={onCoordinatesChange}
        />
      )}
      <label>
        Телефон
        <input value={form.phone_number} onChange={onChange('phone_number')} />
      </label>
      <label>
        Email
        <input type="email" value={form.email} onChange={onChange('email')} />
      </label>
      <label>
        Сайт
        <input type="url" value={form.website ?? ''} onChange={onChange('website')} />
      </label>
      <label>
        Середній чек
        <input value={form.avg_check} onChange={onChange('avg_check')} />
      </label>

      {tags.length > 0 && onToggleTag && (
        <div className="filter-group">
          <span className="filter-label">Теги</span>
          <div className="filter-chips">
            {tags.map((t) => (
              <button
                key={t.id}
                type="button"
                className={`filter-chip ${selectedTagIds.includes(t.id) ? 'filter-chip-active' : ''}`}
                onClick={() => onToggleTag(t.id)}
              >
                {t.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {features.length > 0 && onToggleFeature && (
        <div className="filter-group">
          <span className="filter-label">Особливості</span>
          <div className="filter-chips">
            {features.map((f) => (
              <button
                key={f.id}
                type="button"
                className={`filter-chip ${selectedFeatureIds.includes(f.id) ? 'filter-chip-active' : ''}`}
                onClick={() => onToggleFeature(f.id)}
              >
                {f.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </>
  )
}
