import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Terminal, Copy, Check, ChevronDown } from 'lucide-react';

const SCRIPT_TYPES = ['Remediation', 'Detection', 'Rollback', 'Validation'];

const SCRIPTS = {
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

  const handleCopy = () => {
    navigator.clipboard.writeText(SCRIPTS[activeType]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>PowerShell Script Generator</h1>
        <button style={{
          padding: '0.6rem 1.25rem', background: '#0078D4', border: 'none',
          borderRadius: '0.5rem', color: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600,
        }}>
          Select Policy →
        </button>
      </div>

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
            title="Copy to clipboard"
            style={{
              background: copied ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)',
              border: `1px solid ${copied ? 'rgba(34,197,94,0.3)' : '#333'}`,
              borderRadius: '0.375rem', padding: '0.3rem 0.625rem', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              color: copied ? '#22c55e' : '#9ca3af', fontSize: '0.78rem', transition: 'all 0.2s',
            }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div style={{ maxHeight: 520, overflowY: 'auto' }}>
          <SyntaxHighlighter
            language="powershell"
            style={vscDarkPlus}
            customStyle={{ margin: 0, background: 'transparent', fontSize: '0.82rem', padding: '1.25rem' }}
          >
            {SCRIPTS[activeType]}
          </SyntaxHighlighter>
        </div>
      </div>
    </div>
  );
}
