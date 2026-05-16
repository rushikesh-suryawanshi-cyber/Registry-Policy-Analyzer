import { useEffect, useState } from 'react';
import { Database, ShieldCheck, Terminal, Search, GitCompare, Bot, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const quickLinks = [
  { to: '/search', icon: Search, label: 'Policy Search', desc: 'Full-text search across all ADMX policies', color: '#0078D4' },
  { to: '/assistant', icon: Bot, label: 'AI Assistant', desc: 'Natural language queries via local RAG', color: '#7c3aed' },
  { to: '/scripts', icon: Terminal, label: 'Script Generator', desc: 'Generate PowerShell remediation scripts', color: '#059669' },
  { to: '/compare', icon: GitCompare, label: 'Version Compare', desc: 'Diff two ADMX snapshot files', color: '#d97706' },
];

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState('checking');
  const navigate = useNavigate();

  const checkApi = () => {
    setApiStatus('checking');
    fetch('http://127.0.0.1:8000/', { method: 'GET', signal: AbortSignal.timeout(5000) })
      .then(r => r.ok ? setApiStatus('online') : setApiStatus('offline'))
      .catch(() => setApiStatus('offline'));
  };

  useEffect(() => { checkApi(); }, []);

  const statusColor = { checking: '#d97706', online: '#22c55e', offline: '#ef4444' }[apiStatus];
  const statusLabel = { checking: 'Checking…', online: 'Online', offline: 'Offline' }[apiStatus];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page title */}
      <div>
        <h1 style={{ margin: '0 0 0.35rem', fontSize: '1.75rem', fontWeight: 700, color: '#fff' }}>Dashboard</h1>
        <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>Windows Policy Intelligence Engine — overview and quick access</p>
      </div>

      {/* API Health banner */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.75rem',
        padding: '0.875rem 1.25rem', borderRadius: '0.5rem',
        background: apiStatus === 'offline' ? 'rgba(239,68,68,0.08)' : apiStatus === 'checking' ? 'rgba(234,179,8,0.06)' : 'rgba(34,197,94,0.06)',
        border: `1px solid ${apiStatus === 'offline' ? 'rgba(239,68,68,0.25)' : apiStatus === 'checking' ? 'rgba(234,179,8,0.2)' : 'rgba(34,197,94,0.2)'}`,
      }}>
        <div style={{ width: 9, height: 9, borderRadius: '50%', background: statusColor, flexShrink: 0 }} />
        <span style={{ fontSize: '0.85rem', color: '#d1d5db', flex: 1 }}>
          FastAPI Backend — <strong style={{ color: statusColor }}>{statusLabel}</strong>
          {apiStatus === 'offline' && (
            <span style={{ color: '#9ca3af' }}> · In a NEW terminal run: <code style={{ color: '#60a5fa', background: '#111', padding: '0.1rem 0.4rem', borderRadius: 3 }}>python -m uvicorn api.main:app --reload</code></span>
          )}
        </span>
        <button onClick={checkApi} style={{
          background: 'rgba(255,255,255,0.05)', border: '1px solid #333', borderRadius: '0.375rem',
          padding: '0.3rem 0.75rem', color: '#9ca3af', cursor: 'pointer', fontSize: '0.75rem',
        }}>↻ Retry</button>
      </div>


      {/* Quick links */}
      <div>
        <h2 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quick Access</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
          {quickLinks.map(({ to, icon: Icon, label, desc, color }) => (
            <Link
              key={to}
              to={to}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: '1rem',
                padding: '1.25rem', borderRadius: '0.625rem', textDecoration: 'none',
                background: '#1a1a1a', border: '1px solid #2a2a2a', transition: 'all 0.15s',
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = color; e.currentTarget.style.background = '#1f1f1f'; }}
              onMouseOut={e => { e.currentTarget.style.borderColor = '#2a2a2a'; e.currentTarget.style.background = '#1a1a1a'; }}
            >
              <div style={{
                width: 42, height: 42, borderRadius: '0.5rem', flexShrink: 0,
                background: `${color}18`, border: `1px solid ${color}30`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={20} style={{ color }} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ margin: '0 0 0.2rem', fontWeight: 600, color: '#e5e7eb', fontSize: '0.9rem' }}>{label}</p>
                <p style={{ margin: 0, color: '#6b7280', fontSize: '0.8rem', lineHeight: 1.4 }}>{desc}</p>
              </div>
              <ArrowRight size={16} style={{ color: '#374151', flexShrink: 0, marginTop: 4 }} />
            </Link>
          ))}
        </div>
      </div>

      {/* Pipeline guide */}
      <div style={{ background: '#1a1a1a', borderRadius: '0.625rem', border: '1px solid #2a2a2a', overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #2a2a2a', background: '#141414' }}>
          <h2 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: '#d1d5db' }}>Getting Started — Pipeline</h2>
        </div>
        <div style={{ padding: '1.25rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[
            { step: '1', cmd: 'python main.py --admx_dir "C:\\Windows\\PolicyDefinitions"', label: 'Parse ADMX → SQLite + ChromaDB' },
            { step: '2', cmd: 'uvicorn api.main:app --reload', label: 'Start the FastAPI backend' },
            { step: '3', cmd: 'cd frontend && npm run dev', label: 'Launch the React dashboard' },
          ].map(({ step, cmd, label }) => (
            <div key={step} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%', background: '#0078D4',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 700, color: '#fff', flexShrink: 0,
              }}>{step}</div>
              <div>
                <p style={{ margin: '0 0 0.15rem', fontSize: '0.8rem', color: '#9ca3af' }}>{label}</p>
                <code style={{ fontSize: '0.78rem', color: '#60a5fa', background: '#111', padding: '0.2rem 0.5rem', borderRadius: '0.3rem' }}>{cmd}</code>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
