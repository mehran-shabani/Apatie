export interface AuthResponse {
  token: string;
  user: {
    id: number;
    name: string;
    email: string;
  };
}

export interface Service {
  id: number;
  name: string;
  description: string;
  durationMinutes: number;
  price: number;
}

export interface AppointmentRequest {
  serviceId: number;
  date: string;
  timeSlot: string;
  notes?: string;
}

export interface Appointment extends AppointmentRequest {
  id: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
}

export interface PaymentMethod {
  id: number;
  brand: string;
  last4: string;
  isDefault: boolean;
}

export interface PaymentRecord {
  id: number;
  appointmentId: number;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'failed';
  processedAt: string;
}
