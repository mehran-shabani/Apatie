import { ChangeEvent, FormEvent, useState } from 'react';
import { isAxiosError } from 'axios';
import { apiClient, setAuthToken } from '../api/client';
import type { AuthResponse } from '../types';

type AuthMode = 'login' | 'register';

interface AuthFormProps {
  onAuthenticated: (auth: AuthResponse) => void;
}

const initialState = { email: '', password: '', name: '' };

const extractErrorMessage = (mode: AuthMode, error: unknown): string => {
  if (isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data as
      | { detail?: string; message?: string; errors?: Record<string, string[] | string> | string[] }
      | undefined;

    if (data) {
      if (typeof data.detail === 'string' && data.detail.trim().length > 0) {
        return data.detail;
      }
      if (typeof data.message === 'string' && data.message.trim().length > 0) {
        return data.message;
      }
      if (data.errors) {
        const values = Array.isArray(data.errors)
          ? data.errors
          : Object.values(data.errors);
        const firstError = values[0];
        if (Array.isArray(firstError) && typeof firstError[0] === 'string') {
          return firstError[0];
        }
        if (typeof firstError === 'string') {
          return firstError;
        }
      }
    }

    if (mode === 'login' && (status === 400 || status === 401)) {
      return 'ایمیل یا رمز عبور نامعتبر است.';
    }
    if (mode === 'register' && status === 409) {
      return 'این ایمیل قبلاً ثبت شده است.';
    }
  }

  return 'عملیات با خطا مواجه شد. لطفاً دوباره تلاش کنید.';
};

export function AuthForm({ onAuthenticated }: AuthFormProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [formState, setFormState] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const endpoint = mode === 'login' ? '/auth/login/' : '/auth/register/';
      const payload = mode === 'login' ? { email: formState.email, password: formState.password } : formState;
      const { data } = await apiClient.post<AuthResponse>(endpoint, payload);
      setAuthToken(data.token);
      onAuthenticated(data);
    } catch (err) {
      console.error(err);
      setError(extractErrorMessage(mode, err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <header className="card__header">
        <h2>{mode === 'login' ? 'ورود به حساب کاربری' : 'ثبت‌نام کاربر جدید'}</h2>
        <p>برای مدیریت نوبت‌ها وارد شوید یا یک حساب تازه بسازید.</p>
      </header>

      <form className="form" onSubmit={handleSubmit}>
        {mode === 'register' && (
          <label className="form__field">
            <span>نام و نام خانوادگی</span>
            <input
              required
              name="name"
              type="text"
              value={formState.name}
              onChange={handleInputChange}
            />
          </label>
        )}

        <label className="form__field">
          <span>ایمیل</span>
          <input
            required
            name="email"
            type="email"
            value={formState.email}
            onChange={handleInputChange}
          />
        </label>

        <label className="form__field">
          <span>رمز عبور</span>
          <input
            required
            name="password"
            type="password"
            minLength={8}
            value={formState.password}
            onChange={handleInputChange}
          />
        </label>

        {error && <p className="form__error">{error}</p>}

        <div className="form__actions">
          <button className="button" type="submit" disabled={loading}>
            {loading ? 'در حال ارسال…' : mode === 'login' ? 'ورود' : 'ثبت‌نام'}
          </button>
          <button
            className="button button--link"
            type="button"
            onClick={() => {
              setMode((prev) => (prev === 'login' ? 'register' : 'login'));
              setError(null);
              setFormState(initialState);
            }}
          >
            {mode === 'login' ? 'ساخت حساب جدید' : 'قبلاً ثبت‌نام کرده‌اید؟ ورود'}
          </button>
        </div>
      </form>
    </section>
  );
}

export default AuthForm;
