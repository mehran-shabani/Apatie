import { useMemo, useState } from 'react';
import BookingForm from '../components/BookingForm';
import ServiceList from '../components/ServiceList';
import type { Service } from '../types';

export function BookingPage() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);

  const summary = useMemo(() => {
    if (!selectedService) {
      return 'برای شروع رزرو، ابتدا یک سرویس را انتخاب کنید.';
    }

    return `شما سرویس "${selectedService.name}" با مدت ${selectedService.durationMinutes} دقیقه را انتخاب کرده‌اید.`;
  }, [selectedService]);

  return (
    <div className="page page--two-column">
      <div className="page__column">
        <ServiceList onSelect={setSelectedService} selectedServiceId={selectedService?.id ?? null} />
      </div>
      <div className="page__column">
        <BookingForm selectedService={selectedService} />
        <p className="muted">{summary}</p>
      </div>
    </div>
  );
}

export default BookingPage;
