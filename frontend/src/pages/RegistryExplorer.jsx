import React, { useState, useEffect, useCallback } from 'react';
import {
  Folder, FolderOpen, ChevronRight, ChevronDown,
  File, Loader2, AlertTriangle, Search, X, Database, Key
} from 'lucide-react';
import { getRegistryHives, getRegistryChildren, getRegistryPolicies, getRegistryStats } from '../services/api';

// ── Styles ─────────────────────────────────────────────────────────────────────
const S = {
  root: { display: 'flex', flexDirection: 'column', height: 'calc(100vh - 8rem)', gap: '1rem' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 },
  title: { margin: 0, fontSize: '1.5rem', fontWeight: 600, color: '#fff' },
  statsRow: { display: 'flex', gap: '0.75rem' },
  statChip: {
    display: 'flex', alignItems: 'center', gap: '0.4rem',
    background: '#1f1f1f', border: '1px solid #333', borderRadius: '0.375rem',
    padding: '0.3rem 0.75rem', fontSize: '0.78rem', color: '#9ca3af',
  },
  body: {
    display: 'flex', flex: 1, minHeight: 0,
    background: '#1a1a1a', border: '1px solid #2a2a2a',
    borderRadius: '0.75rem', overflow: 'hidden',
  },
  // Left tree pane
  tree: { width: 320, flexShrink: 0, borderRight: '1px solid #2a2a2a', display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  treeHeader: {
    padding: '0.75rem 1rem', borderBottom: '1px solid #2a2a2a',
    fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', letterSpacing: '0.05em', textTransform: 'uppercase',
  },
  treeBody: { flex: 1, overflowY: 'auto', padding: '0.5rem' },
  // Right panel
  panel: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  panelHeader: {
    padding: '0.75rem 1.25rem', borderBottom: '1px solid #2a2a2a',
    display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0,
  },
  panelPath: { fontFamily: 'monospace', fontSize: '0.8rem', color: '#60a5fa', wordBreak: 'break-all' },
  panelBody: { flex: 1, overflowY: 'auto' },
  // Search bar in panel
  searchWrap: {
    padding: '0.75rem 1.25rem', borderBottom: '1px solid #2a2a2a', flexShrink: 0,
    display: 'flex', alignItems: 'center', gap: '0.5rem',
  },
  searchInput: {
    flex: 1, background: '#111', border: '1px solid #333', borderRadius: '0.375rem',
    padding: '0.4rem 0.75rem', color: '#e5e7eb', fontSize: '0.85rem', outline: 'none',
  },
  // Table
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' },
  th: {
    padding: '0.6rem 1rem', textAlign: 'left', color: '#6b7280',
    fontWeight: 500, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em',
    borderBottom: '1px solid #2a2a2a', position: 'sticky', top: 0, background: '#1a1a1a', zIndex: 1,
  },
  td: { padding: '0.65rem 1rem', borderBottom: '1px solid #1f1f1f', verticalAlign: 'top' },
  // Policy detail drawer
  drawer: {
    width: 380, borderLeft: '1px solid #2a2a2a', background: '#111',
    overflowY: 'auto', flexShrink: 0, display: 'flex', flexDirection: 'column',
  },
  drawerHeader: {
    padding: '1rem', borderBottom: '1px solid #2a2a2a',
    display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem',
  },
  badge: {
    display: 'inline-block', padding: '0.15rem 0.5rem', borderRadius: '0.25rem',
    fontSize: '0.7rem', fontWeight: 600, letterSpacing: '0.04em',
  },
  emptyState: {
    flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', gap: '0.75rem', color: '#4b5563', padding: '2rem',
  },
};

// ── TreeNode component ─────────────────────────────────────────────────────────
function TreeNode({ label, fullPath, depth, onSelect, selectedPath }) {
  const [open, setOpen] = useState(depth < 1); // auto-open root
  const [children, setChildren] = useState(null); // null = not loaded
  const [loading, setLoading] = useState(false);
  const isSelected = selectedPath === fullPath;

  const handleToggle = useCallback(async (e) => {
    e.stopPropagation();
    if (children === null && !loading) {
      setLoading(true);
      try {
        const res = await getRegistryChildren(fullPath);
        setChildren(res.children || []);
      } catch {
        setChildren([]);
      } finally {
        setLoading(false);
      }
    }
    setOpen((v) => !v);
  }, [children, loading, fullPath]);

  const handleSelect = useCallback(() => {
    onSelect(fullPath);
  }, [fullPath, onSelect]);

  const indent = depth * 16;

  return (
    <div>
      <div
        onClick={handleSelect}
        style={{
          display: 'flex', alignItems: 'center', gap: '4px',
          padding: '4px 6px', borderRadius: '0.375rem', cursor: 'pointer',
          paddingLeft: indent + 6,
          background: isSelected ? 'rgba(0,120,212,0.18)' : 'transparent',
          color: isSelected ? '#60a5fa' : '#d1d5db',
          transition: 'background 0.1s',
        }}
        onMouseOver={(e) => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
        onMouseOut={(e) => { if (!isSelected) e.currentTarget.style.background = 'transparent'; }}
      >
        {/* Expand toggle */}
        <span
          onClick={handleToggle}
          style={{ display: 'flex', alignItems: 'center', flexShrink: 0, color: '#6b7280', cursor: 'pointer' }}
        >
          {loading
            ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />
            : (children === null || children.length > 0)
              ? open
                ? <ChevronDown size={13} />
                : <ChevronRight size={13} />
              : <span style={{ width: 13 }} />
          }
        </span>

        {/* Folder icon */}
        {open
          ? <FolderOpen size={14} style={{ color: '#0078D4', flexShrink: 0 }} />
          : <Folder size={14} style={{ color: '#0078D4', flexShrink: 0 }} />
        }

        {/* Label */}
        <span style={{ fontSize: '0.8rem', fontFamily: 'monospace', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {label}
        </span>
      </div>

      {/* Children */}
      {open && children && children.length > 0 && (
        <div>
          {children.map((child) => (
            <TreeNode
              key={`${fullPath}\\${child}`}
              label={child}
              fullPath={`${fullPath}\\${child}`}
              depth={depth + 1}
              onSelect={onSelect}
              selectedPath={selectedPath}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ── PolicyRow component ────────────────────────────────────────────────────────
function PolicyRow({ policy, onSelect, selected }) {
  const isSelected = selected?.id === policy.id;
  return (
    <tr
      onClick={() => onSelect(policy)}
      style={{
        cursor: 'pointer',
        background: isSelected ? 'rgba(0,120,212,0.1)' : 'transparent',
        transition: 'background 0.1s',
      }}
      onMouseOver={(e) => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.03)'; }}
      onMouseOut={(e) => { if (!isSelected) e.currentTarget.style.background = isSelected ? 'rgba(0,120,212,0.1)' : 'transparent'; }}
    >
      <td style={S.td}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <File size={13} style={{ color: '#6b7280', flexShrink: 0 }} />
          <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: '#e5e7eb' }}>
            {policy.value_name || '(Default)'}
          </span>
        </div>
      </td>
      <td style={S.td}>
        <span style={{ ...S.badge, background: '#1e3a5f', color: '#60a5fa' }}>
          {policy.class_type || '—'}
        </span>
      </td>
      <td style={{ ...S.td, color: '#9ca3af', fontSize: '0.78rem', maxWidth: 220 }}>
        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {policy.display_name || policy.name}
        </div>
      </td>
    </tr>
  );
}

// ── PolicyDetail drawer ────────────────────────────────────────────────────────
function PolicyDetail({ policy, onClose }) {
  if (!policy) return null;
  const fields = [
    { label: 'Policy Name', value: policy.name },
    { label: 'Display Name', value: policy.display_name },
    { label: 'Registry Key', value: policy.key },
    { label: 'Value Name', value: policy.value_name },
    { label: 'Class', value: policy.class_type },
    { label: 'GPO Path', value: policy.gpo_path },
  ];
  return (
    <div style={S.drawer}>
      <div style={S.drawerHeader}>
        <div>
          <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '0.25rem' }}>Policy Detail</div>
          <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem', lineHeight: 1.4 }}>
            {policy.display_name || policy.name}
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', flexShrink: 0, padding: '0.25rem' }}
        >
          <X size={16} />
        </button>
      </div>

      <div style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Fields */}
        {fields.map(({ label, value }) => value ? (
          <div key={label}>
            <div style={{ fontSize: '0.7rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>
              {label}
            </div>
            <div style={{ fontFamily: label.includes('Key') || label.includes('Name') ? 'monospace' : 'inherit', fontSize: '0.82rem', color: '#d1d5db', wordBreak: 'break-all' }}>
              {value}
            </div>
          </div>
        ) : null)}

        {/* Explain text */}
        {policy.explain_text && (
          <div>
            <div style={{ fontSize: '0.7rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>
              Description
            </div>
            <div style={{
              fontSize: '0.8rem', color: '#9ca3af', lineHeight: 1.6,
              background: '#1f1f1f', borderRadius: '0.375rem', padding: '0.75rem',
              border: '1px solid #2a2a2a', maxHeight: 200, overflowY: 'auto',
            }}>
              {policy.explain_text}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main RegistryExplorer ──────────────────────────────────────────────────────
export default function RegistryExplorer() {
  const [hives, setHives] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [policiesLoading, setPoliciesLoading] = useState(false);
  const [policyTotal, setPolicyTotal] = useState(0);
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [filterText, setFilterText] = useState('');
  const [hivesLoading, setHivesLoading] = useState(true);
  const [hivesError, setHivesError] = useState(null);

  // Load hives + stats on mount
  useEffect(() => {
    getRegistryStats()
      .then((statData) => setStats(statData))
      .catch(() => {}); // stats failing silently is OK

    getRegistryHives()
      .then((hiveData) => setHives(hiveData.hives || []))
      .catch((err) => setHivesError(err.message || 'Failed to load registry hives'))
      .finally(() => setHivesLoading(false));
  }, []);

  // Load policies when a key is selected
  useEffect(() => {
    if (!selectedPath) { setPolicies([]); return; }
    setPoliciesLoading(true);
    setSelectedPolicy(null);
    setFilterText('');
    getRegistryPolicies(selectedPath, 1, 200)
      .then((res) => { setPolicies(res.items || []); setPolicyTotal(res.total_count || 0); })
      .catch(() => setPolicies([]))
      .finally(() => setPoliciesLoading(false));
  }, [selectedPath]);

  const filtered = filterText
    ? policies.filter((p) =>
        (p.value_name || '').toLowerCase().includes(filterText.toLowerCase()) ||
        (p.display_name || '').toLowerCase().includes(filterText.toLowerCase()) ||
        (p.name || '').toLowerCase().includes(filterText.toLowerCase())
      )
    : policies;

  return (
    <div style={S.root}>
      {/* Header */}
      <div style={S.header}>
        <h1 style={S.title}>Registry Explorer</h1>
        {stats && (
          <div style={S.statsRow}>
            <div style={S.statChip}>
              <Key size={13} style={{ color: '#0078D4' }} />
              <span><strong style={{ color: '#e5e7eb' }}>{stats.unique_keys.toLocaleString()}</strong> unique keys</span>
            </div>
            <div style={S.statChip}>
              <Database size={13} style={{ color: '#10b981' }} />
              <span><strong style={{ color: '#e5e7eb' }}>{stats.total_policies.toLocaleString()}</strong> policies</span>
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {hivesError && (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '0.5rem', padding: '0.75rem 1rem', fontSize: '0.85rem', color: '#fca5a5' }}>
          <AlertTriangle size={15} />
          <span>{hivesError} — Is the backend running? Try restarting uvicorn.</span>
        </div>
      )}

      {/* Main body */}
      <div style={S.body}>
        {/* Left: Tree */}
        <div style={S.tree}>
          <div style={S.treeHeader}>Registry Hive</div>
          <div style={S.treeBody}>
            {hivesLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', color: '#6b7280' }}>
                <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                <span style={{ fontSize: '0.85rem' }}>Loading hives…</span>
              </div>
            ) : hives.length === 0 ? (
              <div style={{ padding: '1rem', color: '#6b7280', fontSize: '0.85rem' }}>
                No registry data found. Run <code>python main.py</code> first.
              </div>
            ) : (
              hives.sort().map((hive) => (
                <TreeNode
                  key={hive}
                  label={hive}
                  fullPath={hive}
                  depth={0}
                  onSelect={setSelectedPath}
                  selectedPath={selectedPath}
                />
              ))
            )}
          </div>
        </div>

        {/* Right: Policies panel */}
        <div style={S.panel}>
          {/* Panel header */}
          <div style={S.panelHeader}>
            <Key size={15} style={{ color: '#0078D4', flexShrink: 0 }} />
            {selectedPath
              ? <span style={S.panelPath}>{selectedPath}</span>
              : <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>Select a registry key from the tree</span>
            }
            {policyTotal > 0 && (
              <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: '#6b7280', whiteSpace: 'nowrap' }}>
                {policyTotal.toLocaleString()} polic{policyTotal === 1 ? 'y' : 'ies'}
              </span>
            )}
          </div>

          {/* Search filter (shown only when there are results) */}
          {policies.length > 0 && (
            <div style={S.searchWrap}>
              <Search size={14} style={{ color: '#6b7280', flexShrink: 0 }} />
              <input
                style={S.searchInput}
                placeholder="Filter policies…"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
              />
              {filterText && (
                <button onClick={() => setFilterText('')} style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer' }}>
                  <X size={14} />
                </button>
              )}
            </div>
          )}

          {/* Table */}
          <div style={S.panelBody}>
            {policiesLoading ? (
              <div style={{ ...S.emptyState }}>
                <Loader2 size={28} style={{ color: '#0078D4', animation: 'spin 1s linear infinite' }} />
                <span style={{ fontSize: '0.875rem' }}>Loading policies…</span>
              </div>
            ) : !selectedPath ? (
              <div style={S.emptyState}>
                <Folder size={48} style={{ color: '#2d2d2d' }} />
                <span style={{ fontSize: '0.9rem' }}>Select a registry key to explore policies</span>
              </div>
            ) : filtered.length === 0 ? (
              <div style={S.emptyState}>
                <File size={32} style={{ color: '#2d2d2d' }} />
                <span style={{ fontSize: '0.875rem' }}>
                  {filterText ? 'No policies match your filter' : 'No policies found for this key'}
                </span>
              </div>
            ) : (
              <table style={S.table}>
                <thead>
                  <tr>
                    <th style={S.th}>Value Name</th>
                    <th style={S.th}>Class</th>
                    <th style={S.th}>Policy</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p) => (
                    <PolicyRow
                      key={p.id}
                      policy={p}
                      onSelect={setSelectedPolicy}
                      selected={selectedPolicy}
                    />
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Detail drawer */}
        {selectedPolicy && (
          <PolicyDetail policy={selectedPolicy} onClose={() => setSelectedPolicy(null)} />
        )}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #444; }
      `}</style>
    </div>
  );
}
