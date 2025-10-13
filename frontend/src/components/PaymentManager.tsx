import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { PaymentMethod, PaymentRecord } from '../types';

interface PaymentManagerProps {
  userId: number | null;
}

export function PaymentManager({ userId }: PaymentManagerProps) {
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [history, setHistory] = useState<PaymentRecord[]>([]);
  const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle');

  useEffect(() => {
    if (!userId) {
      return;
    }

    const fetchData = async () => {
      setStatus('loading');
      try {
        const [methodsResponse, historyResponse] = await Promise.all([
          apiClient.get<PaymentMethod[]>(`/payments/methods/`),
          apiClient.get<PaymentRecord[]>(`/payments/history/`),
        ]);
        setMethods(methodsResponse.data);
        setHistory(historyResponse.data);
        setStatus('idle');
      } catch (err) {
        console.error(err);
        setStatus('error');
        setMethods([
          { id: 1, brand: 'Visa', last4: '1234', isDefault: true },
          { id: 2, brand: 'Mastercard', last4: '9876', isDefault: false },
        ]);
        setHistory([
          {
            id: 100,
            appointmentId: 45,
            amount: 780000,
            currency: 'IRT',
            status: 'paid',
            processedAt: new Date().toISOString(),
          },
        ]);
      }
    };

    fetchData();
  }, [userId]);

  const setDefaultMethod = async (methodId: number) => {
    try {
      await apiClient.post(`/payments/methods/${methodId}/set_default/`);
      setMethods((current) => current.map((method) => ({ ...method, isDefault: method.id === methodId })));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <section className="card">
      <header className="card__header">
        <h2>مدیریت پرداخت</h2>
        <p>روش‌های پرداخت ذخیره شده و وضعیت تراکنش‌ها را بررسی کنید.</p>
      </header>

      {status === 'loading' && <p>در حال بارگذاری اطلاعات پرداخت…</p>}
      {status === 'error' && <p className="card__error">عدم ارتباط با سرور؛ اطلاعات نمونه نمایش داده شده است.</p>}

      <div className="payment-grid">
        <div>
          <h3>روش‌های پرداخت</h3>
          <ul className="list">
            {methods.map((method) => (
              <li key={method.id} className={method.isDefault ? 'list__item list__item--active' : 'list__item'}>
                <div>
                  <strong>{method.brand}</strong>
                  <span>**** {method.last4}</span>
                </div>
                {!method.isDefault && (
                  <button className="button button--secondary" onClick={() => setDefaultMethod(method.id)}>
                    انتخاب به عنوان پیش‌فرض
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3>تاریخچه تراکنش‌ها</h3>
          <ul className="list">
            {history.map((payment) => (
              <li key={payment.id} className="list__item">
                <div>
                  <strong>نوبت #{payment.appointmentId}</strong>
                  <span>{new Date(payment.processedAt).toLocaleString('fa-IR')}</span>
                </div>
                <div>
                  <span>{payment.amount.toLocaleString('fa-IR')} {payment.currency}</span>
                  <span className={`status status--${payment.status}`}>
                    {payment.status === 'paid' ? 'پرداخت شده' : payment.status === 'pending' ? 'در انتظار' : 'ناموفق'}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default PaymentManager;
