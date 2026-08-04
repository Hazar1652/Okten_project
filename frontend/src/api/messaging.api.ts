import api from './axiosInstance'
import type { ChatMessage, Conversation } from '../types/api'

export type CreateConversationPayload =
  | { kind: 'venue'; venue_id: number }
  | { kind: 'hangout'; hangout_id: number }

export const messagingApi = {
  list: () => api.get<Conversation[]>('/conversations/'),
  get: (id: number) => api.get<Conversation>(`/conversations/${id}/`),
  create: (data: CreateConversationPayload) =>
    api.post<Conversation>('/conversations/', data),
  unreadCount: () => api.get<{ unread_total: number }>('/conversations/unread-count/'),
  messages: (id: number, afterId?: number) =>
    api.get<ChatMessage[]>(`/conversations/${id}/messages/`, {
      params: afterId != null ? { after_id: afterId } : undefined,
    }),
  send: (id: number, body: string) =>
    api.post<ChatMessage>(`/conversations/${id}/messages/`, { body }),
  markRead: (id: number) => api.post<{ ok: boolean }>(`/conversations/${id}/read/`),
}
