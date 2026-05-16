import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Search, FolderTree, MessageSquare,
  ArrowLeftRight, Terminal, Settings, Menu, X, Shield, Save
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/search', label: 'Policy Search', icon: Search },
  { path: '/registry', label: 'Registry Explorer', icon: FolderTree },
  { path: '/assistant', label: 'AI Assistant', icon: MessageSquare },
  { path: '/compare', label: 'Version Compare', icon: ArrowLeftRight },
  { path: '/scripts', label: 'Script Generator', icon: Terminal },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [globalSearch, setGlobalSearch] = useState('');

  // Settings dialog state
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [apiUrl, setApiUrl] = useState('http://127.0.0.1:8000');

  const handleGlobalSearch = (e) => {
    if (e.key === 'Enter' && globalSearch.trim()) {
      navigate(`/search?q=${encodeURIComponent(globalSearch.trim())}`);
      setGlobalSearch('');
    }
  };

  const handleSaveSettings = () => {
    // In a real app, you would save these to localStorage or context
    setIsSettingsOpen(false);
  };

  return (
    <div style={{
      display: 'flex', height: '100vh', overflow: 'hidden',
      background: '#111', color: '#e5e7eb', fontFamily: "'Segoe UI', system-ui, sans-serif",
    }}>
      {/* Sidebar */}
      <aside style={{
        width: sidebarOpen ? 240 : 0,
        minWidth: sidebarOpen ? 240 : 0,
        overflow: 'hidden',
        background: '#1a1a1a',
        borderRight: '1px solid #2a2a2a',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease, min-width 0.2s ease',
      }}>
        {/* Logo */}
        <div style={{
          padding: '1.25rem 1rem', borderBottom: '1px solid #2a2a2a',
          display: 'flex', alignItems: 'center', gap: '0.75rem',
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, #0078D4, #005a9e)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <Shield size={20} color="#fff" />
          </div>
          <div>
            <p style={{ margin: 0, fontWeight: 700, fontSize: '0.9rem', color: '#fff', whiteSpace: 'nowrap' }}>Policy Intel</p>
            <p style={{ margin: 0, fontSize: '0.7rem', color: '#6b7280', whiteSpace: 'nowrap' }}>Windows GPO Tool</p>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 0.5rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.625rem',
                  padding: '0.625rem 0.875rem', borderRadius: '0.5rem',
                  textDecoration: 'none', marginBottom: '0.2rem',
                  background: isActive ? 'rgba(0,120,212,0.15)' : 'transparent',
                  color: isActive ? '#60a5fa' : '#9ca3af',
                  borderLeft: isActive ? '2px solid #0078D4' : '2px solid transparent',
                  transition: 'all 0.15s',
                  whiteSpace: 'nowrap',
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 600 : 400,
                }}
                onMouseOver={e => { if (!isActive) { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = '#d1d5db'; } }}
                onMouseOut={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#9ca3af'; } }}
              >
                <Icon size={17} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Bottom status */}
        <div style={{ padding: '1rem', borderTop: '1px solid #2a2a2a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ fontSize: '0.72rem', color: '#6b7280' }}>Backend: localhost:8000</span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Topbar */}
        <header style={{
          height: 60, background: '#1a1a1a', borderBottom: '1px solid #2a2a2a',
          display: 'flex', alignItems: 'center', padding: '0 1.25rem', gap: '1rem', flexShrink: 0,
        }}>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6b7280', padding: '0.25rem', display: 'flex' }}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div style={{ flex: 1, maxWidth: 520, position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
            <input
              type="text"
              value={globalSearch}
              onChange={e => setGlobalSearch(e.target.value)}
              onKeyDown={handleGlobalSearch}
              placeholder="Global search — press Enter to search…"
              style={{
                width: '100%', boxSizing: 'border-box',
                background: '#111', border: '1px solid #2a2a2a',
                borderRadius: '0.5rem', padding: '0.5rem 1rem 0.5rem 2.25rem',
                color: '#e5e7eb', fontSize: '0.85rem', outline: 'none',
              }}
              onFocus={e => e.target.style.borderColor = '#0078D4'}
              onBlur={e => e.target.style.borderColor = '#2a2a2a'}
            />
          </div>

          <button
            onClick={() => setIsSettingsOpen(true)}
            style={{
              marginLeft: 'auto', background: 'none', border: '1px solid #2a2a2a',
              borderRadius: '0.5rem', padding: '0.5rem', cursor: 'pointer', color: '#6b7280', display: 'flex',
              transition: 'all 0.15s'
            }}
            onMouseOver={e => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = '#0078D4'; }}
            onMouseOut={e => { e.currentTarget.style.color = '#6b7280'; e.currentTarget.style.borderColor = '#2a2a2a'; }}
          >
            <Settings size={18} />
          </button>
        </header>

        {/* Page content */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '1.75rem 2rem', position: 'relative' }}>
          <Outlet />
        </main>
      </div>

      {/* Settings Dialog */}
      {isSettingsOpen && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem'
        }}>
          <div style={{
            background: '#1a1a1a', border: '1px solid #333', borderRadius: '0.75rem',
            width: '100%', maxWidth: 450, display: 'flex', flexDirection: 'column',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', overflow: 'hidden'
          }}>
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '1rem 1.5rem', borderBottom: '1px solid #333', background: '#111'
            }}>
              <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Settings size={18} color="#0078D4" /> Settings
              </h2>
              <button
                onClick={() => setIsSettingsOpen(false)}
                style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', display: 'flex' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500, color: '#d1d5db' }}>
                  Backend API URL
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={e => setApiUrl(e.target.value)}
                  style={{
                    width: '100%', boxSizing: 'border-box', background: '#111', border: '1px solid #333',
                    borderRadius: '0.375rem', padding: '0.5rem 0.75rem', color: '#fff', outline: 'none', fontSize: '0.875rem'
                  }}
                  onFocus={e => e.target.style.borderColor = '#0078D4'}
                  onBlur={e => e.target.style.borderColor = '#333'}
                />
                <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#6b7280' }}>
                  The endpoint where the FastAPI server is running.
                </p>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500, color: '#d1d5db' }}>
                  Theme
                </label>
                <select
                  value={theme}
                  onChange={e => setTheme(e.target.value)}
                  style={{
                    width: '100%', boxSizing: 'border-box', background: '#111', border: '1px solid #333',
                    borderRadius: '0.375rem', padding: '0.5rem 0.75rem', color: '#fff', outline: 'none', fontSize: '0.875rem',
                    appearance: 'none'
                  }}
                  onFocus={e => e.target.style.borderColor = '#0078D4'}
                  onBlur={e => e.target.style.borderColor = '#333'}
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light (Coming Soon)</option>
                  <option value="system">System Default</option>
                </select>
              </div>
            </div>

            <div style={{
              padding: '1rem 1.5rem', borderTop: '1px solid #333', background: '#111',
              display: 'flex', justifyContent: 'flex-end', gap: '0.75rem'
            }}>
              <button
                onClick={() => setIsSettingsOpen(false)}
                style={{
                  padding: '0.5rem 1rem', background: 'transparent', border: '1px solid #333',
                  borderRadius: '0.375rem', color: '#d1d5db', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500
                }}
                onMouseOver={e => { e.currentTarget.style.background = '#1a1a1a'; }}
                onMouseOut={e => { e.currentTarget.style.background = 'transparent'; }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveSettings}
                style={{
                  padding: '0.5rem 1rem', background: '#0078D4', border: 'none',
                  borderRadius: '0.375rem', color: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500,
                  display: 'flex', alignItems: 'center', gap: '0.4rem'
                }}
              >
                <Save size={16} /> Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
