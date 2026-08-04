const DEMO_LAT = 50.4501
const DEMO_LNG = 30.5234
const COORD_EPS = 0.0001

const NON_KYIV_MARKERS = ['львів', 'lviv', 'одес', 'odesa', 'харків', 'kharkiv', 'дніпр', 'dnipro']

export function venueCoordsMismatchWarning(address: string, latitude: string, longitude: string): string | null {
  const lat = Number(latitude)
  const lng = Number(longitude)
  if (!address || Number.isNaN(lat) || Number.isNaN(lng)) return null

  const addr = address.toLowerCase()
  const looksNonKyiv = NON_KYIV_MARKERS.some((m) => addr.includes(m))
  if (!looksNonKyiv) return null

  const isDemoKyiv =
    Math.abs(lat - DEMO_LAT) <= COORD_EPS && Math.abs(lng - DEMO_LNG) <= COORD_EPS
  if (!isDemoKyiv) return null

  return (
    'Адреса вказує на місто поза Києвом, а координати — центр Києва (50.45 / 30.52). ' +
    'Вкажи широту й довготу з Google Maps (ПКМ → «Що тут?»), інакше маршрут відкриє не туди.'
  )
}
