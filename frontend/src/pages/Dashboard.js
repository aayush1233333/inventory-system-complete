import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../lib/api';
import { Package, Users, ShoppingCart, AlertTriangle, TrendingUp, Clock } from 'lucide-react';

const STATS_CONFIG = [
  {
    key: 'total_revenue',
    label: 'Total Revenue',
    icon: TrendingUp,
    color: '#22c55e',
    bg: 'rgba(34,197,94,0.1)',
    format: (v) => `₹${Number(v).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`,
  },
  {
    key: 'total_orders',
    label: 'Total Orders',
    icon: ShoppingCart,
    color: '#3d7eff',
    bg: 'rgba(61,126,255,0.1)',
    format: (v) => v,
  },
  {
    key: 'pending_orders',
    label: 'Pending Orders',
    icon: Clock,
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.1)',
    format: (v) => v,
  },
  {
    key: 'total_products',
    label: 'Products',
    icon: Package,
    color: '#a855f7',
    bg: 'rgba(168,85,247,0.1)',
    format: (v) => v,
  },
  {
    key: 'total_customers',
    label: 'Customers',
    icon: Users,
    color: '#06b6d4',
    bg: 'rgba(6,182,212,0.1)',
    format: (v) => v,
  },
  {
    key: 'low_stock_products',
    label: 'Low Stock Alerts',
    icon: AlertTriangle,
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.1)',
    format: (v) => v,
  },
];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.stats()
      .then((r) => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-center">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 24, fontWeight: 800, color: 'var(--text)', marginBottom: 6 }}>
          System Overview
        </h2>
        <p style={{ color: 'var(--text-3)', fontSize: 13 }}>Real-time metrics across your inventory and orders</p>
      </div>

      <div className="stats-grid">
        {STATS_CONFIG.map(({ key, label, icon: Icon, color, bg, format }) => (
          <div
            key={key}
            className="stat-card"
            style={{ '--accent-color': color, '--icon-bg': bg }}
          >
            <div className="stat-icon">
              <Icon />
            </div>
            <div className={`stat-value ${key === 'total_revenue' ? 'stat-value-revenue' : ''}`}>
              {stats ? format(stats[key]) : '—'}
            </div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>

      <div className="card" style={{ maxWidth: 480 }}>
        <div className="card-header">
          <span className="card-title">Quick Actions</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            { href: '/products', label: '+ Add a new product', color: 'var(--accent)' },
            { href: '/customers', label: '+ Register a customer', color: 'var(--green)' },
            { href: '/orders', label: '+ Create an order', color: 'var(--yellow)' },
            { href: '/inventory', label: '⚠ View stock alerts', color: 'var(--red)' },
          ].map(({ href, label, color }) => (
            <Link
              key={href}
              to={href}
              style={{
                padding: '10px 14px',
                background: 'var(--surface-2)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                color,
                textDecoration: 'none',
                fontSize: 13,
                fontWeight: 500,
                display: 'block',
                transition: 'border-color 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = color}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
