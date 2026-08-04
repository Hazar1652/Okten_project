import { Link } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import { useAuth } from '../store/authContext'

type SiteLink = { to: string; label: string; note?: string }
type SiteSection = { title: string; links: SiteLink[] }

export default function SitemapPage() {
  const { isAuthenticated, isSuperAdmin } = useAuth()

  const sections: SiteSection[] = [
    {
      title: 'Каталог',
      links: [
        { to: '/', label: 'Головна — усі заклади' },
        { to: '/#catalog', label: 'Фільтрація і пошук' },
        { to: '/#top', label: 'Топ закладів і топ-категорії' },
      ],
    },
    {
      title: 'Розділи',
      links: [
        { to: '/news', label: 'Новини (Загальні, Акції, Події)' },
        { to: '/hangout', label: 'Пиячок — зустрічі' },
      ],
    },
    {
      title: 'Інформація',
      links: [
        { to: '/pages/about', label: 'Про нас' },
        { to: '/pages/contacts', label: 'Контакти' },
      ],
    },
  ]

  if (isAuthenticated) {
    sections.push({
      title: 'Кабінет',
      links: [
        { to: '/profile', label: 'Профіль, улюблені, мої відгуки й оцінки' },
        { to: '/manager', label: 'Мої заклади, новини, статистика' },
        { to: '/messages', label: 'Повідомлення' },
      ],
    })
  } else {
    sections.push({
      title: 'Акаунт',
      links: [
        { to: '/login', label: 'Вхід' },
        { to: '/register', label: 'Реєстрація' },
      ],
    })
  }

  if (isSuperAdmin) {
    sections.push({
      title: 'Адміністрування',
      links: [
        { to: '/admin', label: 'Модерація, заклади, користувачі, аналітика, контент' },
      ],
    })
  }

  return (
    <div>
      <PageHeader title="Карта сайту" lead="Усі розділи додатку в одному місці." />
      <div className="card-grid section">
        {sections.map((section) => (
          <article key={section.title} className="card">
            <h2>{section.title}</h2>
            <ul className="sitemap-list">
              {section.links.map((link) => (
                <li key={link.to + link.label}>
                  <Link to={link.to}>{link.label}</Link>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </div>
  )
}
