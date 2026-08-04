export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface VenueFeature {
  id: number
  name: string
  slug: string
}

export interface Venue {
  id: number
  owner: string
  name: string
  venue_type?: string
  description: string
  address: string
  latitude: string
  longitude: string
  phone_number: string
  email: string
  website: string
  avg_check: string | null
  status: string
  main_image_url?: string | null
  tags?: Tag[]
  features?: VenueFeature[]
  work_time?: Record<string, unknown>
  rating_avg: number | null
  distance_km: number | null
  created_at: string
}

export interface VenueListParams {
  search?: string
  tags?: number[]
  features?: number[]
  venue_type?: string
  min_rating?: number
  min_avg_check?: number
  max_avg_check?: number
  ordering?: string
  status?: string
  mine?: number
  ref_lat?: number
  ref_lng?: number
  page?: number
}

export interface Review {
  id: number
  user: string
  author_role?: string
  venue: number
  venue_name?: string
  rating: number
  text: string
  check_amount: string | null
  created_at: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  phone_number: string | null
  avatar: string | null
  date_joined: string
  is_active?: boolean
}

export interface NewsItem {
  id: number
  venue: number
  venue_name?: string
  title: string
  content?: string
  category: string
  is_paid: boolean
  image_url?: string | null
  published_at: string | null
}

export interface Hangout {
  id: number
  author: string
  venue: number
  venue_name: string
  meeting_date: string
  meeting_time: string
  goal_description: string
  gender_preferences: string
  people_count: number
  payer_type: string
  budget_min: string | null
  budget_max: string | null
  status: string
  contact_me?: string
  warnings?: string[]
}

export interface ChatPeer {
  id: number
  username: string
}

export interface ChatMessage {
  id: number
  conversation: number
  sender: string
  sender_id: number
  body: string
  created_at: string
}

export interface Conversation {
  id: number
  kind: 'venue' | 'hangout'
  venue: number | null
  hangout: number | null
  title: string
  peer: ChatPeer | null
  last_message: ChatMessage | null
  unread_count: number
  created_at: string
  updated_at: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface RegisterResponse extends TokenPair {
  user: User
}
