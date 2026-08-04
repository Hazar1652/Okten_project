import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import AdminRoute from '../components/AdminRoute'
import Layout from '../components/Layout'
import ManagerRoute from '../components/ManagerRoute'
import PrivateRoute from '../components/PrivateRoute'
import AdminPage from '../pages/AdminPage'
import ManagerPage from '../pages/ManagerPage'
import HangoutPage from '../pages/HangoutPage'
import HomePage from '../pages/HomePage'
import LoginPage from '../pages/LoginPage'
import MessagesPage from '../pages/MessagesPage'
import NewsPage from '../pages/NewsPage'
import NewsDetailPage from '../pages/NewsDetailPage'
import NotFoundPage from '../pages/NotFoundPage'
import ProfilePage from '../pages/ProfilePage'
import RegisterPage from '../pages/RegisterPage'
import SitemapPage from '../pages/SitemapPage'
import SitePageView from '../pages/SitePageView'
import VenuePage from '../pages/VenuePage'

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/venues/:id', element: <VenuePage /> },
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
      { path: '/news', element: <NewsPage /> },
      { path: '/news/:id', element: <NewsDetailPage /> },
      { path: '/hangout', element: <HangoutPage /> },
      { path: '/pages/:slug', element: <SitePageView /> },
      { path: '/sitemap', element: <SitemapPage /> },
      {
        element: <PrivateRoute />,
        children: [
          { path: '/profile', element: <ProfilePage /> },
          { path: '/messages', element: <MessagesPage /> },
          { path: '/messages/:id', element: <MessagesPage /> },
        ],
      },
      {
        element: <AdminRoute />,
        children: [{ path: '/admin', element: <AdminPage /> }],
      },
      {
        element: <ManagerRoute />,
        children: [{ path: '/manager', element: <ManagerPage /> }],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
