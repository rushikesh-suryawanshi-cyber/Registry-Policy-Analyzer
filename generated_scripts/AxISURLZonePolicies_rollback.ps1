<#
.SYNOPSIS
Rollback script for policy: AxISURLZonePolicies

.DESCRIPTION
Restores the registry state using the latest exported .reg snapshots.
#>

$rollbackDir = "C:\PolicyRollbacks\AxISURLZonePolicies"

if (-not (Test-Path $rollbackDir)) {
    Write-Output "No rollback directory found at $rollbackDir."
    exit 1
}

$regFiles = Get-ChildItem -Path $rollbackDir -Filter "*.reg" | Sort-Object LastWriteTime -Descending

if ($regFiles.Count -eq 0) {
    Write-Output "No rollback snapshots found in $rollbackDir."
    exit 1
}

# Import the most recent snapshots
# For simplicity, we import all .reg files from the most recent run (matching timestamp)
$latestTimestamp = $regFiles[0].Name.Split('_')[2] + "_" + $regFiles[0].Name.Split('_')[3].Replace('.reg','')

$filesToRestore = $regFiles | Where-Object { $_.Name -match $latestTimestamp }

foreach ($file in $filesToRestore) {
    Write-Output "Restoring snapshot: $($file.FullName)"
    & reg.exe import $file.FullName
}

Write-Output "Rollback complete."
exit 0