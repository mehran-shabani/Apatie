import { FormEvent, useMemo, useState } from 'react';
import { apiClient } from '../api/client';
import type { AppointmentRequest, Service } from '../types';

interface BookingFormProps {
  selectedService: Service | null;
}

const generateTimeSlots = () => {
  const slots: string[] = [];
  for (let hour = 9; hour <= 17; hour += 1) {
    slots.push(`${hour.toString().padStart(2, '0')}:00`);
    slots.push(`${hour.toString().padStart(2, '0')}:30`);
  }
  return slots;
};

export function BookingForm({ selectedService }: BookingFormProps) {
  const [formState, setFormState] = useState<AppointmentRequest>({
    serviceId: selectedService?.id ?? 0,
    date: new Date().toISOString().split('T')[0],
    timeSlot: '09:00',
    notes: '',
  });
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const timeSlots = useMemo(() => generateTimeSlots(), []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedService) {
      setError('لطفاً ابتدا یک سرویس را انتخاب کنید.');
      return;
    }

    setStatus('submitting');
    setError(null);

    try {
      const payload: AppointmentRequest = {
        ...formState,
        serviceId: selectedService.id,
      };
      await apiClient.post('/appointments/', payload);
      setStatus('success');
    } catch (err) {
      console.error(err);
      setStatus('error');
      setError('ثبت نوبت با مشکل مواجه شد.');
    }
  };

  return (
    <section className="card">
      <header className="card__header">
        <h2>رزرو نوبت</h2>
        <p>تاریخ و زمان دلخواه خود را برای سرویس انتخاب شده وارد کنید.</p>
      </header>
      <form className="form" onSubmit={handleSubmit}>
        <label className="form__field">
          <span>تاریخ</span>
          <input
            type="date"
            value={formState.date}
            onChange={(event) => setFormState((prev) => ({ ...prev, date: event.target.value }))}
            min={new Date().toISOString().split('T')[0]}
            required
          />
        </label>
        <label className="form__field">
          <span>ساعت</span>
          <select
            value={formState.timeSlot}
            onChange={(event) => setFormState((prev) => ({ ...prev, timeSlot: event.target.value }))}
          >
            {timeSlots.map((slot) => (
              <option key={slot} value={slot}>
                {slot}
              </option>
            ))}
          </select>
        </label>
        <label className="form__field">
          <span>توضیحات تکمیلی</span>
          <textarea
            value={formState.notes ?? ''}
            onChange={(event) => setFormState((prev) => ({ ...prev, notes: event.target.value }))}
            rows={3}
            placeholder="جزئیات یا درخواست‌های خاص خود را بنویسید"
          />
        </label>

        {error && <p className="form__error">{error}</p>}
        {status === 'success' && <p className="form__success">نوبت شما ثبت شد و در انتظار تأیید است.</p>}

        <button className="button" type="submit" disabled={status === 'submitting'}>
          {status === 'submitting' ? 'در حال ثبت…' : 'ثبت نوبت'}
        </button>
      </form>
    </section>
  );
}

export default BookingForm;
