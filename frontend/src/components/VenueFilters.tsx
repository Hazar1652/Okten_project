import type { Tag, VenueFeature, VenueListParams } from '../types/api'
import { VENUE_TYPES } from '../utils/venueTypes'

export type VenueFilterState = {

  tagIds: number[]

  featureIds: number[]

  venueType: string

  minRating: string

  minAvgCheck: string

  maxAvgCheck: string

  ordering: string

}

export const emptyVenueFilters: VenueFilterState = {

  tagIds: [],

  featureIds: [],

  venueType: '',

  minRating: '',

  minAvgCheck: '',

  maxAvgCheck: '',

  ordering: '',

}

type GeoRef = { lat: number; lng: number } | null

type Props = {

  tags: Tag[]

  features: VenueFeature[]

  filters: VenueFilterState

  onChange: (next: VenueFilterState) => void

  onApply: () => void

  onReset: () => void

  userCoords: GeoRef

  onRequestLocation: () => void

  locating: boolean

}

export function venueFiltersToParams(

  filters: VenueFilterState,

  search?: string,

  userCoords?: GeoRef,

): VenueListParams {

  const params: VenueListParams = {}

  if (search?.trim()) params.search = search.trim()

  if (filters.tagIds.length) params.tags = filters.tagIds

  if (filters.featureIds.length) params.features = filters.featureIds

  if (filters.venueType) params.venue_type = filters.venueType

  if (filters.minRating) params.min_rating = Number(filters.minRating)

  if (filters.minAvgCheck) params.min_avg_check = Number(filters.minAvgCheck)

  if (filters.maxAvgCheck) params.max_avg_check = Number(filters.maxAvgCheck)

  if (filters.ordering) params.ordering = filters.ordering

  if (filters.ordering === 'distance_km' && userCoords) {

    params.ref_lat = userCoords.lat

    params.ref_lng = userCoords.lng

  }

  return params

}

export default function VenueFilters({

  tags,

  features,

  filters,

  onChange,

  onApply,

  onReset,

  userCoords,

  onRequestLocation,

  locating,

}: Props) {

  const toggleTag = (id: number) => {

    const tagIds = filters.tagIds.includes(id)

      ? filters.tagIds.filter((t) => t !== id)

      : [...filters.tagIds, id]

    onChange({ ...filters, tagIds })

  }

  const toggleFeature = (id: number) => {

    const featureIds = filters.featureIds.includes(id)

      ? filters.featureIds.filter((f) => f !== id)

      : [...filters.featureIds, id]

    onChange({ ...filters, featureIds })

  }

  const onOrderingChange = (ordering: string) => {

    if (ordering === 'distance_km' && !userCoords) {

      onRequestLocation()

    }

    onChange({ ...filters, ordering })

  }

  return (

    <div className="filter-panel">

      <h3 className="filter-panel-title">Фільтри</h3>

      {tags.length > 0 && (

        <div className="filter-group">

          <span className="filter-label">Теги</span>

          <div className="filter-chips">

            {tags.map((t) => (

              <button

                key={t.id}

                type="button"

                className={`filter-chip ${filters.tagIds.includes(t.id) ? 'filter-chip-active' : ''}`}

                onClick={() => toggleTag(t.id)}

              >

                {t.name}

              </button>

            ))}

          </div>

        </div>

      )}

      {features.length > 0 && (

        <div className="filter-group">

          <span className="filter-label">Особливості</span>

          <div className="filter-chips">

            {features.map((f) => (

              <button

                key={f.id}

                type="button"

                className={`filter-chip ${filters.featureIds.includes(f.id) ? 'filter-chip-active' : ''}`}

                onClick={() => toggleFeature(f.id)}

              >

                {f.name}

              </button>

            ))}

          </div>

        </div>

      )}

      <div className="filter-row">

        <label className="filter-field">

          <span className="filter-label">Тип закладу</span>

          <select
            value={filters.venueType}
            onChange={(e) => onChange({ ...filters, venueType: e.target.value })}
          >
            <option value="">Будь-який</option>
            {VENUE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>

        </label>

        <label className="filter-field">

          <span className="filter-label">Мін. рейтинг</span>

          <select

            value={filters.minRating}

            onChange={(e) => onChange({ ...filters, minRating: e.target.value })}

          >

            <option value="">Будь-який</option>

            <option value="3">3+</option>

            <option value="4">4+</option>

            <option value="4.5">4.5+</option>

          </select>

        </label>

        <label className="filter-field">

          <span className="filter-label">Чек від (грн)</span>

          <input

            type="number"

            min={0}

            value={filters.minAvgCheck}

            onChange={(e) => onChange({ ...filters, minAvgCheck: e.target.value })}

            placeholder="200"

          />

        </label>

        <label className="filter-field">

          <span className="filter-label">Чек до (грн)</span>

          <input

            type="number"

            min={0}

            value={filters.maxAvgCheck}

            onChange={(e) => onChange({ ...filters, maxAvgCheck: e.target.value })}

            placeholder="1500"

          />

        </label>

        <label className="filter-field">

          <span className="filter-label">Сортування</span>

          <select

            value={filters.ordering}

            onChange={(e) => onOrderingChange(e.target.value)}

          >

            <option value="">Новіші</option>

            <option value="-rating_avg">За рейтингом</option>

            <option value="-created_at">За датою публікації</option>

            <option value="name">За назвою (А–Я)</option>

            <option value="-avg_check">Дорожчі</option>

            <option value="avg_check">Дешевші</option>

            <option value="distance_km">За віддаленістю</option>

          </select>

        </label>

      </div>

      {filters.ordering === 'distance_km' && (

        <p className="muted" style={{ margin: '0 0 0.75rem', fontSize: '0.9rem' }}>

          {userCoords

            ? `Геолокація: ${userCoords.lat.toFixed(4)}, ${userCoords.lng.toFixed(4)}`

            : locating

              ? 'Визначаємо ваше місцезнаходження…'

              : 'Для сортування за віддаленістю дозвольте геолокацію.'}

          {!locating && (

            <button

              type="button"

              className="btn btn-ghost"

              style={{ marginLeft: '0.5rem', padding: '0.2rem 0.5rem' }}

              onClick={onRequestLocation}

            >

              Оновити

            </button>

          )}

        </p>

      )}

      <div className="filter-actions">

        <button type="button" className="btn btn-primary" onClick={onApply}>

          Застосувати

        </button>

        <button type="button" className="btn btn-ghost" onClick={onReset}>

          Скинути

        </button>

      </div>

    </div>

  )

}

