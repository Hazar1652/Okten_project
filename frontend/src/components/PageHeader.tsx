import type { ReactNode } from 'react'

type Props = {
  title: string
  lead?: string
  children?: ReactNode
}

export default function PageHeader({ title, lead, children }: Props) {
  return (
    <header className="page-header">
      <div className="page-header-text">
        <h1>{title}</h1>
        {lead && <p className="page-lead">{lead}</p>}
      </div>
      {children && <div className="page-header-actions">{children}</div>}
    </header>
  )
}
