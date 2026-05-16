<#
.SYNOPSIS
Validation script for policy: AxISURLZonePolicies

.DESCRIPTION
Validates that the policy is successfully applied post-remediation.
#>

$isCompliant = $true
$errors = @()



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 0, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 1, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallTrustedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 2) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 2, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 0, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 1, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 2) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 2, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 0) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 0, Got: $currentVal)"
    }
}



$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AxInstaller\AxISURLZonePolicies"
$valName = "InstallUnSignedOCX"


if (-not (Test-Path $regPath)) {
    $isCompliant = $false
    $errors += "Missing registry key: $regPath"
} else {
    $currentVal = (Get-ItemProperty -Path $regPath -Name $valName -ErrorAction SilentlyContinue).$valName
    
    if ($null -eq $currentVal -or [int]$currentVal -ne 1) {
    
        $isCompliant = $false
        $errors += "Value mismatch at $regPath\$valName (Expected: 1, Got: $currentVal)"
    }
}



if ($isCompliant) {
    Write-Output "Validation Passed: Policy is compliant."
    exit 0
} else {
    Write-Output "Validation Failed: Policy is non-compliant."
    $errors | ForEach-Object { Write-Output " - $_" }
    exit 1
}