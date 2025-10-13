import { useState } from 'react';
import AuthForm from '../components/AuthForm';
import type { AuthResponse } from '../types';

export function AuthPage() {
  const [authResult, setAuthResult] = useState<AuthResponse | null>(null);

  return (
    <div className="page">
      <AuthForm onAuthenticated={(auth) => setAuthResult(auth)} />
      {authResult && (
        <section className="card">
          <header className="card__header">
            <h2>خلاصه حساب کاربری</h2>
            <p>ورود شما با موفقیت انجام شد.</p>
          </header>
          <dl className="details">
            <div>
              <dt>نام کاربر</dt>
              <dd>{authResult.user.name}</dd>
            </div>
            <div>
              <dt>ایمیل</dt>
              <dd>{authResult.user.email}</dd>
            </div>
            <div>
              <dt>شناسه</dt>
              <dd>{authResult.user.id}</dd>
            </div>
          </dl>
        </section>
      )}
    </div>
  );
}

export default AuthPage;
