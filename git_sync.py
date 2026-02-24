#!/usr/bin/env python3
"""
🚀 SILICON VALLEY DEPLOYMENT & AUDIT PROTOCOL
==============================================
Herramienta integral para:
- Auditoría de seguridad y tests
- Caza de bugs automatizada
- Detección de archivos relacionados
- Despliegue con verificaciones

Uso:
    python git_sync.py                    # Ejecutar auditoría completa
    python git_sync.py --security         # Solo auditoría de seguridad
    python git_sync.py --bug-hunt         # Solo caza de bugs
    python git_sync.py --find-related     # Encontrar archivos relacionados
    python git_sync.py "commit message"   # Desplegar con mensaje
    python git_sync.py --force            # Forzar despliegue (¡peligro!)
"""

import argparse
import datetime
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.request
from typing import Any, ClassVar, Dict, List, Tuple

try:
    import requests  # type: ignore
except ImportError:
    # Fallback for type checking
    requests = Any  # type: ignore

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    # Fallback for type checking
    def load_dotenv(*args: Any, **kwargs: Any) -> bool:
        return True


# =================================================================
# CONFIGURATION
# =================================================================
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")

VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_TEAM_ID = os.getenv("VERCEL_TEAM_ID", "team_VrT30Jn8hOQ8OBW89aErcCkZ")
VERCEL_PROJECT_ID = os.getenv("VERCEL_PROJECT_ID", "prj_W6Q6T34VawNikJ0JCVFsXm9qj9aN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID", "eycumxvxyqzznjkwaumx")

REPO_PATH = os.path.dirname(os.path.abspath(__file__))


# =================================================================
# CONSOLE OUTPUT
# =================================================================
class Console:
    HEADER: str = "\033[95m"
    BLUE: str = "\033[94m"
    CYAN: str = "\033[96m"
    GREEN: str = "\033[92m"
    WARNING: str = "\033[93m"
    FAIL: str = "\033[91m"
    ENDC: str = "\033[0m"
    BOLD: str = "\033[1m"

    @staticmethod
    def write(text: Any) -> None:
        """Prints text to stdout with encoding safety."""
        try:
            print(text)
        except (UnicodeEncodeError, AttributeError):
            enc = sys.stdout.encoding or "utf-8"
            if hasattr(sys.stdout, "buffer") and sys.stdout.buffer:
                sys.stdout.buffer.write(
                    (str(text) + "\n").encode(enc, errors="replace")
                )
                sys.stdout.flush()
            else:
                print(
                    str(text)
                    .encode(enc, errors="replace")
                    .decode(enc, errors="replace")
                )

    @staticmethod
    def log(msg: Any, symbol: str = "*") -> None:
        Console.write(f"{symbol} {msg}")

    @staticmethod
    def success(msg: Any) -> None:
        Console.write(f"{Console.GREEN}[OK] {msg}{Console.ENDC}")

    @staticmethod
    def error(msg: Any) -> None:
        Console.write(f"{Console.FAIL}[ERROR] {msg}{Console.ENDC}")

    @staticmethod
    def info(msg: Any) -> None:
        Console.write(f"{Console.CYAN}[INFO] {msg}{Console.ENDC}")

    @staticmethod
    def warning(msg: Any) -> None:
        Console.write(f"{Console.WARNING}[WARN] {msg}{Console.ENDC}")

    @staticmethod
    def section(title: Any) -> None:
        Console.write(f"\n{Console.BOLD}{'=' * 60}{Console.ENDC}")
        Console.write(f"{Console.BOLD}{title}{Console.ENDC}")
        Console.write(f"\n{Console.BOLD}{'=' * 60}{Console.ENDC}")


# =================================================================
# SECURITY AUDITOR
# =================================================================
class SecurityAuditor:
    """Audits security headers and configurations."""

    REQUIRED_HEADERS: ClassVar[Dict[str, str]] = {
        "Strict-Transport-Security": "HSTS",
        "X-Frame-Options": "Clickjacking Protection",
        "X-Content-Type-Options": "MIME Sniffing Protection",
        "Referrer-Policy": "Referrer Privacy",
        "X-XSS-Protection": "XSS Protection",
        "Cross-Origin-Opener-Policy": "COOP",
        "Cross-Origin-Resource-Policy": "CORP",
        "Content-Security-Policy": "CSP",
    }

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def audit_middleware(self) -> bool:
        """Verifica que el middleware de seguridad tenga todos los headers"""
        Console.section("🔒 SECURITY MIDDLEWARE AUDIT")

        middleware_path = os.path.join(
            self.repo_path, "app", "middleware", "security.py"
        )
        if not os.path.exists(middleware_path):
            self.issues.append("Security middleware not found!")
            return False

        with open(middleware_path, "r") as f:
            content = f.read()

        missing_headers = []
        for header, description in self.REQUIRED_HEADERS.items():
            if header not in content:
                missing_headers.append(f"  - {header} ({description})")

        if missing_headers:
            headers_str = "\n".join(missing_headers)
            self.issues.append(str(f"Missing security headers:\n{headers_str}"))  # type: ignore
            Console.error("Security headers missing!")
            for issue in missing_headers:
                Console.write(f"  {issue}")
            return False

        # Verificar CSP en modo estricto (no report-only)
        if "Content-Security-Policy-Report-Only" in content:
            self.warnings.append(
                "CSP is in Report-Only mode. Consider using strict mode."
            )
            Console.warning("CSP in Report-Only mode")

        if "Content-Security-Policy" in content:
            Console.success("CSP strict mode detected")

        # Verificar HSTS con preload
        if "preload" in content and "includeSubDomains" in content:
            Console.success("HSTS with preload configured")
        else:
            self.warnings.append("HSTS missing preload or includeSubDomains")
            Console.warning("HSTS configuration incomplete")

        Console.success("Security middleware audit passed")
        return True

    def audit_seo_files(self) -> bool:
        """Verifica que existan robots.txt y sitemap.xml"""
        Console.section("🔍 SEO FILES AUDIT")

        routes_path = os.path.join(
            self.repo_path, "app", "interfaces", "api", "routes", "seo.py"
        )
        if not os.path.exists(routes_path):
            self.issues.append("SEO routes not found!")
            return False

        with open(routes_path, "r") as f:
            content = f.read()

        checks = {
            "/robots.txt": "robots.txt route",
            "/sitemap.xml": "sitemap.xml route",
            "User-agent": "robots.txt content",
            "urlset": "sitemap.xml content",
        }

        all_good = True
        for check, desc in checks.items():
            if check in content:
                Console.success(f"{desc}: OK")
            else:
                self.issues.append(f"Missing: {desc}")
                Console.error(f"{desc}: MISSING")
                all_good = False

        return all_good

    def audit_meta_tags(self) -> bool:
        """Verifica meta tags en templates"""
        Console.section("🏷️  META TAGS AUDIT")

        base_template = os.path.join(
            self.repo_path, "api", "templates", "layouts", "base.html"
        )
        if not os.path.exists(base_template):
            self.issues.append("Base template not found!")
            return False

        with open(base_template, "r") as f:
            content = f.read()

        required_meta = {
            'name="description"': "Meta description",
            'name="robots"': "Meta robots",
            'rel="canonical"': "Canonical URL",
            'property="og:title"': "Open Graph title",
            'property="og:description"': "Open Graph description",
            'name="twitter:card"': "Twitter Card",
        }

        all_good = True
        for tag, desc in required_meta.items():
            if tag in content:
                Console.success(f"{desc}: OK")
            else:
                self.warnings.append(f"Missing meta tag: {desc}")
                Console.warning(f"{desc}: MISSING")
                all_good = False

        return all_good

    def run_full_audit(self) -> bool:
        """Ejecuta auditoría completa de seguridad"""
        Console.section("🛡️  FULL SECURITY AUDIT")

        results = [
            self.audit_middleware(),
            self.audit_seo_files(),
            self.audit_meta_tags(),
        ]

        if self.issues:
            Console.section("❌ SECURITY ISSUES FOUND")
            for issue in self.issues:
                Console.error(issue)

        if self.warnings:
            Console.section("⚠️  SECURITY WARNINGS")
            for warning in self.warnings:
                Console.warning(warning)

        if all(results) and not self.issues:
            Console.section("✅ SECURITY AUDIT PASSED")
            return True

        return False


# =================================================================
# BUG HUNTER
# =================================================================
class BugHunter:
    """Automated bug hunter - OPTIMIZED VERSION"""

    # Patterns for modern CI/CD standards
    PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "Security Issues": [
            (r"(?<!_)eval\s*\(", "Dangerous eval() usage"),
            (r"(?<!_)exec\s*\(", "Dangerous exec() usage"),
        ],
        "Debug Code": [
            (r"^\s*print\s*\(", "Raw print() detected (use logging instead)"),
            (
                r"(?<!Logger\.)(?<!console\.)console\.log\(",
                "Raw console.log() detected (use Logger.debug instead)",
            ),
        ],
    }

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.findings: List[Dict[str, Any]] = []

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scans a file for patterns - OPTIMIZED"""
        findings: List[Dict[str, Any]] = []

        try:
            # Skip large files (>500KB)
            file_size = os.path.getsize(file_path)
            if file_size > 500_000:
                return findings

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines: List[str] = f.readlines()
        except OSError:
            return findings

        # Pre-compile patterns for efficiency
        compiled_patterns = []
        for category, patterns in self.PATTERNS.items():
            for pattern, description in patterns:
                try:
                    compiled_patterns.append(
                        (re.compile(pattern, re.IGNORECASE), category, description)
                    )
                except re.error:
                    continue

        # Scan line by line with compiled patterns
        for line_num, line in enumerate(lines, 1):
            # Skip comment lines quickly
            stripped = line.strip()
            if (
                not stripped
                or stripped[0] in "#*-"
                or stripped[:2] in ("//", "--", "/*", "* ")
            ):
                continue

            for compiled_re, category, description in compiled_patterns:
                if compiled_re.search(line):
                    findings.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "category": category,
                            "description": description,
                            "code": line.strip()[:80],
                        }
                    )
                    break  # One finding per line is enough

        return findings

    def hunt(self) -> List[Dict[str, Any]]:
        """Scans the repository for potential issues - OPTIMIZED WITH TIMEOUT"""
        import time

        start_time: float = time.time()
        max_duration: int = 30  # Max 30 seconds

        Console.section("🐛 BUG HUNT INITIATED (Max 30s)")

        extensions: set[str] = {".py", ".js", ".html", ".css", ".sql"}
        exclude_dirs: set[str] = {
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "dist",
            ".venv",
            ".ai",
            "refactor_backup",
            "tests",
            "scripts",
            "tools",
        }
        exclude_files: set[str] = {
            "git_sync.py",
            "antigravity.py",
            "synapse.py",
            "setup_env.py",
            "logger.js",
        }

        files_scanned: int = 0

        for root, dirs, files in os.walk(self.repo_path):
            # Check timeout
            if time.time() - start_time > max_duration:
                Console.warning("Bug hunt timeout reached (30s). Stopping scan.")
                break

            filtered_dirs = [d for d in dirs if d not in exclude_dirs]
            dirs.clear()
            dirs.extend(filtered_dirs)

            for file in files:
                # Check timeout per file
                if time.time() - start_time > max_duration:
                    break

                # Skip infrastructure/logger files
                if file in exclude_files:
                    continue

                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    findings = self.scan_file(file_path)
                    self.findings.extend(findings)
                    files_scanned += 1  # type: ignore

                    # Show progress every 50 files
                    if files_scanned % 50 == 0:
                        elapsed = time.time() - start_time
                        Console.log(
                            f"Scanned {files_scanned} files... ({elapsed:.1f}s)"
                        )

        elapsed = time.time() - start_time
        Console.log(f"Scan complete: {files_scanned} files scanned in {elapsed:.1f}s")

        # Group by category
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for finding in self.findings:
            cat = str(finding["category"])
            by_category.setdefault(cat, []).append(finding)

        # Show results
        if not self.findings:
            Console.success("No critical bugs found! Code is clean.")
            return []

        Console.warning(f"Found {len(self.findings)} potential issues:")

        for category, cat_findings in by_category.items():
            Console.write(f"\n{Console.BOLD}{category}:{Console.ENDC}")
            # Ensure it is a concrete list for slicing
            display_list: List[Dict[str, Any]] = list(cat_findings)
            for i in range(min(3, len(display_list))):
                finding = display_list[i]
                rel_path = os.path.relpath(str(finding["file"]), self.repo_path)
                Console.write(
                    f"  {Console.WARNING}{rel_path}:{finding['line']}{Console.ENDC}"
                )
                Console.write(f"    {finding['description']}")
            if len(cat_findings) > 3:
                Console.write(f"  ... and {len(cat_findings) - 3} more")

        return self.findings


# =================================================================
# RELATED FILES FINDER
# =================================================================
class RelatedFilesFinder:
    """Finds related files based on name, imports, and templates."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def find_related(self, target_file: str) -> List[Tuple[str, str]]:
        """Finds files related to the target file."""
        Console.section(f"🔍 FINDING FILES RELATED TO: {target_file}")

        if not os.path.exists(target_file):
            Console.error(f"File not found: {target_file}")
            return []

        # Get base name without extension
        base_name = os.path.splitext(os.path.basename(target_file))[0]

        related: List[Tuple[str, str]] = []

        # Search for files with same name but different extension
        target_dir = os.path.dirname(target_file)
        if os.path.isdir(target_dir):
            for file in os.listdir(target_dir):
                file_base = os.path.splitext(file)[0]
                full_item_path = os.path.join(target_dir, file)
                if file_base == base_name and full_item_path != target_file:
                    related.append((full_item_path, "Same name, different extension"))

        # Search for imports/references
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return related

        # Search for Python imports
        python_imports = re.findall(
            r"from\s+([\w.]+)\s+import|import\s+([\w.]+)", content
        )
        for match in python_imports:
            module = str(match[0] or match[1])
            module_path = module.replace(".", "/") + ".py"
            full_path = os.path.join(self.repo_path, module_path)
            if os.path.exists(full_path):
                related.append((full_path, f"Python import: {module}"))

        # Search for JS imports
        js_imports = re.findall(
            r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]|"
            r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            content,
        )
        for match in js_imports:
            module = str(match[0] or match[1])
            if module.startswith("."):
                # Relative import
                dir_path = os.path.dirname(target_file)
                resolved = os.path.normpath(os.path.join(dir_path, module))
                if os.path.exists(resolved):
                    related.append((resolved, f"JS import: {module}"))
                elif os.path.exists(resolved + ".js"):
                    related.append((resolved + ".js", f"JS import: {module}"))

        # Search for related templates
        if "routes" in target_file or "views" in target_file:
            template_patterns = re.findall(r"['\"]([\w/]+\.html)['\"]", content)
            for template in template_patterns:
                template_path = os.path.join(
                    self.repo_path, "api", "templates", str(template)
                )
                if os.path.exists(template_path):
                    related.append((template_path, f"Template: {template}"))

        # Show results
        if related:
            Console.success(f"Found {len(related)} related files:")
            for item_path, reason in related:
                rel_path = os.path.relpath(item_path, self.repo_path)
                Console.write(f"  {Console.CYAN}{rel_path}{Console.ENDC}")
                Console.write(f"    Reason: {reason}")
        else:
            Console.info("No related files found")

        return related

    def find_by_pattern(self, pattern: str) -> List[str]:
        """Finds files by name pattern."""
        Console.section(f"🔍 FINDING FILES MATCHING: {pattern}")

        matches: List[str] = []
        exclude_dirs: set[str] = {
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
        }

        for root, dirs, files in os.walk(self.repo_path):
            filtered_dirs = [d for d in dirs if d not in exclude_dirs]
            dirs.clear()
            dirs.extend(filtered_dirs)

            for file in files:
                if pattern.lower() in file.lower():
                    matches.append(os.path.join(root, file))

        if matches:
            Console.success(f"Found {len(matches)} matches:")
            for match in matches:
                Console.write(f"  {os.path.relpath(match, self.repo_path)}")
        else:
            Console.info("No matches found")

        return matches


# =================================================================
# SYSTEM AUDITOR (Original)
# =================================================================
class SystemAuditor:
    """System and test auditor."""

    def __init__(self, repo_path: str):
        self.repo_path: str = repo_path
        self.issues: List[Dict[str, str]] = []
        self.raw_logs: List[str] = []
        self.suggestions: List[str] = []

    def check_assets(self) -> bool:
        """Run the Asset Integrity Audit via Pytest."""
        Console.log("Verifying Asset Integrity (Build System)...", "🎨")

        test_path: str = "tests/L5_system/test_assets_integrity.py"
        cmd: List[str] = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_path, check=False
            )

            if result.returncode == 0:
                Console.success("Assets Verified: Build config and CSS are valid.")
                return True
            else:
                self._add_issue(
                    file_path="ASSETS",
                    line="N/A",
                    err_type="BuildIntegrityError",
                    message="Critical assets or config missing.",
                    phase="Asset Audit",
                )
                Console.error("Asset Audit Failed.")
                print(result.stdout)
                return False
        except OSError as e:
            self._add_issue(
                file_path="ASSETS",
                line="N/A",
                err_type="Exception",
                message=str(e),
                phase="Asset Audit",
            )
            Console.error(f"Asset Audit Crashed: {e}")
            return False

    def check_environment(self) -> bool:
        Console.log("Verifying Execution Environment...", "🔍")
        required_modules: List[str] = ["pytest", "hypothesis", "httpx"]
        missing: List[str] = []
        for mod in required_modules:
            try:
                import importlib

                importlib.import_module(mod)
            except ImportError:
                missing.append(mod)

        if missing:
            self._add_issue(
                file_path="ENVIRONMENT",
                line="N/A",
                err_type="Missing Critical Dev Dependencies",
                message=f"Modules not found: {', '.join(missing)}",
                phase="Environment",
            )
            Console.error(f"Missing modules: {missing}")
            return False

        Console.success("Environment Integrity Verified.")
        return True

    def run_phase(self, name, path, audit_mode=True, retries=1):
        Console.log(f"Running Integrity: {name}...", "-")

        env = os.environ.copy()
        if audit_mode:
            env["AUDIT_MODE"] = "1"

        test_paths = shlex.split(path) if isinstance(path, str) else list(path)
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            *test_paths,
            "-v",
            "--tb=short",
            "--maxfail=0",
        ]

        last_combined = ""
        for attempt in range(1, retries + 2):
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                env=env,
                check=False,
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            combined = stdout + "\n" + stderr
            last_combined = combined

            if result.returncode == 0:
                self.raw_logs.append(combined)
                Console.success(f"Phase passed: {name}")
                return

            Console.warning(f"Phase {name} attempt {attempt} failed.")
            if attempt <= retries:
                time.sleep(2)
                continue

        self.raw_logs.append(last_combined)
        Console.error(f"Phase failed: {name}")
        issues = self._extract_issues(last_combined, phase=name)
        if not issues:
            self._add_issue(
                file_path="UNKNOWN",
                line="N/A",
                err_type="Exception",
                message="Unknown failure. Check logs.",
                phase=name,
            )

    def _add_issue(self, file_path, line, err_type, message, phase):
        self.issues.append(
            {
                "file": file_path,
                "line": str(line),
                "type": err_type,
                "message": message.strip(),
                "phase": phase,
            }
        )

    def _extract_issues(self, output, phase):
        issues_added = 0
        for line in output.splitlines():
            fail_match = re.match(r"^FAILED\s+(.+?)\s+-\s+(.*)$", line)
            if fail_match:
                self._add_issue(
                    file_path=fail_match.group(1),
                    line="N/A",
                    err_type="TestFailure",
                    message=fail_match.group(2),
                    phase=phase,
                )
                issues_added += 1
        return issues_added

    def report(self):
        Console.log("========== FORENSIC DIAGNOSTIC REPORT ==========", "=")
        if not self.issues:
            Console.success("Score de Salud: 100% (Zero Defects Detected)")
            return True

        Console.error(f"Score de Salud: < 100% ({len(self.issues)} errores)")
        for issue in self.issues:
            Console.write(
                f"- {issue['file']}:{issue['line']} [{issue['type']}] {issue['message']}"
            )

        return False


# =================================================================
# INFRASTRUCTURE AUDITOR (Original)
# =================================================================
class InfrastructureAuditor:
    """Audits the health of external infrastructure (Vercel, Supabase)."""

    def __init__(self):
        # API Tokens from environment
        self.vercel_token: str = os.getenv("VERCEL_TOKEN", "")
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_key: str = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or ""
        )

    def check_vercel_health(self) -> bool:
        """Verifies Vercel deployment status."""
        if not self.vercel_token:
            Console.info("Vercel token not configured. Skipping health check.")
            return True

        project_id: str = os.getenv("VERCEL_PROJECT_ID", "")
        if not project_id:
            Console.warning("VERCEL_PROJECT_ID not set. Skipping health check.")
            return True

        Console.log("Verifying Vercel Infrastructure Health...", "⚡")
        try:
            headers: Dict[str, str] = {"Authorization": f"Bearer {self.vercel_token}"}
            url = (
                f"https://api.vercel.com/v6/deployments?projectId={project_id}&limit=1"
            )

            # Using Any for requests to bypass type checking issues if necessary
            req_any: Any = requests
            resp = req_any.get(url, headers=headers, timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                deployments = data.get("deployments", [])
                if deployments:
                    state = deployments[0].get("state")
                    if state == "READY":
                        Console.success("Vercel Deployment is Healthy and READY.")
                        return True
                    else:
                        Console.warning(f"Vercel Deployment Status: {state}")
                return True
            else:
                Console.warning(f"Vercel Health Check Failed: Status {resp.status_code}")
                return False
        except Exception as e:
            Console.warning(f"Vercel health check failed (Network/Timeout): {e}")
            return False

        return False

    def check_supabase_health(self) -> bool:
        """Verifies Supabase connection."""
        if not self.supabase_url or not self.supabase_key:
            Console.info("Supabase credentials not configured. Skipping health check.")
            return True

        Console.log("Verifying Supabase Backend Health...", "🔥")
        try:
            url = f"{self.supabase_url}/rest/v1/"
            headers: Dict[str, str] = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
            }
            req_any: Any = requests
            # Reduced timeout and added better error handling
            resp = req_any.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                Console.success("Supabase Backend is responsive.")
                return True
            else:
                Console.warning(f"Supabase Health Check Status: {resp.status_code}")
                return False
        except Exception as e:
            Console.warning(f"Supabase health check failed (Network/Timeout): {e}")

        return False


# =================================================================
# UTILITY FUNCTIONS (Original)
# =================================================================
def purge_cloudflare_cache() -> None:
    """Purges Cloudflare cache using API."""
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")

    if not zone_id or not api_token:
        Console.info("Cloudflare credentials not found. Skipping cache purge.")
        return

    try:
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"purge_everything": True})
        req = urllib.request.Request(
            url, data=data.encode("utf-8"), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                Console.success("Cloudflare Edge Cache Purged.")
            else:
                Console.warning(f"Cloudflare purge failed: {response.status}")
    except Exception as e:
        Console.warning(f"Cloudflare purge failed: {e}")


def run_cmd(
    command: str, cwd: str | None = None, exit_on_fail: bool = False
) -> Tuple[bool, str, str]:
    """Runs a shell command and returns success, stdout, stderr."""
    cmd_args = shlex.split(command)
    if not cmd_args:
        return False, "", "Empty command"

    try:
        result = subprocess.run(
            cmd_args, shell=False, capture_output=True, text=True, cwd=cwd, check=False
        )
    except FileNotFoundError:
        # Command not found
        return False, "", f"Command not found: {command}"

    if result.returncode != 0:
        if exit_on_fail:
            Console.error(f"Command failed: {command}\n{result.stderr.strip()}")
            sys.exit(1)
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr


# =================================================================
# MAIN DEPLOYMENT PIPELINE
# =================================================================
def _run_audit_gates(auditor: SystemAuditor, force: bool) -> bool:
    env_ok = auditor.check_environment()

    integrity_phases = [
        {"name": "L1: Atomic Logic", "path": "tests/L1_atoms"},
        {"name": "L2: Component Logic", "path": "tests/L2_components"},
        {"name": "L3: Module Integrations", "path": "tests/L3_modules"},
        {
            "name": "L4: Supervisor/Integration",
            "path": "tests/L4_supervisor tests/L4_integration",
        },
        {"name": "L5: System Reality", "path": "tests/L5_system"},
        {"name": "Frontend & Platform", "path": "tests/frontend tests/platform"},
        {
            "name": "Root & Misc",
            "path": "tests/test_tracking_integration.py tests/anti_crash_test.py",
        },
    ]

    if not auditor.check_assets():
        if not force:
            Console.error("Deployment blocked: Asset Audit Failed.")
            return False
        else:
            Console.warning("⚠️ Forcing deployment despite failed Asset Audit.")

    if force:
        Console.warning("⚠️ SKIPPING GATES: --force flag detected.")
        return True

    infra = InfrastructureAuditor()
    infra.check_vercel_health()
    infra.check_supabase_health()

    if not env_ok:
        for phase in integrity_phases:
            auditor._add_issue(
                file_path=phase["path"],
                line="N/A",
                err_type="Exception",
                message="Skipped due to missing dependencies.",
                phase=phase["name"],
            )
    else:
        for phase in integrity_phases:
            auditor.run_phase(phase["name"], phase["path"], audit_mode=True)

    healthy = auditor.report()

    if not healthy:
        Console.error("Deployment blocked due to LOCAL TEST FAILURES.")
        return False

    return True


def _stage_and_commit(message: str | None, force: bool) -> bool:
    Console.log("[2/6] Staging & Committing...", "+")
    run_cmd("git add .", cwd=REPO_PATH)

    _success, output, _ = run_cmd("git status --porcelain", cwd=REPO_PATH)
    has_changes = bool(output.strip())

    if has_changes or force:
        time_str = datetime.datetime.now().strftime("%H:%M")
        msg = message if message else f"chore: system sync {time_str}"

        if not has_changes and force:
            msg += " (FORCED)"
            run_cmd(f'git commit --allow-empty -m "{msg}"', cwd=REPO_PATH)
        elif has_changes:
            Console.log(f"Committing source: '{msg}'", "📝")
            run_cmd(f'git commit -m "{msg}"', cwd=REPO_PATH)
        return True
    else:
        Console.info("No local changes to commit.")
        return True


def _sync_with_origin() -> bool:
    Console.log("[3/6] Synchronizing with Origin...", ">")
    run_cmd("git fetch origin", cwd=REPO_PATH)

    Console.log("[4/6] Rebase Integration...", "~")
    success, _, _ = run_cmd("git pull origin main --rebase", cwd=REPO_PATH)
    if not success:
        Console.error("CRITICAL: Rebase Conflict. Resolve manually.")
        return False

    _, local_sha, _ = run_cmd("git rev-parse HEAD", cwd=REPO_PATH)
    _, remote_sha, _ = run_cmd("git rev-parse origin/main", cwd=REPO_PATH)

    if local_sha.strip() == remote_sha.strip():
        Console.success("SYSTEM SYNCED. No Ops Required.")
        return True

    Console.log("Local is ahead. Proceeding to Push...", "⬆️")
    Console.log("[6/6] Injecting into Production...", "!")
    success, _, stderr = run_cmd("git push -u origin main", cwd=REPO_PATH)

    if not success:
        Console.error(f"Push Failed: {stderr}")
        return False

    Console.success("✅ DEPLOYMENT SUCCESSFUL")
    return True


def _post_deploy_verify() -> None:
    Console.log("Validating Edge Cache Purge...", "🧹")
    purge_cloudflare_cache()

    try:
        url = "https://jorgeaguirreflores.com"
        Console.log(f"🔥 Pre-Warming Global Edge: {url}", "🔥")
        time.sleep(10)

        req_any: Any = requests
        resp = req_any.get(url, timeout=15)
        if resp.status_code == 200:
            version_match = re.search(r"\?v=(\d+)", str(resp.text))
            new_version = version_match.group(1) if version_match else "Unknown"
            Console.success(
                f"PRODUCCIÓN ACTUALIZADA: Versión Atómica {new_version} activa."
            )
        else:
            Console.warning(f"Pre-Warm status: {resp.status_code}")
    except Exception as e:
        Console.warning(f"Pre-Warm failed: {e}")

    print(
        f"\n{Console.GREEN}System is Live: https://jorgeaguirreflores.com{Console.ENDC}"
    )


# =================================================================
# MAIN ENTRY POINT
# =================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Silicon Valley Deployment & Audit Tool"
    )
    parser.add_argument(
        "--force", action="store_true", help="⚠️ DANGER: Bypass all checks"
    )
    parser.add_argument(
        "--security", action="store_true", help="🔒 Run security audit only"
    )
    parser.add_argument("--bug-hunt", action="store_true", help="🐛 Run bug hunt only")
    parser.add_argument(
        "--find-related", metavar="FILE", help="🔍 Find files related to FILE"
    )
    parser.add_argument(
        "--pattern", metavar="PATTERN", help="🔍 Find files matching pattern"
    )
    parser.add_argument("message", nargs="?", default=None, help="Commit message")
    parser.add_argument(
        "--yes-to-deploy",
        action="store_true",
        help="Bypass confirmation for deployment after bug hunt",
    )
    parser.add_argument(
        "--self-heal",
        action="store_true",
        help="💊 Run Auto-Fixer protocol before audit",
    )
    args: Any = parser.parse_args()

    # Modo: Self-Healing
    if args.self_heal:
        print(f"\n{Console.BOLD}💊 INITIATING SELF-HEALING PROTOCOL...{Console.ENDC}")
        auto_fix_path = os.path.join(REPO_PATH, "tools", "auto_fix.py")
        if os.path.exists(auto_fix_path):
            subprocess.run([sys.executable, auto_fix_path], check=False)
        else:
            Console.error("Auto-fix tool not found!")

    # Modo: Find Related Files
    if args.find_related:
        finder = RelatedFilesFinder(REPO_PATH)
        finder.find_related(args.find_related)
        return

    # Modo: Find by Pattern
    if args.pattern:
        finder = RelatedFilesFinder(REPO_PATH)
        finder.find_by_pattern(args.pattern)
        return

    # Modo: Bug Hunt
    if args.bug_hunt:
        hunter = BugHunter(REPO_PATH)
        hunter.hunt()
        return

    # Modo: Security Audit
    if args.security:
        security = SecurityAuditor(REPO_PATH)
        passed = security.run_full_audit()
        sys.exit(0 if passed else 1)

    # Modo: Full Deployment Pipeline
    print(
        f"\n{Console.BOLD}[NEURAL-SYNC] Initializing Silicon Valley Protocol...{Console.ENDC}\n"
    )

    # Ejecutar auditoría de seguridad primero
    security = SecurityAuditor(REPO_PATH)
    if not args.force and not security.run_full_audit():
        Console.error("Security audit failed. Fix issues before deploying.")
        Console.info("Run: python git_sync.py --security")
        sys.exit(1)

    # Ejecutar caza de bugs
    hunter = BugHunter(REPO_PATH)
    findings = hunter.hunt()
    if findings and not args.force and not args.yes_to_deploy:
        Console.warning(f"Found {len(findings)} potential issues.")
        Console.info("Run: python git_sync.py --bug-hunt")
        response = input("Continue with deployment? (yes/no): ")
        if response.lower() != "yes":
            Console.info("Deployment cancelled.")
            sys.exit(0)

    # Phase 1: Audit gates
    auditor = SystemAuditor(REPO_PATH)
    if not _run_audit_gates(auditor, args.force):
        sys.exit(1)

    # Phase 2: Stage & commit
    _stage_and_commit(args.message, args.force)

    # Phase 3: Sync with origin
    if not _sync_with_origin():
        sys.exit(1)

    # Phase 4: Post-deploy verification
    _post_deploy_verify()


if __name__ == "__main__":
    main()
