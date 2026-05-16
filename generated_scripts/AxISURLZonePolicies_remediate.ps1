<#
.SYNOPSIS
Remediation script for policy: AxISURLZonePolicies

.DESCRIPTION
Applies the required registry settings and creates a rollback snapshot.
#>

$ErrorActionPreference = "Stop"

# Create Rollback Directory
$rollbackDir = "C:\PolicyRollbacks\AxISURLZonePolicies"
if (-not (Test-Path $rollbackDir)) {
    New-Item -ItemType Directory -Force -Path $rollbackDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_1_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 0


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_2_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 1


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_3_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 2


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_4_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 0


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_5_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 1


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_6_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 2


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_7_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 0


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"

# Snapshot existing key if it exists
if (Test-Path $regPath) {
    $exportPath = Join-Path $rollbackDir "HKLM_8_$timestamp.reg"
    # Using reg.exe to export
    & reg.exe export "HKLM\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies" $exportPath /y | Out-Null
}

# Ensure parent key exists
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}



$valData = 1


Set-ItemProperty -Path $regPath -Name $valName -Value $valData -Type DWORD -Force | Out-Null
Write-Output "Set $valName in $regPath"



Write-Output "Remediation complete."
exit 0