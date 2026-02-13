param(
    [string]$ServersFile = "scripts/codex_mcp_servers.json",
    [string]$PresetPromptFile = "scripts/codex_prompt_max.txt",
    [string]$Model = "",
    [switch]$SkipMcpSetup,
    [switch]$SafeMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[codex-max] $Message" -ForegroundColor Cyan
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "No se encontro '$Name' en PATH."
    }
}

function Add-McpServerFromConfig {
    param([pscustomobject]$Server)

    if (-not $Server.name) {
        throw "Cada servidor MCP debe tener 'name'."
    }
    if (-not $Server.type) {
        throw "Servidor MCP '$($Server.name)': falta 'type' (stdio/http)."
    }

    $name = [string]$Server.name
    $type = [string]$Server.type

    # Mantiene idempotencia: si existe, lo reemplaza.
    & codex mcp remove $name 2>$null | Out-Null

    if ($type -eq "http") {
        if (-not $Server.url) {
            throw "Servidor MCP '$name' (http): falta 'url'."
        }

        $args = @("mcp", "add", $name, "--url", [string]$Server.url)
        if ($Server.bearer_token_env_var) {
            $args += @("--bearer-token-env-var", [string]$Server.bearer_token_env_var)
        }

        Write-Info "Registrando MCP http '$name'..."
        & codex @args | Out-Host
        return
    }

    if ($type -ne "stdio") {
        throw "Servidor MCP '$name': type no valido '$type' (usa stdio/http)."
    }

    if (-not $Server.command) {
        throw "Servidor MCP '$name' (stdio): falta 'command'."
    }

    $args = @("mcp", "add", $name)
    if ($Server.env) {
        $envProps = $Server.env.PSObject.Properties
        foreach ($prop in $envProps) {
            $args += @("--env", "$($prop.Name)=$($prop.Value)")
        }
    }

    $args += "--"
    $args += [string]$Server.command
    if ($Server.args) {
        foreach ($item in $Server.args) {
            $args += [string]$item
        }
    }

    Write-Info "Registrando MCP stdio '$name'..."
    & codex @args | Out-Host
}

function Setup-McpServers {
    param([string]$ConfigPath)

    if (-not (Test-Path $ConfigPath)) {
        Write-Info "No existe $ConfigPath. Omitiendo registro MCP."
        return
    }

    $raw = Get-Content -Path $ConfigPath -Raw -Encoding UTF8
    $servers = $raw | ConvertFrom-Json
    if ($null -eq $servers) {
        Write-Info "Archivo MCP vacio. Omitiendo."
        return
    }

    if ($servers -isnot [System.Array]) {
        $servers = @($servers)
    }

    foreach ($server in $servers) {
        Add-McpServerFromConfig -Server $server
    }
}

Assert-Command -Name "codex"

$repoRoot = (Get-Location).Path

if (-not $SkipMcpSetup) {
    Setup-McpServers -ConfigPath $ServersFile
}

$defaultPrompt = @"
Modo MAX:
- Razona en profundidad antes de ejecutar cambios complejos.
- Prioriza soluciones robustas, testeables y alineadas a Clean Architecture/DDD.
- Usa las herramientas disponibles de shell/MCP cuando agreguen precision.
- Explica decisiones tecnicas de forma breve y accionable.
- Antes de terminar, valida cambios con pruebas o checks relevantes.
"@

$presetPrompt = $defaultPrompt
if (Test-Path $PresetPromptFile) {
    $presetPrompt = (Get-Content -Path $PresetPromptFile -Raw -Encoding UTF8).Trim()
    if (-not $presetPrompt) {
        $presetPrompt = $defaultPrompt
    }
}

$codexArgs = @("--cd", $repoRoot, "--search")
if ($Model) {
    $codexArgs += @("--model", $Model)
}

if ($SafeMode) {
    $codexArgs += @("--full-auto")
} else {
    $codexArgs += @("--dangerously-bypass-approvals-and-sandbox")
}

$codexArgs += $presetPrompt

Write-Info "Iniciando Codex CLI en modo maximo..."
& codex @codexArgs
