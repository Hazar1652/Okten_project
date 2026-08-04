import L from 'leaflet'
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

// Vite не підхоплює дефолтні шляхи іконок Leaflet.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetina,
  iconUrl: icon,
  shadowUrl: iconShadow,
})

export const DEFAULT_MAP_CENTER: [number, number] = [50.4501, 30.5234]
export const DEFAULT_MAP_ZOOM = 6
export const PICKER_ZOOM = 15
