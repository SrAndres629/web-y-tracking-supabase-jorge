param(
    [string]$McpServersFile = "scripts/gemini_mcp_servers.json",
    [string]$Model = "",
    [switch]$SkipMcpSetup,
    [switch]$SafeMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[gemini-max] $Message" -ForegroundColor Green
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "No se encontro '$Name' en PATH. Por favor, asegúrate de que Gemini CLI esté instalado y en tu PATH."
    }
}

function Add-McpServerFromConfig {
    param([pscustomobject]$Server)

    if (-not $Server.name) {
        throw "Cada servidor MCP debe tener 'name'."
    }
    if (-not $Server.type) {
        throw "Servidor MCP '$($Server.name)': falta 'type' (stdio/http/sse)."
    }

    $name = [string]$Server.name
    $type = [string]$Server.type

    Write-Info "Eliminando MCP server '$name' para asegurar idempotencia..."
    & gemini mcp remove $name 2>$null | Out-Null

    $args = @("mcp", "add", $name, "--type", $type)

    if ($type -eq "http" -or $type -eq "sse") {
        if (-not $Server.url) {
            throw "Servidor MCP '$name' ($type): falta 'url'."
        }
        $args += @($Server.url) # commandOrUrl parameter
        if ($Server.bearer_token_env_var) {
            $args += @("-e", "$($Server.bearer_token_env_var)=$([System.Environment]::GetEnvironmentVariable($Server.bearer_token_env_var))")
        }
        if ($Server.headers) {
            foreach ($header in $Server.headers.PSObject.Properties) {
                $args += @("-H", "$($header.Name):$($header.Value)")
            }
        }
    } elseif ($type -eq "stdio") {
        if (-not $Server.command) {
            throw "Servidor MCP '$name' (stdio): falta 'command'."
        }
        $args += @($Server.command) # commandOrUrl parameter
        if ($Server.args) {
            foreach ($item in $Server.args) {
                $args += [string]$item
            }
        }
        if ($Server.env) {
            $envProps = $Server.env.PSObject.Properties
            foreach ($prop in $envProps) {
                $args += @("-e", "$($prop.Name)=$($prop.Value)")
            }
        }
    } else {
        throw "Servidor MCP '$name': type no valido '$type' (usa stdio/http/sse)."
    }
    
    # Always trust servers when in max mode
    $args += @("--trust")

    Write-Info "Registrando MCP $type '$name'..."
    & gemini @args | Out-Host
}

function Setup-McpServers {
    param([string]$ConfigPath)

    if (-not (Test-Path $ConfigPath)) {
        Write-Info "Advertencia: No existe el archivo de configuración MCP en '$ConfigPath'. Omitiendo registro MCP."
        return
    }

    $raw = Get-Content -Path $ConfigPath -Raw -Encoding UTF8
    $serversConfig = $raw | ConvertFrom-Json

    if ($null -eq $serversConfig -or $serversConfig.mcpServers -eq $null) {
        Write-Info "Archivo MCP vacio o formato incorrecto. Omitiendo."
        return
    }

    $mcpServers = $serversConfig.mcpServers.PSObject.Properties | ForEach-Object { $_.Value }

    foreach ($server in $mcpServers) {
        Add-McpServerFromConfig -Server $server
    }
}

Assert-Command -Name "gemini"

if (-not $SkipMcpSetup) {
    Setup-McpServers -ConfigPath $McpServersFile
}

$presetPrompt = "actua como un genio de sillicon valley pensando en la arquitectura actual y su escalonamiento avanzado usando herramientas contemporaneas pero super utiles."

$geminiArgs = @()

if ($Model) {
    $geminiArgs += @("-m", $Model)
}

# Auto-approve all actions for full automation
$geminiArgs += @("--approval-mode", "yolo")

# Pass the preset prompt
$geminiArgs += @("-p", $presetPrompt)

Write-Info "Iniciando Gemini CLI en modo maximo con prompt preestablecido..."
& gemini @geminiArgs
