import React, { useState } from 'react';
import { Search as SearchIcon, Loader2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { searchByKeyword } from '../services/api';

function PolicyCard({ item }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <li style={{
      padding: '1.25rem 1.5rem',
      borderBottom: '1px solid #2a2a2a',
      transition: 'background 0.15s',
    }}
      onMouseOver={e => e.currentTarget.style.background = '#161616'}
      onMouseOut={e => e.currentTarget.style.background = 'transparent'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ margin: '0 0 0.4rem', fontSize: '0.975rem', fontWeight: 600, color: '#60a5fa' }}>
            {item.display_name || item.name}
          </h3>
          <span style={{
            fontSize: '0.72rem', fontFamily: 'monospace',
            background: '#1a1a1a', border: '1px solid #333',
            padding: '0.2rem 0.5rem', borderRadius: '0.3rem', color: '#9ca3af',
          }}>
            {item.gpo_path || 'No path'}
          </span>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6b7280', flexShrink: 0, padding: '0.25rem' }}
        >
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {/* Registry info */}
      {(item.key || item.value_name) && (
        <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.65rem', fontSize: '0.75rem', color: '#6b7280' }}>
          {item.key && <span><span style={{ color: '#4b5563' }}>Key: </span>{item.key}</span>}
          {item.value_name && <span><span style={{ color: '#4b5563' }}>Value: </span>{item.value_name}</span>}
        </div>
      )}

      {/* Expandable explain text */}
      {expanded && item.explain_text && (
        <div style={{
          marginTop: '0.85rem', padding: '0.875rem', background: '#0f0f0f',
          borderRadius: '0.5rem', border: '1px solid #2a2a2a',
          fontSize: '0.82rem', color: '#d1d5db', lineHeight: 1.7,
          whiteSpace: 'pre-wrap',
        }}>
          {item.explain_text}
        </div>
      )}
    </li>
  );
}

export default function PolicySearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await searchByKeyword(query);
      setResults(data);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to connect to the API. Is the FastAPI server running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', height: '100%' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#fff', margin: 0 }}>Policy Search</h1>

      {/* Search bar */}
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.75rem' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <SearchIcon size={17} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder='Search by keyword, policy name, or description (e.g. "telemetry")'
            style={{
              width: '100%', boxSizing: 'border-box',
              background: '#1f1f1f', border: '1px solid #333',
              borderRadius: '0.5rem', padding: '0.8rem 1rem 0.8rem 2.75rem',
              color: '#e5e7eb', fontSize: '0.9rem', outline: 'none',
            }}
            onFocus={e => e.target.style.borderColor = '#0078D4'}
            onBlur={e => e.target.style.borderColor = '#333'}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          style={{
            padding: '0.8rem 1.75rem', borderRadius: '0.5rem',
            background: loading || !query.trim() ? '#1a3a5c' : '#0078D4',
            border: 'none', color: '#fff', fontWeight: 600,
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            transition: 'background 0.15s',
          }}
        >
          {loading ? <Loader2 size={17} style={{ animation: 'spin 1s linear infinite' }} /> : 'Search'}
        </button>
      </form>

      {/* Error state */}
      {error && (
        <div style={{
          display: 'flex', gap: '0.75rem', alignItems: 'flex-start',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '0.5rem', padding: '1rem 1.25rem',
        }}>
          <AlertTriangle size={18} style={{ color: '#f87171', flexShrink: 0, marginTop: 1 }} />
          <div>
            <p style={{ margin: '0 0 0.25rem', fontWeight: 600, color: '#fca5a5', fontSize: '0.875rem' }}>Search Failed</p>
            <p style={{ margin: 0, color: '#f87171', fontSize: '0.82rem' }}>{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div style={{
          flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column',
          background: '#1a1a1a', borderRadius: '0.5rem', border: '1px solid #2a2a2a',
        }}>
          <div style={{
            padding: '0.75rem 1.5rem', borderBottom: '1px solid #2a2a2a',
            background: '#141414', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: '0.82rem', color: '#6b7280' }}>
              Found <strong style={{ color: '#d1d5db' }}>{results.total_count}</strong> matching policies
              {results.total_count > results.items.length && ` (showing ${results.items.length})`}
            </span>
          </div>
          <ul style={{ flex: 1, overflowY: 'auto', margin: 0, padding: 0, listStyle: 'none' }}>
            {results.items.length === 0 ? (
              <li style={{ padding: '3rem', textAlign: 'center', color: '#6b7280' }}>No policies found.</li>
            ) : (
              results.items.map((item) => <PolicyCard key={item.id || item.name} item={item} />)
            )}
          </ul>
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
