import DatePicker, { registerLocale } from 'react-datepicker'
import { uk } from 'date-fns/locale'
import 'react-datepicker/dist/react-datepicker.css'

registerLocale('uk', uk)

function toDateStr(d: Date): string {
  const tzOffset = d.getTimezoneOffset() * 60000
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 10)
}

function toTimeStr(d: Date): string {
  return d.toTimeString().slice(0, 5)
}

function parseDate(value: string): Date | null {
  if (!value) return null
  const d = new Date(`${value}T00:00:00`)
  return Number.isNaN(d.getTime()) ? null : d
}

function parseTime(dateValue: string, timeValue: string): Date | null {
  if (!timeValue) return null
  const base = dateValue || toDateStr(new Date())
  const d = new Date(`${base}T${timeValue}:00`)
  return Number.isNaN(d.getTime()) ? null : d
}

interface Props {
  date: string
  time: string
  onDateChange: (value: string) => void
  onTimeChange: (value: string) => void
}

export default function MeetingDateTimePicker({
  date,
  time,
  onDateChange,
  onTimeChange,
}: Props) {
  const now = new Date()
  const today = toDateStr(now)
  const isToday = date === today

  const dayStart = new Date()
  dayStart.setHours(0, 0, 0, 0)
  const dayEnd = new Date()
  dayEnd.setHours(23, 59, 0, 0)

  return (
    <>
      <label>
        Дата *
        <DatePicker
          selected={parseDate(date)}
          onChange={(d: Date | null) => onDateChange(d ? toDateStr(d) : '')}
          minDate={now}
          dateFormat="dd.MM.yyyy"
          locale="uk"
          calendarStartDay={1}
          showPopperArrow={false}
          placeholderText="Оберіть дату"
          className="dtp-input"
          required
        />
      </label>
      <label>
        Час *
        <DatePicker
          selected={parseTime(date, time)}
          onChange={(d: Date | null) => onTimeChange(d ? toTimeStr(d) : '')}
          showTimeSelect
          showTimeSelectOnly
          timeIntervals={30}
          timeCaption="Час"
          dateFormat="HH:mm"
          locale="uk"
          minTime={isToday ? now : dayStart}
          maxTime={dayEnd}
          showPopperArrow={false}
          placeholderText="Оберіть час"
          className="dtp-input"
          required
        />
      </label>
    </>
  )
}
