$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $root 'dist\AuraAgenda.exe'
if (!(Test-Path $exe)) { throw "Build dist\AuraAgenda.exe first." }
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut((Join-Path $desktop 'AuraAgenda.lnk'))
$link.TargetPath = $exe
$link.WorkingDirectory = Split-Path $exe
$link.IconLocation = $exe
$link.Description = 'AuraAgenda — Personal Life Planner'
$link.Save()
