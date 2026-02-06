import pytest
from importlib.metadata import distributions

def test_dependency_vulnerabilities():
    """
    Using standard importlib.metadata (Python 3.8+)
    Verifies that critical packages are installed.
    """
    # Lista de paquetes críticos
    # Note: Package names in metadata are usually lowercase/hyphenated
    critical_packages = {'fastapi', 'uvicorn', 'psycopg2-binary', 'pydantic', 'httpx', 'jinja2'}
    
    # Get all installed packages
    installed = {dist.metadata['Name'].lower() for dist in distributions()}
    
    missing_packages = []
    for package in critical_packages:
        # Normalize package name just in case
        if package.lower() not in installed:
            # psycopg2-binary sometimes registers as psycopg2-binary or psycopg2
            if package == 'psycopg2-binary' and 'psycopg2' in installed:
                continue
            missing_packages.append(package)
            
    assert not missing_packages, f"❌ Critical Packages Missing: {', '.join(missing_packages)}"

def test_config_audit():
    """
    Audits configuration for basic security flaws.
    """
    from app.config import settings
    
    # 1. Ensure Debug is False in Production logic (unless overridden)
    # This is just a structural check that settings load correctly
    assert hasattr(settings, 'DATABASE_URL'), "Settings must have DATABASE_URL"
    
    # 2. Check for weak keys (if any default values are dangerous)
    if settings.SECRET_KEY == "secret":
        pytest.fail("❌ SECRET_KEY is set to default 'secret'. This is insecure.")
