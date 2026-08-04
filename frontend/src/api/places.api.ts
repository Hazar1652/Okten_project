import api from './axiosInstance'

export interface PlaceSuggestion {
  place_id: string
  description: string
  main_text: string
  secondary_text: string
}

export interface PlaceDetails {
  place_id: string
  name: string
  address: string
  latitude: string
  longitude: string
  phone_number: string
  website: string
}

export const placesApi = {
  autocomplete: (q: string, sessionToken: string) =>
    api.get<{ suggestions: PlaceSuggestion[] }>('/places/autocomplete/', {
      params: { q, session_token: sessionToken },
    }),
  details: (placeId: string, sessionToken: string) =>
    api.get<PlaceDetails>('/places/details/', {
      params: { place_id: placeId, session_token: sessionToken },
    }),
}
