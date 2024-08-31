# Check if the Docker container exists
$containerExists = docker ps -aq --filter "name=viewfarm_v2"

# If the container doesn't exist, build it
if (!$containerExists) {
    Write-Host "Building Docker container..."
    & .\build.ps1
}

# Schedule the container to run once a day 3:35PM
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"& .\run.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 16:40
$principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 8)
$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Register-ScheduledTask -TaskName "RunViewFarm" -InputObject $task