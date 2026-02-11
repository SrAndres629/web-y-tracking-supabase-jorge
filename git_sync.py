import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

import requests
from dotenv import load_dotenv

load_dotenv()

# =================================================================
# 🛡️ SILICON VALLEY DEPLOYMENT PROTOCOL
# =================================================================
# Robust, Idempotent, and Observable.
# =================================================================

# --- CONFIGURATION (Credentials loaded from environment) ---
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN") # Safer alternative
CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")

if not (CLOUDFLARE_API_KEY or CLOUDFLARE_API_TOKEN) or not CLOUDFLARE_ZONE_ID:
    print("\033[93m[WARN] Missing Cloudflare Credentials in .env. Purge will be skipped.\033[0m")

if not CLOUDFLARE_API_KEY or not CLOUDFLARE_EMAIL:
    # We don't block execution effectively here as they might not be needed for all ops,
    # but we should warn or handle gracefully in functions that need them.
    pass
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
# -------------------------------------------------------


class Console:
    """Professional Logging Wrapper"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

    @staticmethod
    def _print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            enc = sys.stdout.encoding or "utf-8"
            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write((text + "\n").encode(enc, errors="replace"))
                sys.stdout.flush()
            else:
                print(text.encode(enc, errors="replace").decode(enc, errors="replace"))

    @staticmethod
    def log(msg, symbol="*"):
        Console._print(f"{symbol} {msg}")

    @staticmethod
    def success(msg):
        Console._print(f"{Console.GREEN}[OK] {msg}{Console.ENDC}")

    @staticmethod
    def error(msg):
        Console._print(f"{Console.FAIL}[ERROR] {msg}{Console.ENDC}")

    @staticmethod
    def info(msg):
        Console._print(f"{Console.CYAN}[INFO] {msg}{Console.ENDC}")

    @staticmethod
    def warning(msg):
        Console._print(f"{Console.WARNING}[WARN] {msg}{Console.ENDC}")


class SystemAuditor:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.issues = []
        self.raw_logs = []
        self.suggestions = []

    def check_environment(self):
        Console.log("Verifying Execution Environment...", "🔍")
        required_modules = ["pytest", "hypothesis", "httpx"]
        missing = []
        for mod in required_modules:
            try:
                __import__(mod)
            except ImportError:
                missing.append(mod)

        if missing:
            self._add_issue(
                file_path="ENVIRONMENT",
                line="N/A",
                err_type="Exception",
                message=f"Missing modules: {', '.join(missing)}",
                phase="Environment",
            )
            Console.error(f"CRITICAL: Missing core engineering mandates: {', '.join(missing)}")
            Console.info("Run: pip install -r requirements.txt")
            return False

        Console.success("Environment Integrity Verified (Dependencies Loaded).")
        return True

    def run_phase(self, name, path, audit_mode=True):
        Console.log(f"Running Integrity: {name}...", "-")

        # Cross-platform environment variables
        env = os.environ.copy()
        if audit_mode:
            env["AUDIT_MODE"] = "1"
        
        pytest_cmd = [
            sys.executable, "-m", "pytest", path, "-v", "-W", "error",
            "--tb=short", "--maxfail=0"
        ]

        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            env=env
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + "\n" + stderr
        self.raw_logs.append(combined)

        if result.returncode != 0:
            Console.error(f"Phase failed: {name}")
            issues = self._extract_issues(combined, phase=name)
            if not issues:
                self._add_issue(
                    file_path="UNKNOWN",
                    line="N/A",
                    err_type="Exception",
                    message="Unknown failure. Check logs.",
                    phase=name,
                )
        else:
            Console.success(f"Phase passed: {name}")

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
        last_file = None
        last_line = None

        for line in output.splitlines():
            file_match = re.search(r'File "([^"]+\.py)", line (\d+)', line)
            if file_match:
                last_file = file_match.group(1)
                last_line = file_match.group(2)
                continue

            win_path = re.search(r"([A-Za-z]:\\[^:]+\.py):(\d+):", line)
            unix_path = re.search(r"(/[^:]+\.py):(\d+):", line)
            if win_path:
                last_file, last_line = win_path.group(1), win_path.group(2)
                continue
            if unix_path:
                last_file, last_line = unix_path.group(1), unix_path.group(2)
                continue

            error_match = re.match(r"^E\s+(.*)", line)
            if error_match:
                msg = error_match.group(1)
                err_type = self._classify_error_type(msg)
                self._add_issue(
                    file_path=last_file or "UNKNOWN",
                    line=last_line or "N/A",
                    err_type=err_type,
                    message=msg,
                    phase=phase,
                )
                issues_added += 1
                continue

            fail_match = re.match(r"^FAILED\s+(.+?)\s+-\s+(.*)$", line)
            if fail_match:
                msg = fail_match.group(2)
                err_type = self._classify_error_type(msg)
                self._add_issue(
                    file_path=last_file or fail_match.group(1),
                    line=last_line or "N/A",
                    err_type=err_type,
                    message=msg,
                    phase=phase,
                )
                issues_added += 1

        return issues_added

    def _classify_error_type(self, message):
        msg = message.lower()
        if "assert" in msg or "assertionerror" in msg:
            return "Assert"
        if "timeout" in msg or "timeoutexception" in msg:
            return "Timeout"
        if "exception" in msg or "error" in msg or "failed" in msg:
            return "Exception"
        return "Exception"

    def analyze_suggestions(self):
        combined = "\n".join(self.raw_logs).lower()
        suggestion_map = {
            r"oauth.*190|error 190": "Posible error de credenciales OAuth. Revisa tus variables .env y el token.",
            r"permission denied": "Parece un error de permisos. Revisa accesos a archivos o credenciales.",
            r"timeout": "Hay un timeout. Revisa red/servicios externos y aumenta el timeout si aplica.",
        }
        for pattern, suggestion in suggestion_map.items():
            if re.search(pattern, combined):
                self.suggestions.append(suggestion)

    def report(self):
        Console.log("========== FORENSIC DIAGNOSTIC REPORT ==========", "=")
        if not self.issues:
            Console.success("Score de Salud: 100% (Zero Defects Detected)")
            return True

        total_phases = len({i["phase"] for i in self.issues})
        Console.error(f"Score de Salud: < 100% ({len(self.issues)} errores en {total_phases} fases)")

        rows = []
        for issue in self.issues:
            rows.append(
                (
                    self._shorten_path(issue["file"]),
                    issue["line"],
                    issue["type"],
                    issue["phase"],
                )
            )

        headers = ("Archivo", "Linea", "Tipo", "Fase")
        col_widths = [
            max(len(headers[0]), *(len(r[0]) for r in rows)),
            max(len(headers[1]), *(len(r[1]) for r in rows)),
            max(len(headers[2]), *(len(r[2]) for r in rows)),
            max(len(headers[3]), *(len(r[3]) for r in rows)),
        ]

        def fmt_row(values):
            return (
                f"{values[0]:<{col_widths[0]}}  "
                f"{values[1]:<{col_widths[1]}}  "
                f"{values[2]:<{col_widths[2]}}  "
                f"{values[3]:<{col_widths[3]}}"
            )

        Console._print(Console.BOLD + fmt_row(headers) + Console.ENDC)
        for row in rows:
            Console._print(Console.FAIL + fmt_row(row) + Console.ENDC)

        Console.log("Detalles de errores:", "!")
        for issue in self.issues:
            Console._print(
                f"- {self._shorten_path(issue['file'])}:{issue['line']} "
                f"[{issue['type']}] {issue['message']}"
            )

        self.analyze_suggestions()
        if self.suggestions:
            Console.log("Sugerencias de mejora:", "💡")
            for suggestion in sorted(set(self.suggestions)):
                Console._print(f"- {suggestion}")

        return False

    def _shorten_path(self, path):
        if not path or path in {"UNKNOWN", "ENVIRONMENT"}:
            return path
        if len(path) <= 80:
            return path
        return f"...{path[-77:]}"


def purge_cloudflare_cache():
    """Purge everything from Cloudflare Edge for jorgeaguirreflores.com"""
    Console.log("Initiating Cloudflare Cache Purge (Standard SV Protocol)...", "🧹")
    has_token = bool(CLOUDFLARE_API_TOKEN)
    has_global_key = bool(CLOUDFLARE_API_KEY and CLOUDFLARE_EMAIL)
    if not CLOUDFLARE_ZONE_ID or not (has_token or has_global_key):
        Console.warning("Skipping Cloudflare Purge: Missing Credentials.")
        return

    url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/purge_cache"
    headers = {
        "Content-Type": "application/json",
    }
    
    # Priority: API Token (Bearer) > Global API Key (X-Auth-Key)
    if has_token:
        headers["Authorization"] = f"Bearer {CLOUDFLARE_API_TOKEN}"
    elif has_global_key:
        headers["X-Auth-Email"] = CLOUDFLARE_EMAIL
        headers["X-Auth-Key"] = CLOUDFLARE_API_KEY
    else:
        Console.warning("Skipping Cloudflare Purge: Insufficient Credentials.")
        return
    data = json.dumps({"purge_everything": True}).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                Console.success("CLOUDFLARE CACHE PURGED. Site is now live at the Edge.")
            else:
                Console.error(f"Cloudflare Purge Issue: {result.get('errors')}")
    except Exception as e:
        Console.error(f"Critical Purge Exception: {e}")


def run_cmd(command, cwd=None, exit_on_fail=False):
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        if exit_on_fail:
            Console.error(f"Command failed: {command}\n{result.stderr.strip()}")
            sys.exit(1)
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="Silicon Valley Deployment Pipeline")
    parser.add_argument("--force", action="store_true", help="Bypass checks (NOT RECOMMENDED)")
    parser.add_argument("message", nargs="?", default=None, help="Commit message")
    args = parser.parse_args()

    print(f"\n{Console.BOLD}[NEURAL-SYNC] Initializing Silicon Valley Deployment Protocol...{Console.ENDC}\n")

    auditor = SystemAuditor(REPO_PATH)
    env_ok = auditor.check_environment()

    integrity_phases = [
        {"name": "Architecture & Boot", "path": "tests/00_architecture"},
        {"name": "Unit Ops", "path": "tests/01_unit"},
        {"name": "Integration & Sync", "path": "tests/02_integration"},
        {"name": "Security & Perf Audit", "path": "tests/03_audit"},
    ]

    if args.force:
        Console.warning("⚠️ SKIPPING GATES: --force flag detected. You are flying blind.")
    else:
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
    if not healthy and not args.force:
        Console.error("Deployment blocked due to failures. Fix issues and re-run.")
        sys.exit(1)

    Console.log("[2/6] Staging & Committing...", "+")
    run_cmd("git add .", cwd=REPO_PATH)

    success, output, _ = run_cmd("git status --porcelain", cwd=REPO_PATH)
    has_changes = bool(output.strip())

    if has_changes or args.force:
        time_str = datetime.datetime.now().strftime("%H:%M")
        msg = args.message if args.message else f"chore: system sync {time_str}"

        if not has_changes and args.force:
            msg += " (FORCED)"
            run_cmd(f'git commit --allow-empty -m "{msg}"', cwd=REPO_PATH)
        elif has_changes:
            Console.log(f"Committing source: '{msg}'", "📝")
            run_cmd(f'git commit -m "{msg}"', cwd=REPO_PATH)
    else:
        Console.info("No local changes to commit.")

    Console.log("[3/6] Synchronizing with Origin...", ">")
    run_cmd("git fetch origin", cwd=REPO_PATH)

    Console.log("[4/6] Rebase Integration...", "~")
    success, _, _ = run_cmd("git pull origin main --rebase", cwd=REPO_PATH)
    if not success:
        Console.error("CRITICAL: Rebase Conflict. Resolve manually with 'git status'.")
        sys.exit(1)

    _, local_sha, _ = run_cmd("git rev-parse HEAD", cwd=REPO_PATH)
    _, remote_sha, _ = run_cmd("git rev-parse origin/main", cwd=REPO_PATH)

    if local_sha.strip() == remote_sha.strip():
        Console.success("SYSTEM SYNCED. No Ops Required.")
        return
    else:
        Console.log("Local is ahead. Proceeding to Push...", "⬆️")

    Console.log("[6/6] Injecting into Production...", "!")
    success, _, stderr = run_cmd("git push -u origin main", cwd=REPO_PATH)

    if success:
        Console.success("✅ DEPLOYMENT SUCCESSFUL")
        Console.log("Validating Edge Cache Purge...", "🧹")
        purge_cloudflare_cache()

        try:
            url = "https://jorgeaguirreflores.com"
            Console.log(f"🔥 Pre-Warming Global Edge: {url}", "🔥")
            time.sleep(10)

            debug_key = os.getenv("PREWARM_DEBUG_KEY") or os.getenv("DEBUG_DIAGNOSTIC_KEY")
            headers = {"User-Agent": "SV-Prewarm/1.0"}
            params = {}
            if debug_key:
                headers["X-Prewarm-Debug"] = debug_key
                params["__debug_key"] = debug_key
            else:
                headers["X-Prewarm-Debug"] = "1"
                params["__debug_key"] = "1"

            resp = requests.get(url, timeout=15, headers=headers, params=params)
            if resp.status_code == 200:
                version_match = re.search(r"\?v=(\d+)", resp.text)
                new_version = version_match.group(1) if version_match else "Unknown"
                Console.success(f"PRODUCCIÓN ACTUALIZADA: Versión Atómica {new_version} activa.")
            else:
                Console.warning(f"Pre-Warm status: {resp.status_code}")
                Console.info(f"Pre-Warm content-type: {resp.headers.get('content-type', 'unknown')}")
                try:
                    if "application/json" in (resp.headers.get("content-type") or ""):
                        Console.info(f"Diagnostic Full (JSON): {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
                    else:
                        Console.info(f"Diagnostic Full (RAW): {resp.text}")
                except Exception as e:
                    Console.warning(f"Pre-Warm response decode failed: {e}")
                
                # Secondary probe for full diagnostics (template paths)
                try:
                    diag_url = f"{url}/__prewarm_debug"
                    diag_resp = requests.get(diag_url, timeout=15, headers=headers, params=params)
                    if "application/json" in (diag_resp.headers.get("content-type") or ""):
                        Console.info(f"Pre-Warm Diagnostics: {json.dumps(diag_resp.json(), indent=2, ensure_ascii=False)}")
                    else:
                        Console.info(f"Pre-Warm Diagnostics (RAW): {diag_resp.text}")
                except Exception as e:
                    Console.warning(f"Pre-Warm diagnostics failed: {e}")
        except Exception as e:
            Console.warning(f"Pre-Warm failed: {e}")

        print(f"\n{Console.GREEN}System is Live: https://jorgeaguirreflores.com{Console.ENDC}")
    else:
        Console.error(f"Push Failed: {stderr}")


if __name__ == "__main__":
    main()
