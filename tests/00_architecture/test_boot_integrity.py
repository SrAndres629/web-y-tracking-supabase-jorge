"""
🚀 Architecture Test: Boot Integrity

Silicon Valley Pattern: System Bootstrap Validation

Este test asegura que la aplicación puede iniciar sin errores de importación
circulares o dependencias rotas. Es la primera línea de defensa contra
regresiones de arquitectura.
"""

import pytest
import sys
import os
import ast

# Ensure root path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)


def test_app_boot_integrity():
    """
    CRITICAL: Verifies that the FastAPI 'app' object can be imported 
    and initialized without any ImportError or circular dependencies.
    This would have caught the recent 'Request' and 'get_all_visitors' issues.
    """
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        # Create a test client to force initialization of routers/lifespan
        with TestClient(app) as client:
            # Probar endpoint de health
            response = client.get("/healthcheck")
            # Health endpoint debe existir (200) o estar documentado (404 por diseño)
            assert response.status_code in [200, 404], (
                f"Health endpoint returned unexpected status: {response.status_code}"
            )
            
    except ImportError as e:
        pytest.fail(f"🔥 BOOT FAILURE: Missing dependency or circular import: {e}")
    except Exception as e:
        pytest.fail(f"🔥 BOOT FAILURE: Unexpected error during startup: {e}")


def test_module_import_consistency():
    """
    Verifica que todos los módulos core sean importables.
    Este test detecta dependencias rotas o imports circulares.
    """
    # Core Layer (Innermost - No dependencies)
    core_modules = [
        "app.core.result",
        "app.core.decorators",
        "app.core.validators",
    ]
    
    # Domain Layer (Depends only on Core)
    domain_modules = [
        "app.domain.models.values",
        "app.domain.models.visitor",
        "app.domain.models.lead",
        "app.domain.models.events",
        "app.domain.repositories.visitor_repo",
        "app.domain.repositories.lead_repo",
        "app.domain.repositories.event_repo",
    ]
    
    # Application Layer (Depends on Domain and Core)
    application_modules = [
        "app.application.dto.tracking_dto",
        "app.application.dto.lead_dto",
        "app.application.dto.visitor_dto",
        "app.application.commands.track_event",
        "app.application.commands.create_lead",
        "app.application.commands.create_visitor",
        "app.application.queries.get_visitor",
        "app.application.queries.list_visitors",
    ]
    
    # Infrastructure Layer (Depends on all inner layers)
    infrastructure_modules = [
        "app.infrastructure.persistence.database",
        "app.infrastructure.persistence.visitor_repo",
        "app.infrastructure.persistence.event_repo",
        "app.infrastructure.cache.redis_cache",
        "app.infrastructure.cache.memory_cache",
    ]
    
    # Interface Layer (Outermost - Depends on all)
    interface_modules = [
        "app.interfaces.api.routes.pages",
        "app.interfaces.api.routes.tracking",
        "app.interfaces.api.routes.admin",
        "app.interfaces.api.routes.health",
        "app.interfaces.api.routes.identity",
        "app.interfaces.api.routes.seo",
    ]
    
    all_modules = (
        core_modules + 
        domain_modules + 
        application_modules + 
        infrastructure_modules + 
        interface_modules
    )
    
    failures = []
    
    for mod in all_modules:
        try:
            __import__(mod)
        except ImportError as e:
            failures.append(f"❌ {mod}: {e}")
        except Exception as e:
            failures.append(f"💥 {mod}: Unexpected error: {e}")
    
    if failures:
        pytest.fail(
            f"🔥 MODULE IMPORT FAILURES ({len(failures)}):\n" + 
            "\n".join(failures) +
            "\n\n💡 Check for circular imports or missing dependencies"
        )


def test_domain_layer_purity():
    """
    Verifica que la capa Domain no tenga dependencias externas.
    Clean Architecture Rule: Domain debe ser pura (sin imports de FastAPI, SQL, etc.)
    """
    from pathlib import Path
    
    domain_path = Path(PROJECT_ROOT) / "app" / "domain"
    violations = []
    
    # Patrones prohibidos en Domain
    prohibited_imports = [
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "psycopg2",
        "httpx",
        "requests",
    ]
    
    for py_file in domain_path.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        rel_path = py_file.relative_to(PROJECT_ROOT)
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                for prohibited in prohibited_imports:
                    if module_name == prohibited or module_name.startswith(f"{prohibited}."):
                        violations.append(
                            f"{rel_path}:{node.lineno} -> Domain importing '{module_name}'"
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    for prohibited in prohibited_imports:
                        if module_name == prohibited or module_name.startswith(f"{prohibited}."):
                            violations.append(
                                f"{rel_path}:{node.lineno} -> Domain importing '{module_name}'"
                            )
    
    assert not violations, (
        "🚨 DOMAIN LAYER POLLUTION:\n" +
        "\n".join(f"  - {v}" for v in violations) +
        "\n\n📖 Domain layer must be pure - no external framework dependencies allowed"
    )


def test_config_loading():
    """Verifica que la configuración carga correctamente"""
    try:
        from app.config import settings
        
        # Verificar que settings tiene atributos esperados
        required_attrs = [
            "DATABASE_URL",
            "META_PIXEL_ID", 
            "META_ACCESS_TOKEN",
            "HOST",
            "PORT",
        ]
        
        missing = [attr for attr in required_attrs if not hasattr(settings, attr)]
        
        assert not missing, (
            f"Missing required settings attributes: {missing}"
        )
        
    except Exception as e:
        pytest.fail(f"🔥 Config loading failed: {e}")
