#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Autonomous Results Agent Startup Script
.DESCRIPTION
    Starts the autonomous results management system for intelligent categorization and organization of AI system results
.PARAMETER Mode
    Startup mode: 'agent' (default), 'api', or 'both'
.PARAMETER Config
    Path to configuration file (default: config/agent-config.json)
.EXAMPLE
    .\start-results-agent.ps1 -Mode both
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('agent', 'api', 'both')]
    [string]$Mode = 'both',

    [Parameter(Mandatory=$false)]
    [string]$Config = 'config/agent-config.json'
)

$ErrorActionPreference = 'Stop'

# Configuration
$RESULTS_ROOT = $PSScriptRoot
$AGENT_SCRIPT = Join-Path $RESULTS_ROOT 'dist/autonomous-results-agent.js'
$API_SCRIPT = Join-Path $RESULTS_ROOT 'dist/api-server.js'
$LOG_DIR = Join-Path $RESULTS_ROOT 'logs'
$PID_DIR = Join-Path $RESULTS_ROOT 'pids'

# Ensure directories exist
if (!(Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR | Out-Null }
if (!(Test-Path $PID_DIR)) { New-Item -ItemType Directory -Path $PID_DIR | Out-Null }

# Function to check if process is running
function Test-ProcessRunning {
    param([int]$ProcessId)
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        return $null -ne $process
    } catch {
        return $false
    }
}

# Function to start agent
function Start-ResultsAgent {
    Write-Host "🚀 Starting Autonomous Results Agent..." -ForegroundColor Green

    # Check if already running
    $pidFile = Join-Path $PID_DIR 'agent.pid'
    if (Test-Path $pidFile) {
        $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($existingPid -and (Test-ProcessRunning -ProcessId $existingPid)) {
            Write-Host "⚠️  Agent is already running (PID: $existingPid)" -ForegroundColor Yellow
            return
        }
    }

    # Build if needed
    if (!(Test-Path $AGENT_SCRIPT)) {
        Write-Host "🔨 Building agent..." -ForegroundColor Cyan
        & npm run build
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build agent"
            exit 1
        }
    }

    # Start agent in background
    $logFile = Join-Path $LOG_DIR 'agent.log'
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = 'node'
    $startInfo.Arguments = $AGENT_SCRIPT
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $process.Start() | Out-Null

    # Save PID
    $process.Id | Out-File $pidFile

    Write-Host "✅ Agent started (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "📝 Logs: $logFile" -ForegroundColor Gray
}

# Function to start API server
function Start-ResultsAPI {
    Write-Host "🌐 Starting Results API Server..." -ForegroundColor Green

    # Check if already running
    $pidFile = Join-Path $PID_DIR 'api.pid'
    if (Test-Path $pidFile) {
        $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($existingPid -and (Test-ProcessRunning -ProcessId $existingPid)) {
            Write-Host "⚠️  API server is already running (PID: $existingPid)" -ForegroundColor Yellow
            return
        }
    }

    # Build if needed
    if (!(Test-Path $API_SCRIPT)) {
        Write-Host "🔨 Building API server..." -ForegroundColor Cyan
        & npm run build
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build API server"
            exit 1
        }
    }

    # Start API server in background
    $logFile = Join-Path $LOG_DIR 'api.log'
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = 'node'
    $startInfo.Arguments = $API_SCRIPT
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $process.Start() | Out-Null

    # Save PID
    $process.Id | Out-File $pidFile

    Write-Host "✅ API server started (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "📝 Logs: $logFile" -ForegroundColor Gray
    Write-Host "🔗 API: http://localhost:8081" -ForegroundColor Gray
}

# Function to stop services
function Stop-ResultsServices {
    Write-Host "🛑 Stopping Results Services..." -ForegroundColor Yellow

    $services = @('agent', 'api')
    foreach ($service in $services) {
        $pidFile = Join-Path $PID_DIR "$service.pid"
        if (Test-Path $pidFile) {
            $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
            if ($pid -and (Test-ProcessRunning -ProcessId $pid)) {
                try {
                    Stop-Process -Id $pid -Force
                    Write-Host "✅ Stopped $service (PID: $pid)" -ForegroundColor Green
                } catch {
                    Write-Host "❌ Failed to stop $service (PID: $pid)" -ForegroundColor Red
                }
            }
            Remove-Item $pidFile -ErrorAction SilentlyContinue
        }
    }
}

# Function to check status
function Get-ResultsStatus {
    Write-Host "📊 Results System Status" -ForegroundColor Cyan
    Write-Host "─" * 40 -ForegroundColor Gray

    $services = @('agent', 'api')
    foreach ($service in $services) {
        $pidFile = Join-Path $PID_DIR "$service.pid"
        $status = "❌ Stopped"
        $processId = "N/A"

        if (Test-Path $pidFile) {
            $processId = Get-Content $pidFile -ErrorAction SilentlyContinue
            if ($processId -and (Test-ProcessRunning -ProcessId $processId)) {
                $status = "✅ Running"
            }
        }

        Write-Host "$($service.ToUpper()): $status (PID: $processId)" -ForegroundColor White
    }

    # Check API health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8081/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "API Health: ✅ Healthy" -ForegroundColor Green
        } else {
            Write-Host "API Health: ⚠️  Unhealthy" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "API Health: ❌ Unreachable" -ForegroundColor Red
    }
}

# Main execution
try {
    Set-Location $RESULTS_ROOT

    # Check if config exists
    if (!(Test-Path $Config)) {
        Write-Error "Configuration file not found: $Config"
        exit 1
    }

    Write-Host "🤖 Autonomous Results Management System" -ForegroundColor Magenta
    Write-Host "Config: $Config" -ForegroundColor Gray
    Write-Host ""

    switch ($Mode) {
        'agent' {
            Start-ResultsAgent
        }
        'api' {
            Start-ResultsAPI
        }
        'both' {
            Start-ResultsAgent
            Start-Sleep -Seconds 2
            Start-ResultsAPI
        }
    }

    Write-Host ""
    Get-ResultsStatus

    Write-Host ""
    Write-Host "🎯 Useful commands:" -ForegroundColor Cyan
    Write-Host "  Stop services: .\\$($MyInvocation.MyCommand.Name) -Stop" -ForegroundColor Gray
    Write-Host "  Check status:  .\\$($MyInvocation.MyCommand.Name) -Status" -ForegroundColor Gray
    Write-Host "  View logs:     Get-Content .\\logs\\*.log -Tail 20 -Wait" -ForegroundColor Gray

} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
