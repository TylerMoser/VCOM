```powershell
# USAGE: .\Start-RemoteClaude.ps1 -DeviceName "AI-PC" -Model "gemma4:26b-a4b-it-q4_K_M"

<#
================================================================================
 Remote Ollama + Claude Code Launcher
================================================================================

DESCRIPTION
-----------
This script assumes the remote Windows PC has ALREADY been powered on.

It:

  1. Verifies that the remote PC is reachable.
  2. Connects to it using PowerShell Remoting / WinRM.
  3. Starts Ollama with LAN access enabled.
  4. Downloads the requested Ollama model if it is not already installed.
  5. Opens the Ollama port through Windows Firewall.
  6. Loads the requested model into Ollama.
  7. Verifies that Ollama can be reached from this computer.
  8. Configures Claude Code to use the remote Ollama server.
  9. Launches Claude Code on THIS computer using the remote model.

Claude Code runs on the current computer.

Ollama and the model run on the remote computer.


================================================================================
 DEFAULT VALUES
================================================================================

Change these values to match your normal setup:

    DeviceName
        Windows hostname of the remote PC.

    Model
        Ollama model that Claude Code should use.

Example defaults:

    DeviceName = "AI-PC"
    Model      = "gemma4:26b-a4b-it-q4_K_M"

With the defaults configured, simply run:

    .\Start-RemoteClaude.ps1

You can override either value from the command line:

    .\Start-RemoteClaude.ps1 -Model "qwen3:30b"

or:

    .\Start-RemoteClaude.ps1 -DeviceName "AI-PC-2"

or:

    .\Start-RemoteClaude.ps1 `
        -DeviceName "AI-PC-2" `
        -Model "qwen3:30b"


================================================================================
 PREREQUISITES - REMOTE PC
================================================================================

The remote PC must be manually powered on BEFORE running this script.

1. WINDOWS
   --------
   The remote machine must be running Windows and connected to the same
   local network as this computer.

2. OLLAMA
   -------
   Install Ollama on the remote PC.

   The model does NOT need to be downloaded beforehand. This script will
   automatically run:

       ollama pull <model>

   if the requested model is not already installed.

3. POWERSHELL REMOTING / WINRM
   ---------------------------
   PowerShell Remoting must be enabled on the remote PC.

   Run PowerShell as Administrator ON THE REMOTE PC:

       Enable-PSRemoting -Force

   Verify from this computer:

       Test-WSMan <DeviceName>

   For example:

       Test-WSMan AI-PC

   If Test-WSMan fails, this script will not be able to start Ollama.

4. USER PERMISSIONS
   -----------------
   The Windows account running this script must have permission to use
   PowerShell Remoting on the remote PC.

   The easiest configuration is generally to use the same Windows account
   or credentials on both machines.

5. WINDOWS FIREWALL
   -----------------
   The script creates a Windows Firewall rule on the remote PC allowing
   inbound TCP traffic on Ollama's default port:

       TCP 11434

   The rule is named:

       Ollama LAN Access

   The rule is created for the Private network profile.

   Make sure the remote PC's network is classified as Private if necessary.


================================================================================
 PREREQUISITES - CURRENT PC
================================================================================

The computer running this script needs:

1. PowerShell.

2. Network access to the remote PC.

3. Claude Code installed and available as:

       claude

   or:

       claude.exe

   Verify with:

       claude --version

4. The remote PC's hostname must resolve from this computer.

   Test with:

       ping <DeviceName>

   For example:

       ping AI-PC

   NOTE:
   Ping itself is not required by this script. The script checks the
   PowerShell Remoting port instead. Successful hostname resolution is
   nevertheless necessary.

5. The current computer must have network access to TCP port 11434 on
   the remote PC.


================================================================================
 FIRST-TIME REMOTE PC SETUP
================================================================================

Perform these steps ONCE on the remote PC.

1. Install Ollama.

2. Verify Ollama works locally.

3. Open PowerShell as Administrator.

4. Enable PowerShell Remoting:

       Enable-PSRemoting -Force

5. Make sure the Windows network is classified as Private.

6. From the current computer, verify WinRM:

       Test-WSMan <DeviceName>

   Example:

       Test-WSMan AI-PC


================================================================================
 OLLAMA LAN ACCESS
================================================================================

Ollama normally listens only on localhost.

Claude Code is running on THIS computer, however, so Ollama must listen
on the remote PC's network interface.

The script starts Ollama with:

    OLLAMA_HOST=0.0.0.0:11434

This allows Ollama's HTTP API to accept connections through the LAN.

Claude Code will connect to:

    http://<DeviceName>:11434

For example:

    http://AI-PC:11434


================================================================================
 CLAUDE CODE CONFIGURATION
================================================================================

The script configures Claude Code using:

    ANTHROPIC_BASE_URL
    ANTHROPIC_AUTH_TOKEN

It sets:

    ANTHROPIC_BASE_URL=http://<DeviceName>:11434
    ANTHROPIC_AUTH_TOKEN=ollama

The requested Ollama model is passed to Claude Code with:

    claude --model <Model>

The authentication token is required by Ollama's Anthropic-compatible
endpoint but does not represent a real Ollama password.


================================================================================
 FIRST-TIME SETUP CHECKLIST
================================================================================

REMOTE PC:

  [ ] Manually turn on the PC.
  [ ] Install Ollama.
  [ ] Verify Ollama works locally.
  [ ] Enable PowerShell Remoting:
          Enable-PSRemoting -Force
  [ ] Make sure the PC is connected to the LAN.
  [ ] Make sure the Windows network profile is Private.

CURRENT PC:

  [ ] Install Claude Code.
  [ ] Verify:
          claude --version
  [ ] Verify the remote PC name resolves:
          ping <DeviceName>
  [ ] Verify WinRM:
          Test-WSMan <DeviceName>


================================================================================
 EXAMPLES
================================================================================

Using the defaults:

    .\Start-RemoteClaude.ps1


Using a different model:

    .\Start-RemoteClaude.ps1 `
        -Model "qwen3:30b"


Using a different remote PC:

    .\Start-RemoteClaude.ps1 `
        -DeviceName "AI-PC-2"


Override everything:

    .\Start-RemoteClaude.ps1 `
        -DeviceName "AI-PC-2" `
        -Model "qwen3:30b"


================================================================================
 IMPORTANT NOTES
================================================================================

- The remote PC MUST be manually powered on before running this script.

- Wake-on-LAN is NOT used by this script.

- The MAC address of the remote PC is NOT required.

- The remote PC must remain connected to the LAN while Claude Code is
  using the model.

- The first time a model is used, downloading it may take a significant
  amount of time.

- Loading a large model into RAM/VRAM can also take considerable time.

- Claude Code runs on the current PC.

- Ollama and the model run on the remote PC.

- The script does not install Ollama or Claude Code automatically.

- Ollama uses TCP port 11434 by default.

================================================================================
 #>

param(
    [Parameter(Mandatory = $false)]
    [string]$DeviceName = "TvDesktop",

    [Parameter(Mandatory = $false)]
    [string]$Model = "gemma4:26b-a4b-it-q4_K_M"
)

$ErrorActionPreference = "Stop"

# ============================================================================
# CONFIGURATION
# ============================================================================

$OllamaPort = 11434

# Maximum amount of time to wait for the remote PC's WinRM service.
$RemoteTimeoutSeconds = 60

# Maximum amount of time to wait for Ollama to start.
$OllamaTimeoutSeconds = 60


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Step {
    param([string]$Message)

    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}


function Test-TcpPort {
    param(
        [string]$ComputerName,
        [int]$Port
    )

    try {

        $client = [System.Net.Sockets.TcpClient]::new()

        $async = $client.BeginConnect(
            $ComputerName,
            $Port,
            $null,
            $null
        )

        $success = $async.AsyncWaitHandle.WaitOne(1500)

        if ($success -and $client.Connected) {

            $client.EndConnect($async)
            $client.Dispose()

            return $true
        }

        $client.Dispose()

        return $false
    }
    catch {

        return $false
    }
}


# ============================================================================
# 1. CHECK REMOTE PC
# ============================================================================

Write-Step "Checking whether $DeviceName is available..."

$remoteOnline = Test-TcpPort `
    -ComputerName $DeviceName `
    -Port 5985

if (-not $remoteOnline) {

    throw @"
The remote PC '$DeviceName' is not reachable.

Make sure:

  1. The PC is powered on.
  2. It is connected to the network.
  3. PowerShell Remoting is enabled.
  4. Windows Firewall allows WinRM.
  5. The device name is correct.

You can test PowerShell Remoting manually with:

    Test-WSMan $DeviceName
"@
}

Write-Host "$DeviceName is online." -ForegroundColor Green


# ============================================================================
# 2. CONNECT USING POWERSHELL REMOTING
# ============================================================================

Write-Step "Connecting to $DeviceName with PowerShell Remoting..."

try {

    $session = New-PSSession `
        -ComputerName $DeviceName
}
catch {

    throw @"
Could not establish a PowerShell Remoting session to $DeviceName.

On the remote PC, run PowerShell as Administrator:

    Enable-PSRemoting -Force

Then test from this computer:

    Test-WSMan $DeviceName

Original error:

$($_.Exception.Message)
"@
}


try {

    # ========================================================================
    # 3. LOCATE OLLAMA
    # ========================================================================

    Write-Step "Locating Ollama on $DeviceName..."

    $ollamaPath = Invoke-Command `
        -Session $session `
        -ScriptBlock {

            $candidates = @(
                "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
                "$env:ProgramFiles\Ollama\ollama.exe",
                "$env:ProgramFiles(x86)\Ollama\ollama.exe"
            )

            $command = Get-Command `
                ollama.exe `
                -ErrorAction SilentlyContinue

            if ($command) {
                $candidates += $command.Source
            }

            $found = $candidates |
                Where-Object {
                    $_ -and (Test-Path $_)
                } |
                Select-Object -First 1

            return $found
        }

    if (-not $ollamaPath) {

        throw @"
Ollama could not be found on $DeviceName.

Install Ollama on the remote PC first.
"@
    }

    Write-Host "Found Ollama at: $ollamaPath"


    # ========================================================================
    # 4. START OLLAMA
    # ========================================================================

    Write-Step "Starting Ollama with LAN access enabled..."

    Invoke-Command `
        -Session $session `
        -ArgumentList $ollamaPath `
        -ScriptBlock {

            param($OllamaPath)

            # Determine whether Ollama is already running.
            $running = $false

            try {

                Invoke-RestMethod `
                    -Uri "http://127.0.0.1:11434/api/tags" `
                    -TimeoutSec 2 `
                    -ErrorAction Stop | Out-Null

                $running = $true
            }
            catch {

                $running = $false
            }

            if (-not $running) {

                # Make Ollama listen on all network interfaces.
                $env:OLLAMA_HOST = "0.0.0.0:11434"

                Start-Process `
                    -FilePath $OllamaPath `
                    -ArgumentList "serve" `
                    -WindowStyle Hidden
            }
        }


    # ========================================================================
    # 5. WAIT FOR OLLAMA
    # ========================================================================

    Write-Step "Waiting for Ollama API..."

    $ollamaReady = $false

    $deadline = (Get-Date).AddSeconds(
        $OllamaTimeoutSeconds
    )

    do {

        Start-Sleep -Seconds 2

        try {

            Invoke-RestMethod `
                -Uri "http://$DeviceName`:$OllamaPort/api/tags" `
                -TimeoutSec 3 `
                -ErrorAction Stop | Out-Null

            $ollamaReady = $true
        }
        catch {

            $ollamaReady = $false
        }

    } while (
        -not $ollamaReady -and
        (Get-Date) -lt $deadline
    )

    if (-not $ollamaReady) {

        throw @"
Ollama did not become reachable at:

    http://${DeviceName}:${OllamaPort}

Possible causes:

  - Ollama failed to start.
  - Windows Firewall is blocking TCP 11434.
  - Ollama is listening only on localhost.
  - The remote PC has a network configuration problem.
"@
    }

    Write-Host "Ollama is reachable." -ForegroundColor Green


    # ========================================================================
    # 6. CHECK FOR MODEL
    # ========================================================================

    Write-Step "Checking for model '$Model'..."

    $modelExists = Invoke-Command `
        -Session $session `
        -ArgumentList $ollamaPath, $Model `
        -ScriptBlock {

            param(
                $OllamaPath,
                $Model
            )

            $models = & $OllamaPath list 2>$null

            if ($LASTEXITCODE -ne 0) {
                return $false
            }

            foreach ($line in $models) {

                if ($line -match "^\s*$([regex]::Escape($Model))\s+") {
                    return $true
                }
            }

            return $false
        }


    # ========================================================================
    # 7. DOWNLOAD MODEL IF NECESSARY
    # ========================================================================

    if (-not $modelExists) {

        Write-Step "Model is not installed. Pulling '$Model'..."

        Invoke-Command `
            -Session $session `
            -ArgumentList $ollamaPath, $Model `
            -ScriptBlock {

                param(
                    $OllamaPath,
                    $Model
                )

                & $OllamaPath pull $Model

                if ($LASTEXITCODE -ne 0) {

                    throw "Ollama failed to pull model '$Model'."
                }
            }

        Write-Host "Model downloaded." -ForegroundColor Green
    }
    else {

        Write-Host "Model already exists." -ForegroundColor Green
    }


    # ========================================================================
    # 8. OPEN OLLAMA FIREWALL PORT
    # ========================================================================

    Write-Step "Checking Windows Firewall..."

    Invoke-Command `
        -Session $session `
        -ArgumentList $OllamaPort `
        -ScriptBlock {

            param($Port)

            $ruleName = "Ollama LAN Access"

            $existing = Get-NetFirewallRule `
                -DisplayName $ruleName `
                -ErrorAction SilentlyContinue

            if (-not $existing) {

                New-NetFirewallRule `
                    -DisplayName $ruleName `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort $Port `
                    -Action Allow `
                    -Profile Private `
                    -ErrorAction Stop | Out-Null
            }
        }


    # ========================================================================
    # 9. LOAD MODEL
    # ========================================================================

    Write-Step "Loading '$Model' into Ollama..."

    Invoke-Command `
        -Session $session `
        -ArgumentList $Model `
        -ScriptBlock {

            param($Model)

            $body = @{
                model      = $Model
                prompt     = ""
                stream     = $false
                keep_alive = -1
            } | ConvertTo-Json

            Invoke-RestMethod `
                -Uri "http://127.0.0.1:11434/api/generate" `
                -Method Post `
                -ContentType "application/json" `
                -Body $body `
                -TimeoutSec 600 `
                -ErrorAction Stop | Out-Null
        }

    Write-Host "Model loaded." -ForegroundColor Green


    # ========================================================================
    # 10. VERIFY LAN ACCESS
    # ========================================================================

    Write-Step "Verifying LAN access to Ollama..."

    try {

        Invoke-RestMethod `
            -Uri "http://$DeviceName`:$OllamaPort/api/tags" `
            -TimeoutSec 5 `
            -ErrorAction Stop | Out-Null
    }
    catch {

        throw @"
Ollama is running on the remote PC, but it is not reachable from this PC.

Check:

  - Windows Firewall
  - Network profile
  - OLLAMA_HOST configuration
  - TCP port 11434
"@
    }

    Write-Host "LAN access verified." -ForegroundColor Green

}
finally {

    if ($session) {
        Remove-PSSession $session
    }
}


# ============================================================================
# 11. CONFIGURE CLAUDE CODE
# ============================================================================

Write-Step "Configuring Claude Code..."

$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_BASE_URL = "http://${DeviceName}:${OllamaPort}"

Write-Host ""
Write-Host "Claude Code configuration:" -ForegroundColor DarkGray
Write-Host "  ANTHROPIC_BASE_URL   = $env:ANTHROPIC_BASE_URL"
Write-Host "  ANTHROPIC_AUTH_TOKEN = ollama"
Write-Host "  Model                = $Model"
Write-Host ""


# ============================================================================
# 12. LAUNCH CLAUDE CODE
# ============================================================================

Write-Step "Launching Claude Code using '$Model'..."

$claude = Get-Command `
    claude.exe `
    -ErrorAction SilentlyContinue

if (-not $claude) {

    $claude = Get-Command `
        claude `
        -ErrorAction SilentlyContinue
}

if (-not $claude) {

    throw @"
Claude Code was not found on this PC.

Install Claude Code first, then run this script again.

Verify the installation with:

    claude --version
"@
}


# Environment variables are inherited by Claude Code.
#
# Claude Code:
#
#     runs on this computer
#
# and connects to:
#
#     http://<DeviceName>:11434
#
# while Ollama serves:
#
#     <Model>
#

& $claude.Source --model $Model
```
