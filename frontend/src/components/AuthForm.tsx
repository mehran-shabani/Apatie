import { FormEvent, useState } from 'react';
import { apiClient, setAuthToken } from '../api/client';
import type { AuthResponse } from '../types';

type AuthMode = 'login' | 'register';

interface AuthFormProps {
  onAuthenticated: (auth: AuthResponse) => void;
}

const initialState = { email: '', password: '', name: '' };

export function AuthForm({ onAuthenticated }: AuthFormProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [formState, setFormState] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError('عملیات با خطا مواجه شد. لطفاً دوباره تلاش کنید.');
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
              onChange={(event) => setFormState((prev) => ({ ...prev, name: event.target.value }))}
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
            onChange={(event) => setFormState((prev) => ({ ...prev, email: event.target.value }))}
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
            onChange={(event) => setFormState((prev) => ({ ...prev, password: event.target.value }))}
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
