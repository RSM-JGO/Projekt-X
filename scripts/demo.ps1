<#
.SYNOPSIS
    Externe Demo von Projekt X starten, stoppen oder mit Beispieldaten füllen.

.DESCRIPTION
    start  : migrate, collectstatic, check --deploy, Waitress auf 127.0.0.1:<PX_PORT> und
             Microsoft Dev Tunnel (devtunnel host <PX_TUNNEL_ID>) im Hintergrund starten.
    stop   : Tunnel und Waitress beenden (ganzer Prozessbaum) und prüfen, dass der Port frei ist.
    seed   : Beispieldaten in die Demo-Datenbank laden (seed_demo, nur Instanz demo).
    status : Zeigt, ob Waitress und Tunnel laufen.

    Konfiguration ausschließlich aus .env.demo (PX_ENV_FILE). Das Skript gibt keine
    Passwörter oder Geheimnisse aus. Prozess-IDs und Protokolle liegen im ignorierten Ordner run\.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 start
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('start', 'stop', 'seed', 'status')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$RunDir = Join-Path $Root 'run'
$EnvFile = Join-Path $Root '.env.demo'
$WaitressPidFile = Join-Path $RunDir 'demo-waitress.pid'
$TunnelPidFile = Join-Path $RunDir 'demo-tunnel.pid'

# uv-Umgebung wie in der Entwicklung (Python liegt im Benutzer-Installationsordner)
$env:UV_PYTHON_INSTALL_DIR = [Environment]::GetEnvironmentVariable('UV_PYTHON_INSTALL_DIR', 'User')
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
$env:PX_ENV_FILE = $EnvFile
$env:PYTHONPATH = Join-Path $Root 'src'

function Get-DemoSetting([string]$Name, [string]$Default = '') {
    # Liest nur einzelne, nicht geheime Werte (Port, Tunnel-ID) aus .env.demo
    foreach ($line in Get-Content -LiteralPath $EnvFile) {
        if ($line -match "^\s*$Name\s*=\s*(.*)\s*$") { return $Matches[1].Trim() }
    }
    return $Default
}

function Invoke-Manage([string[]]$Arguments) {
    Push-Location $Root
    try {
        & uv run python manage.py @Arguments
        if ($LASTEXITCODE -ne 0) { throw "manage.py $($Arguments -join ' ') ist fehlgeschlagen." }
    } finally { Pop-Location }
}

function Stop-Tree([string]$PidFile, [string]$Label) {
    if (-not (Test-Path -LiteralPath $PidFile)) { return }
    $procId = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    if ($procId -and (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
        # /T beendet auch Kindprozesse (uv startet Python als Kind)
        & taskkill.exe /PID $procId /T /F | Out-Null
        Write-Host "$Label beendet (PID $procId)."
    }
    Remove-Item -LiteralPath $PidFile -Force
}

function Get-PortListener([int]$Port) {
    Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
}

function Test-Running([string]$PidFile) {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $false }
    $procId = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    return [bool](Get-Process -Id $procId -ErrorAction SilentlyContinue)
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw '.env.demo fehlt. Bitte nach dem Muster .env.demo.example anlegen.'
}
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
$Port = [int](Get-DemoSetting 'PX_PORT' '8100')

switch ($Action) {
    'seed' {
        Invoke-Manage @('seed_demo')
    }

    'status' {
        Write-Host ("Waitress: " + $(if (Test-Running $WaitressPidFile) { 'läuft' } else { 'gestoppt' }))
        Write-Host ("Tunnel:   " + $(if (Test-Running $TunnelPidFile) { 'läuft' } else { 'gestoppt' }))
    }

    'start' {
        if ((Test-Running $WaitressPidFile) -or (Test-Running $TunnelPidFile)) {
            throw 'Die Demo läuft bereits. Zuerst "stop" ausführen.'
        }
        if (Get-PortListener $Port) { throw "Port $Port ist bereits belegt." }
        $tunnelId = Get-DemoSetting 'PX_TUNNEL_ID'
        if (-not $tunnelId -or $tunnelId -eq 'HIER_TUNNEL_ID') { throw 'PX_TUNNEL_ID fehlt in .env.demo.' }
        if (-not (Get-Command devtunnel -ErrorAction SilentlyContinue)) {
            throw 'devtunnel ist nicht installiert oder nicht im PATH.'
        }

        Invoke-Manage @('migrate', '--noinput')
        Invoke-Manage @('collectstatic', '--noinput')
        # Sicherheitsprüfung: bei Warnungen wird nicht gestartet
        Invoke-Manage @('check', '--deploy', '--fail-level', 'WARNING')

        $waitress = Start-Process -FilePath 'uv' -WorkingDirectory $Root -WindowStyle Hidden -PassThru `
            -ArgumentList @('run', 'waitress-serve', "--listen=127.0.0.1:$Port",
                # Der Tunnel verbindet sich lokal; nur ihm werden die Forwarded-Header geglaubt
                '--trusted-proxy=127.0.0.1', '--trusted-proxy-count=1',
                '--trusted-proxy-headers="x-forwarded-for x-forwarded-host x-forwarded-proto x-forwarded-port"',
                'config.wsgi:application') `
            -RedirectStandardOutput (Join-Path $RunDir 'demo-waitress.log') `
            -RedirectStandardError (Join-Path $RunDir 'demo-waitress.err.log')
        Set-Content -LiteralPath $WaitressPidFile -Value $waitress.Id

        $ok = $false
        for ($i = 0; $i -lt 30 -and -not $ok; $i++) {
            Start-Sleep -Seconds 1
            try {
                $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health/" -UseBasicParsing -TimeoutSec 2
                $ok = $r.StatusCode -eq 200
            } catch { $ok = $false }
        }
        if (-not $ok) {
            Stop-Tree $WaitressPidFile 'Waitress'
            throw 'Waitress antwortet nicht. Siehe run\demo-waitress.err.log.'
        }
        Write-Host "Waitress läuft auf http://127.0.0.1:$Port (nur lokal)."

        # Origin und Host unverändert durchreichen, sonst setzt Dev Tunnels beide auf
        # "localhost" und Djangos CSRF-Herkunftsprüfung schlägt im Browser fehl
        $tunnel = Start-Process -FilePath 'devtunnel' -WindowStyle Hidden -PassThru `
            -ArgumentList @('host', $tunnelId, '--origin-header', 'unchanged', '--host-header', 'unchanged') `
            -RedirectStandardOutput (Join-Path $RunDir 'demo-tunnel.log') `
            -RedirectStandardError (Join-Path $RunDir 'demo-tunnel.err.log')
        Set-Content -LiteralPath $TunnelPidFile -Value $tunnel.Id
        Start-Sleep -Seconds 3
        if (-not (Test-Running $TunnelPidFile)) {
            Stop-Tree $WaitressPidFile 'Waitress'
            throw 'Der Tunnel ist sofort beendet worden. Siehe run\demo-tunnel.err.log.'
        }
        Write-Host 'Tunnel läuft. Adresse siehe run\demo-tunnel.log. Stoppen: scripts\demo.ps1 stop'
    }

    'stop' {
        # Zuerst den Tunnel, damit von außen sofort nichts mehr erreichbar ist
        Stop-Tree $TunnelPidFile 'Tunnel'
        Stop-Tree $WaitressPidFile 'Waitress'
        $rest = Get-PortListener $Port
        foreach ($conn in $rest) {
            $p = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($p -and $p.ProcessName -match '^(python|waitress-serve|uv)$') {
                & taskkill.exe /PID $p.Id /T /F | Out-Null
                Write-Host "Restprozess auf Port $Port beendet (PID $($p.Id))."
            }
        }
        if (Get-PortListener $Port) { throw "Port $Port ist weiterhin belegt. Bitte manuell prüfen." }
        Write-Host 'Demo gestoppt. Von außen ist nichts mehr erreichbar.'
    }
}
