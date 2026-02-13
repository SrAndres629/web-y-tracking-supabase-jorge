#Requires -Version 7.0
<#
.SYNOPSIS
    Kimi CLI - Modo Máximo Poder para Jorge Aguirre
    
.DESCRIPTION
    Script que inicializa Kimi CLI con:
    - Configuración MCP completa (10 servidores)
    - Modo YOLO (auto-aceptar todo)
    - Pensamiento profundo activado
    - Agente personalizado Max-Power
    - Prompts preestablecidos
    
.PARAMETER Prompt
    Ejecuta un prompt directo y sale (modo non-interactive)
    
.PARAMETER Continue
    Continúa la sesión anterior
    
.PARAMETER Model
    Especifica el modelo a usar (default: kimi-k2)
    
.PARAMETER NoYolo
    Desactiva el modo YOLO (pedirá confirmaciones)
    
.PARAMETER NoThinking
    Desactiva el pensamiento profundo
    
.PARAMETER Web
    Inicia el servidor Web UI en lugar de la consola
    
.PARAMETER Port
    Puerto para el servidor Web UI (default: 5494)
    
.PARAMETER Analyze
    Ejecuta análisis profundo del proyecto
    
.PARAMETER Refactor
    Ejecuta refactorización segura
    
.PARAMETER Debug
    Modo debugging avanzado
    
.PARAMETER Deploy
    Verifica preparación para deploy
    
.PARAMETER Seo
    Ejecuta optimización SEO
    
.PARAMETER Track
    Audita el sistema de tracking
    
.PARAMETER Help
    Muestra esta ayuda
    
.EXAMPLE
    .\kimi-max.ps1
    Inicia Kimi CLI en modo interactivo con máxima configuración
    
.EXAMPLE
    .\kimi-max.ps1 -Prompt "Analiza la arquitectura del proyecto"
    Ejecuta un comando y sale
    
.EXAMPLE
    .\kimi-max.ps1 -Analyze
    Ejecuta análisis profundo automático
    
.EXAMPLE
    .\kimi-max.ps1 -Web -Port 8080
    Inicia la interfaz web en el puerto 8080
#>

[CmdletBinding()]
param(
    [Parameter()][string]$Prompt,
    [Parameter()][switch]$Continue,
    [Parameter()][string]$Model = "kimi-k2",
    [Parameter()][switch]$NoYolo,
    [Parameter()][switch]$NoThinking,
    [Parameter()][switch]$Web,
    [Parameter()][int]$Port = 5494,
    [Parameter()][switch]$Analyze,
    [Parameter()][switch]$Refactor,
    [Parameter()][switch]$Debug,
    [Parameter()][switch]$Deploy,
    [Parameter()][switch]$Seo,
    [Parameter()][switch]$Track,
    [Parameter()][switch]$Help
)

# Mostrar banner
function Show-Banner {
    $banner = @"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔥 KIMI CLI - MODO MÁXIMO PODER 🔥                            ║
║                                                                  ║
║   Para: Jorge Aguirre - Web Tracking v3.0                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"@
    Write-Host $banner -ForegroundColor Cyan
}

# Mostrar ayuda
function Show-Help {
    Get-Help $PSCommandPath -Full
}

# Verificar dependencias
function Test-Dependencies {
    $deps = @{
        "kimi" = $false
        "npx" = $false
        "uvx" = $false
        "node" = $false
    }
    
    foreach ($dep in $deps.Keys) {
        $deps[$dep] = [bool](Get-Command $dep -ErrorAction SilentlyContinue)
    }
    
    Write-Host "`n📋 Verificando dependencias..." -ForegroundColor Yellow
    foreach ($dep in $deps.Keys) {
        $status = if ($deps[$dep]) { "✅" } else { "❌" }
        $color = if ($deps[$dep]) { "Green" } else { "Red" }
        Write-Host "   $status $dep" -ForegroundColor $color
    }
    
    return $deps["kimi"]
}

# Configurar variables de entorno MCP
function Set-MCPEnvironment {
    Write-Host "`n🔧 Configurando entorno MCP..." -ForegroundColor Yellow
    
    # Leer variables del .env
    $envFile = ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^([^#][^=]*)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim().Trim('"', "'")
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    
    # Asegurar que MCP esté habilitado
    $env:KIMI_MCP_ENABLED = "true"
    
    Write-Host "   ✅ Variables de entorno cargadas" -ForegroundColor Green
}

# Construir argumentos de Kimi
function Build-KimiArgs {
    $argsList = @()
    
    # Configuración base
    $argsList += "--config-file", ".kimi/config.toml"
    $argsList += "--agent-file", ".kimi/agent-max.toml"
    $argsList += "--model", $Model
    $argsList += "--mcp-config-file", ".kimi/mcp.json"
    
    # Modo YOLO (por defecto activado)
    if (-not $NoYolo) {
        $argsList += "--yolo"
    }
    
    # Pensamiento profundo (por defecto activado)
    if (-not $NoThinking) {
        $argsList += "--thinking"
    }
    
    # Continuar sesión
    if ($Continue) {
        $argsList += "--continue"
    }
    
    # Prompt predefinido
    if ($Analyze) {
        $Prompt = @"
Realiza un ANÁLISIS PROFUNDO COMPLETO del proyecto. Revisa:
1. Arquitectura Clean/DDD - cumplimiento y violaciones
2. Calidad del código - code smells, deuda técnica
3. Testing cobertura y calidad
4. Seguridad - vulnerabilidades potenciales
5. Performance - cuellos de botella
6. SEO - optimización técnica
7. Tracking - configuración Meta CAPI y RudderStack

Usa pensamiento secuencial. Genera un reporte detallado con prioridades.
"@
    }
    elseif ($Refactor) {
        $Prompt = @"
Realiza REFACTORIZACIÓN SEGURA del código:
1. Primero, ejecuta todos los tests y verifica que pasen
2. Identifica violaciones de Clean Architecture
3. Aplica refactors manteniendo TODO el comportamiento
4. Ejecuta tests después de cada cambio
5. Documenta todos los cambios realizados

NO cambies la lógica de negocio, solo la estructura.
"@
    }
    elseif ($Debug) {
        $Prompt = @"
MODO DEBUGGING AVANZADO:
1. Busca todos los TODO, FIXME, XXX en el código
2. Revisa logs de errores recientes en .kimi/logs/
3. Identifica bugs potenciales con análisis estático
4. Verifica manejo de errores en todas las rutas
5. Propone y aplica fixes

No pares hasta que todo esté limpio.
"@
    }
    elseif ($Deploy) {
        $Prompt = @"
VERIFICACIÓN PRE-DEPLOY:
1. Ejecuta TODO el test suite - deben pasar 100%
2. Verifica migraciones de base de datos
3. Revisa variables de entorno necesarias
4. Valida build de Vercel
5. Verifica integración Meta CAPI y RudderStack
6. Comprueba SEO y metadata
7. Lista de checklist para producción

Genera un reporte de deploy readiness.
"@
    }
    elseif ($Seo) {
        $Prompt = @"
OPTIMIZACIÓN SEO COMPLETA:
1. Analiza meta tags de todas las páginas
2. Verifica sitemap.xml y robots.txt
3. Revisa structured data (JSON-LD)
4. Optimiza Open Graph y Twitter Cards
5. Verifica Core Web Vitals
6. Revisa URLs y canonical tags
7. Implementa mejoras necesarias
"@
    }
    elseif ($Track) {
        $Prompt = @"
AUDITORÍA DE TRACKING:
1. Verifica configuración Meta CAPI (test_event, deduplicación)
2. Revisa integración RudderStack
3. Valida eventos personalizados
4. Comprueba identificación de usuarios
5. Verifica precisión de datos geográficos
6. Testea endpoints de tracking
7. Documenta el estado actual
"@
    }
    
    # Agregar prompt si existe
    if ($Prompt) {
        $argsList += "--prompt", $Prompt
    }
    
    return $argsList
}

# Función principal
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Show-Banner
    
    # Verificar dependencias
    if (-not (Test-Dependencies)) {
        Write-Host "`n❌ ERROR: kimi no está instalado" -ForegroundColor Red
        Write-Host "   Instala con: powershell -c `"irm https://moonshotai.github.io/kimi-cli/install.ps1 | iex`"" -ForegroundColor Yellow
        exit 1
    }
    
    # Configurar entorno
    Set-MCPEnvironment
    
    # Construir argumentos
    $kimiArgs = Build-KimiArgs
    
    # Ejecutar Kimi
    Write-Host "`n🚀 Iniciando Kimi CLI con configuración MÁXIMA..." -ForegroundColor Green
    Write-Host "   Modelo: $Model" -ForegroundColor Gray
    Write-Host "   YOLO: $(if (-not $NoYolo) { 'ON' } else { 'OFF' })" -ForegroundColor Gray
    Write-Host "   Thinking: $(if (-not $NoThinking) { 'ON' } else { 'OFF' })" -ForegroundColor Gray
    Write-Host "   MCP: $(if (Test-Path ".kimi/mcp.json") { 'ON' } else { 'OFF' })" -ForegroundColor Gray
    Write-Host ""
    
    if ($Web) {
        Write-Host "🌐 Iniciando servidor Web UI en puerto $Port..." -ForegroundColor Cyan
        & kimi web --port $Port @kimiArgs
    }
    else {
        & kimi @kimiArgs
    }
}

# Ejecutar
Main
