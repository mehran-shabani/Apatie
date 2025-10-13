import { NavLink, Route, Routes } from 'react-router-dom';
import './App.css';
import AuthPage from './pages/AuthPage';
import BookingPage from './pages/BookingPage';
import PaymentsPage from './pages/PaymentsPage';
import ServicesPage from './pages/ServicesPage';

const getNavLinkClassName = ({ isActive }: { isActive: boolean }) =>
  (isActive ? 'topbar__link topbar__link--active' : 'topbar__link');

function App() {
  return (
    <div className="layout">
      <header className="topbar">
        <h1 className="topbar__title">سامانه مدیریت خدمات</h1>
        <nav className="topbar__nav">
          <NavLink to="/auth" className={getNavLinkClassName}>
            احراز هویت
          </NavLink>
          <NavLink to="/services" className={getNavLinkClassName}>
            فهرست سرویس‌ها
          </NavLink>
          <NavLink to="/booking" className={getNavLinkClassName}>
            رزرو نوبت
          </NavLink>
          <NavLink to="/payments" className={getNavLinkClassName}>
            مدیریت پرداخت
          </NavLink>
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<ServicesPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/booking" element={<BookingPage />} />
          <Route path="/payments" element={<PaymentsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
