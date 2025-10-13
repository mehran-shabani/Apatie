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
  /** Price in Iranian rials (integer, no decimal places). */
  price: number;
}

export interface AppointmentRequest {
  serviceId: number;
  /** ISO 8601 date string (YYYY-MM-DD). */
  date: string;
  /** Time slot in 24-hour HH:mm format. */
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
  /** Amount in Iranian rials (integer, no decimal places). */
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'failed';
  /** ISO 8601 datetime string (e.g., 2025-10-13T16:06:28Z). */
  processedAt: string;
}
