# Install the `scoop` package manager.
# For execution policy issues, check: https:/go.microsoft.com/fwlink/?LinkID=135170

Write-Host "`nInstalling Scoop...`n"

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

Write-Host "`nScoop installation completed; press enter/return to exit...`n"
Read-Host -Prompt "`n"

