$startup = [System.Environment]::GetFolderPath('Startup')
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$startup\GF Lead Hunter.lnk")
$Shortcut.TargetPath = "C:\Users\genna\Desktop\gf-lead-hunter\AVVIA_DASHBOARD.bat"
$Shortcut.WorkingDirectory = "C:\Users\genna\Desktop\gf-lead-hunter"
$Shortcut.Description = "GF Lead Hunter Dashboard"
$Shortcut.Save()
Write-Host "Avvio automatico configurato in: $startup"
