import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

describe('App routing', () => {
  it('renders navigation links and default services page', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );

    expect(screen.getByRole('heading', { name: 'سامانه مدیریت خدمات' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'احراز هویت' })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'انتخاب سرویس' })).toBeInTheDocument();
  });
});
