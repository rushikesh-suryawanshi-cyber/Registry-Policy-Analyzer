<#
.SYNOPSIS
Detection script for policy: AxISURLZonePolicies

.DESCRIPTION
Checks if the registry settings for this policy are applied.
#>

$isCompliant = $true



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 2) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 2) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
    }
}



if ($isCompliant) {
    Write-Output "Compliant"
    exit 0
} else {
    Write-Output "Non-Compliant"
    exit 1
}