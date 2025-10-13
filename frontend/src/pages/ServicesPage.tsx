import { useState } from 'react';
import ServiceList from '../components/ServiceList';
import type { Service } from '../types';

export function ServicesPage() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);

  return (
    <div className="page">
      <ServiceList onSelect={(service) => setSelectedService(service)} selectedServiceId={selectedService?.id ?? null} />
      {selectedService && (
        <section className="card">
          <header className="card__header">
            <h2>جزییات سرویس انتخاب شده</h2>
            <p>پس از اطمینان می‌توانید به مرحله رزرو نوبت بروید.</p>
          </header>
          <dl className="details">
            <div>
              <dt>عنوان</dt>
              <dd>{selectedService.name}</dd>
            </div>
            <div>
              <dt>مدت زمان</dt>
              <dd>{selectedService.durationMinutes} دقیقه</dd>
            </div>
            <div>
              <dt>هزینه</dt>
              <dd>{selectedService.price.toLocaleString('fa-IR')} تومان</dd>
            </div>
          </dl>
        </section>
      )}
    </div>
  );
}

export default ServicesPage;
