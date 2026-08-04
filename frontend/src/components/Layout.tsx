import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { messagingApi } from '../api/messaging.api'
import { useAuth } from '../store/authContext'
import { displayName } from '../utils/displayName'

const navClass = ({ isActive }: { isActive: boolean }) => (isActive ? 'active' : undefined)

export default function Layout() {
  const { user, isAuthenticated, isSuperAdmin, logout, loading } = useAuth()
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (!isAuthenticated) {
      setUnread(0)
      return
    }
    let cancelled = false
    const refresh = () => {
      messagingApi
        .unreadCount()
        .then(({ data }) => {
          if (!cancelled) setUnread(data.unread_total)
        })
        .catch(() => {
          /* ignore */
        })
    }
    refresh()
    const timer = window.setInterval(refresh, 15000)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [isAuthenticated])

  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo-wrap">
          <span className="logo">Okten</span>
          <span className="logo-tagline">заклади · новини · пиячок</span>
        </Link>
        <nav className="nav">
          <NavLink to="/" end className={navClass}>
            Заклади
          </NavLink>
          <NavLink to="/#top" className={navClass}>
            Топ
          </NavLink>
          <NavLink to="/news" className={navClass}>
            Новини
          </NavLink>
          <NavLink to="/hangout" className={navClass}>
            Пиячок
          </NavLink>
          {isAuthenticated && (
            <NavLink to="/messages" className={navClass}>
              Повідомлення
              {unread > 0 && <span className="nav-unread">{unread > 99 ? '99+' : unread}</span>}
            </NavLink>
          )}
          {isAuthenticated && (
            <NavLink to="/manager" className={navClass}>
              Мої заклади
            </NavLink>
          )}
          {isSuperAdmin && (
            <NavLink to="/admin" className={navClass}>
              Адмін
            </NavLink>
          )}
        </nav>
        <div className="header-auth">
          {loading ? (
            <span className="muted">...</span>
          ) : isAuthenticated ? (
            <>
              <Link to="/profile" className="header-user" title={user?.email || user?.username}>
                {displayName(user)}
              </Link>
              <button type="button" className="btn btn-ghost" onClick={logout}>
                Вийти
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Увійти</Link>
              <Link to="/register" className="btn btn-primary">
                Реєстрація
              </Link>
            </>
          )}
        </div>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <Link to="/pages/about">Про нас</Link>
        {' · '}
        <Link to="/pages/contacts">Контакти</Link>
        {' · '}
        <Link to="/sitemap">Карта сайту</Link>
        {' · '}
        <a href="/api/docs/" target="_blank" rel="noreferrer">
          API docs
        </a>
      </footer>
    </div>
  )
}
