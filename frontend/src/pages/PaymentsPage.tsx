import { useState } from 'react';
import PaymentManager from '../components/PaymentManager';

export function PaymentsPage() {
  const [userId, setUserId] = useState<number | null>(null);

  return (
    <div className="page">
      <section className="card">
        <header className="card__header">
          <h2>انتخاب کاربر</h2>
          <p>برای مشاهده اطلاعات پرداخت، شناسه کاربر را وارد کنید.</p>
        </header>
        <label className="form__field">
          <span>شناسه کاربر</span>
          <input
            type="number"
            min={1}
            value={userId ?? ''}
            onChange={(event) => setUserId(event.target.value ? Number(event.target.value) : null)}
            placeholder="مثلاً 12"
          />
        </label>
      </section>

      <PaymentManager userId={userId} />
    </div>
  );
}

export default PaymentsPage;
