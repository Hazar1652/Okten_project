import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import VenueCard from '../components/VenueCard'
import VenueFilters, {
  emptyVenueFilters,
  venueFiltersToParams,
  type VenueFilterState,
} from '../components/VenueFilters'
import VenuesBrowseMap from '../components/VenuesBrowseMap'
import { cmsApi, type TopCategory } from '../api/cms.api'
import { featuresApi } from '../api/features.api'
import { tagsApi } from '../api/tags.api'
import { venuesApi } from '../api/venues.api'
import { useAuth } from '../store/authContext'
import type { Tag, Venue, VenueFeature } from '../types/api'

export default function HomePage() {
  const { isSuperAdmin } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [venues, setVenues] = useState<Venue[]>([])
  const [topVenues, setTopVenues] = useState<Venue[]>([])
  const [topCategories, setTopCategories] = useState<TopCategory[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [features, setFeatures] = useState<VenueFeature[]>([])
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState<VenueFilterState>(emptyVenueFilters)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null)
  const [locating, setLocating] = useState(false)
  const [nextPage, setNextPage] = useState<number | null>(null)
  const cardRefs = useRef<Record<number, HTMLDivElement | null>>({})
  const initialTagApplied = useRef(false)

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) return
    setLocating(true)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setLocating(false)
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }, [])

  const load = useCallback(
    (
      searchQ?: string,
      filterState: VenueFilterState = emptyVenueFilters,
      coords = userCoords,
      pageNum = 1,
      append = false,
    ) => {
      setLoading(true)
      setError('')
      const params = { ...venueFiltersToParams(filterState, searchQ, coords), page: pageNum }
      venuesApi
        .list(params)
        .then((res) => {
          const items = res.data.results.filter((v) => v.status === 'published')
          setVenues((prev) => (append ? [...prev, ...items] : items))
          setSelectedId((prev) => (prev && items.some((v) => v.id === prev) ? prev : null))
          setNextPage(res.data.next ? pageNum + 1 : null)
        })
        .catch(() =>
          setError(
            'Не вдалося завантажити заклади. Перевір, чи працює backend (Docker або runserver).',
          ),
        )
        .finally(() => setLoading(false))
    },
    [userCoords],
  )

  useEffect(() => {
    load(undefined, emptyVenueFilters)

    void Promise.all([
      tagsApi.list().then((res) => setTags(res.data.results)).catch(() => setTags([])),
      featuresApi.list().then((res) => setFeatures(res.data.results)).catch(() => setFeatures([])),
      cmsApi
        .listTopCategories()
        .then((res) => setTopCategories(res.data.results.filter((c) => c.is_active)))
        .catch(() => setTopCategories([])),
    ]).then(() => {
      venuesApi
        .list({ ordering: '-rating_avg', min_rating: 3 })
        .then((res) => {
          const items = res.data.results.filter((v) => v.status === 'published').slice(0, 4)
          setTopVenues(items)
        })
        .catch(() => setTopVenues([]))
    })
  }, [load])

  useEffect(() => {
    const tagParam = searchParams.get('tag')
    if (!tagParam || initialTagApplied.current || tags.length === 0) return
    const tagId = Number(tagParam)
    if (!Number.isNaN(tagId) && tags.some((t) => t.id === tagId)) {
      initialTagApplied.current = true
      const next = { ...emptyVenueFilters, tagIds: [tagId] }
      setFilters(next)
      load(search.trim() || undefined, next)
    }
  }, [searchParams, tags, load, search])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    load(search.trim() || undefined, filters, userCoords, 1, false)
  }

  const applyFilters = () => load(search.trim() || undefined, filters, userCoords, 1, false)

  const resetFilters = () => {
    setFilters(emptyVenueFilters)
    setSearchParams({})
    load(search.trim() || undefined, emptyVenueFilters, userCoords, 1, false)
  }

  const selectVenue = (id: number) => {
    setSelectedId(id)
    cardRefs.current[id]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }

  const applyTagFilter = (tagId: number) => {
    const next = { ...emptyVenueFilters, tagIds: [tagId] }
    setFilters(next)
    setSearchParams({ tag: String(tagId) })
    load(undefined, next, userCoords, 1, false)
    document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div>
      {isSuperAdmin && (
        <div className="admin-banner">
          Ви увійшли як адмін. Заклади на модерації — у{' '}
          <Link to="/admin">панелі адміна</Link>.
        </div>
      )}

      <section className="hero">
        <PageHeader
          title="Знайди своє місце"
          lead="Бари, кафе та заклади з відгуками, новинами та зустрічами «пиячок»."
        />
      </section>

      {topVenues.length > 0 && (
        <section className="section top-section" id="top">
          <h2 className="section-title">Топ закладів</h2>
          <p className="muted section-lead">Найкращі за рейтингом відвідувачів</p>
          <div className="card-grid top-grid">
            {topVenues.map((v, i) => (
              <div key={v.id} className="top-card-wrap">
                <span className="top-rank">#{i + 1}</span>
                <VenueCard venue={v} />
              </div>
            ))}
          </div>
          {(topCategories.length > 0 || tags.length > 0) && (
            <div className="filter-group" style={{ marginTop: '1.25rem' }}>
              <span className="filter-label">Топ-категорії</span>
              <div className="filter-chips">
                {topCategories.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    className="filter-chip"
                    disabled={!c.tag_id}
                    onClick={() => c.tag_id && applyTagFilter(c.tag_id)}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      <section id="catalog">
        <form className="search-bar" onSubmit={handleSearch}>
          <input
            type="search"
            placeholder="Пошук за назвою або адресою..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Пошук закладів"
          />
          <button type="submit" className="btn btn-primary">
            Шукати
          </button>
        </form>

        <VenueFilters
          tags={tags}
          features={features}
          filters={filters}
          onChange={setFilters}
          onApply={applyFilters}
          onReset={resetFilters}
          userCoords={userCoords}
          onRequestLocation={requestLocation}
          locating={locating}
        />
      </section>

      {loading && venues.length === 0 && (
        <div className="card-grid" aria-busy="true">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card skeleton" />
          ))}
        </div>
      )}
      {error && <p className="error">{error}</p>}

      {!loading && !error && venues.length === 0 && (
        <p className="muted">За цими критеріями закладів не знайдено. Спробуй інші фільтри.</p>
      )}

      {venues.length > 0 && (
        <>
          <p className="muted results-count">
            {venues.length} {venues.length === 1 ? 'заклад' : 'закладів'}
            {venues[0]?.distance_km != null && ' · сортовано за віддаленістю'}
          </p>
          <div className="catalog-layout">
            <VenuesBrowseMap venues={venues} selectedId={selectedId} onSelect={selectVenue} />
            <div className="catalog-list">
              <div className="card-grid">
                {venues.map((v) => (
                  <div
                    key={v.id}
                    ref={(el) => {
                      cardRefs.current[v.id] = el
                    }}
                    className={
                      selectedId === v.id ? 'venue-card-wrap venue-card-wrap-active' : 'venue-card-wrap'
                    }
                  >
                    <VenueCard venue={v} />
                  </div>
                ))}
              </div>
              {nextPage && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ marginTop: '1rem' }}
                  disabled={loading}
                  onClick={() =>
                    load(search.trim() || undefined, filters, userCoords, nextPage, true)
                  }
                >
                  {loading ? '...' : 'Ще заклади'}
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
