import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { Service } from '../types';

interface ServiceListProps {
  onSelect?: (service: Service) => void;
  selectedServiceId?: number | null;
}

export function ServiceList({ onSelect, selectedServiceId }: ServiceListProps) {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const { data } = await apiClient.get<Service[]>('/services/');
        setServices(data);
      } catch (err) {
        console.error(err);
        setError('امکان دریافت فهرست سرویس‌ها وجود ندارد.');
        if (import.meta.env.DEV) {
          setServices([
            {
              id: 1,
              name: 'مشاوره اولیه',
              description: 'گفتگوی ۳۰ دقیقه‌ای برای بررسی نیازها و پاسخ به سوالات.',
              durationMinutes: 30,
              price: 450000,
            },
            {
              id: 2,
              name: 'پیگیری تخصصی',
              description: 'جلسه ۶۰ دقیقه‌ای جهت بررسی وضعیت و ارائه برنامه شخصی‌سازی شده.',
              durationMinutes: 60,
              price: 780000,
            },
          ]);
        } else {
          setServices([]);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  if (loading) {
    return <p>در حال بارگذاری سرویس‌ها…</p>;
  }

  return (
    <section className="card">
      <header className="card__header">
        <h2>انتخاب سرویس</h2>
        <p>یکی از سرویس‌های فعال را برای ادامه فرایند انتخاب کنید.</p>
      </header>
      {error && <p className="card__error">{error}</p>}
      <ul className="service-list">
        {services.map((service) => (
          <li key={service.id} className={selectedServiceId === service.id ? 'service-list__item service-list__item--active' : 'service-list__item'}>
            <button type="button" onClick={() => onSelect?.(service)}>
              <div>
                <h3>{service.name}</h3>
                <p>{service.description}</p>
              </div>
              <dl>
                <div>
                  <dt>مدت زمان</dt>
                  <dd>{service.durationMinutes} دقیقه</dd>
                </div>
                <div>
                  <dt>هزینه</dt>
                  <dd>{service.price.toLocaleString('fa-IR')} تومان</dd>
                </div>
              </dl>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ServiceList;
