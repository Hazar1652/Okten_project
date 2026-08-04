import { Link } from 'react-router-dom'
import type { Venue } from '../types/api'
import { resolveMediaUrl } from '../utils/mediaUrl'
import { venueTypeLabel } from '../utils/venueTypes'

type Props = {
  venue: Venue
}

export default function VenueCard({ venue }: Props) {
  const initial = venue.name.trim().charAt(0).toUpperCase() || '?'
  const imageSrc = resolveMediaUrl(venue.main_image_url)

  return (
    <article className="card card-venue">
      <Link to={`/venues/${venue.id}`} className="card-cover-link">
        {imageSrc ? (
          <img src={imageSrc} alt="" className="card-cover" loading="lazy" />
        ) : (
          <div className="card-cover card-cover-placeholder" aria-hidden>
            <span className="card-cover-letter">{initial}</span>
          </div>
        )}
      </Link>
      <div className="card-venue-body">
        <div className="card-venue-top">
          {venue.tags && venue.tags.length > 0 ? (
            <div className="card-tags">
              {venue.tags.slice(0, 2).map((t) => (
                <span key={t.id} className="badge">
                  {t.name}
                </span>
              ))}
            </div>
          ) : (
            <span />
          )}
          <span className="badge badge-published">Відкрито</span>
        </div>
        <h2>
          <Link to={`/venues/${venue.id}`}>{venue.name}</Link>
        </h2>
        <p className="card-address">{venue.address}</p>
        <div className="card-venue-meta">
          {venue.rating_avg != null && (
            <span className="rating-pill">★ {venue.rating_avg.toFixed(1)}</span>
          )}
          {venue.venue_type && (
            <span className="muted">{venueTypeLabel(venue.venue_type)}</span>
          )}
          {venue.avg_check && <span className="muted">~{venue.avg_check} грн</span>}
        </div>
      </div>
    </article>
  )
}
