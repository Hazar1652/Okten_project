import { useEffect, useState, type ReactNode } from 'react'

type Props = {
  children: ReactNode
  className?: string
}

export default function ClientOnlyMap({ children, className }: Props) {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setReady(true)
  }, [])

  if (!ready) {
    return <div className={className ?? 'map-leaflet skeleton'} aria-hidden />
  }

  return children
}
