import { useState, useEffect, useRef } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Terminal, Copy, Check, Search, X, Loader2, AlertTriangle } from 'lucide-react';
import { searchByKeyword } from '../services/api';

const SCRIPT_TYPES = ['Remediation', 'Detection', 'Rollback', 'Validation'];

const MOCK_SCRIPTS = {
  Remediation: `<#
.SYNOPSIS
  Remediation script — Enforce minimum password length
.DESCRIPTION
  Applies registry settings and creates rollback snapshot.
#>
$ErrorActionPreference = "Stop"

$rollbackDir = "C:\\PolicyRollbacks\\PasswordLength"
if (-not (Test-Path $rollbackDir)) {
    New-Item -ItemType Directory -Force -Path $rollbackDir | Out-Null
}

# Export current value for rollback
reg export "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Network" \`
    "$rollbackDir\\snapshot.reg" /y 2>$null

$regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Network"
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

Set-ItemProperty -Path $regPath -Name "MinPwdLen" -Value 14 -Type DWORD -Force
Write-Output "[SUCCESS] Minimum password length set to 14."
exit 0`,
  Detection: `<#
.SYNOPSIS
  Detection script — Enforce minimum password length
#>
$regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Network"
$expected = 14

try {
    $current = (Get-ItemProperty -Path $regPath -Name "MinPwdLen" -EA Stop).MinPwdLen
    if ($current -ge $expected) {
        Write-Output "[COMPLIANT] MinPwdLen = $current"
        exit 0
    } else {
        Write-Output "[NON-COMPLIANT] MinPwdLen = $current (expected >= $expected)"
        exit 1
    }
} catch {
    Write-Output "[NON-COMPLIANT] Registry key not found."
    exit 1
}`,
  Rollback: `<#
.SYNOPSIS
  Rollback script — Restore previous registry state
#>
$rollbackFile = "C:\\PolicyRollbacks\\PasswordLength\\snapshot.reg"

if (Test-Path $rollbackFile) {
    reg import $rollbackFile
    Write-Output "[SUCCESS] Rollback applied from $rollbackFile"
    exit 0
} else {
    Write-Output "[ERROR] No rollback snapshot found at $rollbackFile"
    exit 1
}`,
  Validation: `<#
.SYNOPSIS
  Validation script — Verify policy is correctly applied
#>
$regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Network"

try {
    $value = (Get-ItemProperty -Path $regPath -Name "MinPwdLen" -EA Stop).MinPwdLen
    Write-Output "[VALIDATED] MinPwdLen = $value"
} catch {
    Write-Output "[FAILED] Could not read registry value."
    exit 1
}`,
};

export default function ScriptGenerator() {
  const [activeType, setActiveType] = useState('Remediation');
  const [copied, setCopied] = useState(false);

  // Dialog state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const searchInputRef = useRef(null);

  // Script generation state
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [generatedScript, setGeneratedScript] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState(null);

  // Focus search input when dialog opens
  useEffect(() => {
    if (isDialogOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isDialogOpen]);

  // Fetch script when policy or type changes
  useEffect(() => {
    if (!selectedPolicy) {
      setGeneratedScript(MOCK_SCRIPTS[activeType]);
      return;
    }

    const fetchScript = async () => {
      setIsGenerating(true);
      setGenerateError(null);
      try {
        const typeParam = activeType.toLowerCase();
        const response = await fetch(`http://127.0.0.1:8000/scripts/generate/${encodeURIComponent(selectedPolicy.name)}?script_type=${typeParam}`);

        if (!response.ok) {
          throw new Error(`Failed to generate script: ${response.statusText}`);
        }

        const scriptText = await response.text();
        setGeneratedScript(scriptText);
      } catch (err) {
        setGenerateError(err.message);
        setGeneratedScript('');
      } finally {
        setIsGenerating(false);
      }
    };

    fetchScript();
  }, [selectedPolicy, activeType]);

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedScript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setSearchError(null);
    try {
      const data = await searchByKeyword(searchQuery, 1, 20);
      setSearchResults(data.items);
    } catch (err) {
      setSearchError(err?.response?.data?.detail || 'Failed to search policies');
    } finally {
      setIsSearching(false);
    }
  };

  const selectPolicy = (policy) => {
    setSelectedPolicy(policy);
    setIsDialogOpen(false);
    setSearchQuery('');
    setSearchResults(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>PowerShell Script Generator</h1>
          {selectedPolicy && (
             <div style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#60a5fa' }}>
               Selected: {selectedPolicy.display_name || selectedPolicy.name}
             </div>
          )}
        </div>
        <button
          onClick={() => setIsDialogOpen(true)}
          style={{
            padding: '0.6rem 1.25rem', background: '#0078D4', border: 'none',
            borderRadius: '0.5rem', color: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600,
          }}>
          {selectedPolicy ? 'Change Policy →' : 'Select Policy →'}
        </button>
      </div>

      {/* Select Policy Dialog */}
      {isDialogOpen && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem'
        }}>
          <div style={{
            background: '#1a1a1a', border: '1px solid #333', borderRadius: '0.75rem',
            width: '100%', maxWidth: 600, maxHeight: '85vh', display: 'flex', flexDirection: 'column',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', overflow: 'hidden'
          }}>
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '1rem 1.5rem', borderBottom: '1px solid #333', background: '#111'
            }}>
              <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#fff' }}>Select Policy</h2>
              <button
                onClick={() => setIsDialogOpen(false)}
                style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', display: 'flex' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
              <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search policies..."
                    style={{
                      width: '100%', boxSizing: 'border-box', background: '#111', border: '1px solid #333',
                      borderRadius: '0.5rem', padding: '0.6rem 1rem 0.6rem 2.25rem', color: '#fff', outline: 'none'
                    }}
                    onFocus={e => e.target.style.borderColor = '#0078D4'}
                    onBlur={e => e.target.style.borderColor = '#333'}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  style={{
                    padding: '0 1.25rem', background: isSearching || !searchQuery.trim() ? '#1a3a5c' : '#0078D4',
                    border: 'none', borderRadius: '0.5rem', color: '#fff', fontWeight: 600, cursor: isSearching || !searchQuery.trim() ? 'not-allowed' : 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}
                >
                  {isSearching ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : 'Search'}
                </button>
              </form>

              {searchError && (
                <div style={{ color: '#f87171', fontSize: '0.875rem', padding: '0.5rem', background: 'rgba(239,68,68,0.1)', borderRadius: '0.375rem' }}>
                  {searchError}
                </div>
              )}

              {searchResults && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: 600 }}>RESULTS ({searchResults.length})</div>
                  {searchResults.length === 0 ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: '#6b7280', fontSize: '0.875rem' }}>No policies found.</div>
                  ) : (
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {searchResults.map(policy => (
                        <li key={policy.id || policy.name}>
                          <button
                            onClick={() => selectPolicy(policy)}
                            style={{
                              width: '100%', textAlign: 'left', padding: '0.75rem', background: 'transparent',
                              border: '1px solid transparent', borderRadius: '0.375rem', cursor: 'pointer',
                              display: 'flex', flexDirection: 'column', gap: '0.25rem', transition: 'all 0.15s'
                            }}
                            onMouseOver={e => { e.currentTarget.style.background = '#1f1f1f'; e.currentTarget.style.borderColor = '#333'; }}
                            onMouseOut={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'transparent'; }}
                          >
                            <div style={{ color: '#60a5fa', fontWeight: 500, fontSize: '0.9rem', wordBreak: 'break-word' }}>
                              {policy.display_name || policy.name}
                            </div>
                            {policy.gpo_path && (
                              <div style={{ color: '#6b7280', fontSize: '0.75rem', fontFamily: 'monospace', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {policy.gpo_path}
                              </div>
                            )}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Type tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {SCRIPT_TYPES.map(type => (
          <button
            key={type}
            onClick={() => setActiveType(type)}
            style={{
              padding: '0.4rem 1rem', borderRadius: '0.375rem', border: '1px solid',
              fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s',
              background: activeType === type ? '#0078D4' : 'transparent',
              borderColor: activeType === type ? '#0078D4' : '#333',
              color: activeType === type ? '#fff' : '#9ca3af',
            }}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Script viewer */}
      <div style={{ background: '#1a1a1a', borderRadius: '0.625rem', border: '1px solid #2a2a2a', overflow: 'hidden' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0.75rem 1.25rem', background: '#111', borderBottom: '1px solid #2a2a2a',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Terminal size={16} style={{ color: '#0078D4' }} />
            <span style={{ fontFamily: 'monospace', fontSize: '0.82rem', color: '#9ca3af' }}>
              {activeType.toLowerCase()}.ps1
            </span>
          </div>
          <button
            onClick={handleCopy}
            disabled={isGenerating || !!generateError}
            title="Copy to clipboard"
            style={{
              background: copied ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)',
              border: `1px solid ${copied ? 'rgba(34,197,94,0.3)' : '#333'}`,
              borderRadius: '0.375rem', padding: '0.3rem 0.625rem',
              cursor: isGenerating || !!generateError ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              color: copied ? '#22c55e' : '#9ca3af', fontSize: '0.78rem', transition: 'all 0.2s',
              opacity: isGenerating || !!generateError ? 0.5 : 1
            }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>

        <div style={{ maxHeight: 520, overflowY: 'auto', minHeight: 200, position: 'relative' }}>
          {isGenerating ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 200, gap: '1rem', color: '#6b7280' }}>
              <Loader2 size={32} style={{ animation: 'spin 1s linear infinite', color: '#0078D4' }} />
              <span>Generating script...</span>
            </div>
          ) : generateError ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 200, gap: '1rem', color: '#f87171' }}>
              <AlertTriangle size={32} />
              <span>{generateError}</span>
            </div>
          ) : (
            <SyntaxHighlighter
              language="powershell"
              style={vscDarkPlus}
              customStyle={{ margin: 0, background: 'transparent', fontSize: '0.82rem', padding: '1.25rem' }}
            >
              {generatedScript || '# No script generated.'}
            </SyntaxHighlighter>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
