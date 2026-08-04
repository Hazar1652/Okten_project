import { useEffect, useState, type ReactNode } from 'react'

const AGE_KEY = 'okten_age_confirmed'
const SAFETY_KEY = 'okten_safety_confirmed'

type Step = 'age' | 'safety' | 'done'

export default function FirstLaunchGate({ children }: { children: ReactNode }) {
  const [step, setStep] = useState<Step>('done')

  useEffect(() => {
    if (!localStorage.getItem(AGE_KEY)) {
      setStep('age')
    } else if (!localStorage.getItem(SAFETY_KEY)) {
      setStep('safety')
    } else {
      setStep('done')
    }
  }, [])

  const confirmAge = () => {
    localStorage.setItem(AGE_KEY, '1')
    setStep('safety')
  }

  const declineAge = () => {
    window.location.href = 'https://www.google.com'
  }

  const confirmSafety = () => {
    localStorage.setItem(SAFETY_KEY, '1')
    setStep('done')
  }

  if (step === 'done') return <>{children}</>

  return (
    <>
      {children}
      <div className="modal-overlay" role="presentation">
        <div className="modal-card" role="dialog" aria-modal="true">
          {step === 'age' ? (
            <>
              <h2>Вікове обмеження 18+</h2>
              <p>
                Запускаючи цей додаток, ви підтверджуєте, що вам виповнилось <strong>18 років</strong>.
              </p>
              <div className="modal-actions">
                <button type="button" className="btn btn-primary" onClick={confirmAge}>
                  Мені є 18 років
                </button>
                <button type="button" className="btn btn-ghost" onClick={declineAge}>
                  Вийти
                </button>
              </div>
            </>
          ) : (
            <>
              <h2>Безпека зустрічей</h2>
              <p>
                Адміністрація застерігає: будьте обережні та не зустрічайтесь з незнайомими людьми в
                небезпечних чи невідомих вам місцях. Обирайте перевірені заклади та повідомляйте близьких
                про плани.
              </p>
              <div className="modal-actions">
                <button type="button" className="btn btn-primary" onClick={confirmSafety}>
                  Зрозуміло
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
