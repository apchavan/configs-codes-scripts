# Print the current PowerShell version.
# For execution policy issues, check: https:/go.microsoft.com/fwlink/?LinkID=135170

$currentPowerShellVersion = $PSVersionTable.PSVersion

Write-Host "`nYour PowerShell version is: $currentPowerShellVersion"

Read-Host -Prompt "`n`nPress a key to exit..."

