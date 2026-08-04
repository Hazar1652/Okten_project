const DEFAULT_FIELD_LABELS: Record<string, string> = {
  name: 'Назва',
  description: 'Опис',
  address: 'Адреса',
  latitude: 'Широта',
  longitude: 'Довгота',
  phone_number: 'Телефон',
  email: 'Email',
  website: 'Сайт',
  avg_check: 'Середній чек',
  work_time: 'Години роботи',
  tag_ids: 'Теги',
  feature_ids: 'Особливості',
  main_image: 'Головне фото',
  image: 'Фото',
  images: 'Фото',
  status: 'Статус',
  title: 'Заголовок',
  content: 'Текст',
  body: 'Повідомлення',
  rating: 'Оцінка',
  username: "Ім'я користувача",
  password: 'Пароль',
  first_name: "Ім'я",
  last_name: 'Прізвище',
  venue: 'Заклад',
  meeting_date: 'Дата',
  meeting_time: 'Час',
  goal_description: 'Мета зустрічі',
  contact_me: 'Контакт',
  gender_preferences: 'Стать',
  people_count: 'Кількість людей',
  payer_type: 'Хто платить',
  budget_min: 'Бюджет від',
  budget_max: 'Бюджет до',
}

// Field-level DRF messages are often too technical for end users.
// Show a friendly hint instead of the raw serializer wording.
const FRIENDLY_FIELD_MESSAGES: Record<string, string> = {
  main_image: 'Завантажте коректний файл зображення.',
  image: 'Завантажте коректний файл зображення.',
}

function humanizeField(field: string): string {
  return DEFAULT_FIELD_LABELS[field] ?? field
}

export function apiErrorMessage(
  err: unknown,
  fallback: string,
  fieldLabels: Record<string, string> = {},
): string {
  const data = (err as { response?: { data?: unknown } })?.response?.data
  // Non-JSON responses (e.g. Django HTML 500 page) must not be dumped field-by-field.
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return fallback
  }

  const record = data as Record<string, unknown>
  if (typeof record.detail === 'string') return record.detail

  const labels = { ...DEFAULT_FIELD_LABELS, ...fieldLabels }
  const parts: string[] = []

  for (const [field, value] of Object.entries(record)) {
    const text = Array.isArray(value)
      ? value.filter((v) => typeof v === 'string').join(', ')
      : typeof value === 'string'
        ? value
        : ''
    if (!text) continue

    // Errors not tied to a specific field are shown as-is.
    if (field === 'non_field_errors' || field === 'detail') {
      parts.push(text)
      continue
    }

    const friendly = FRIENDLY_FIELD_MESSAGES[field] ?? text
    const label = labels[field] ?? humanizeField(field)
    parts.push(`${label}: ${friendly}`)
  }

  return parts.length > 0 ? parts.join(' · ') : fallback
}
