"""
Phase 3 - Frontend build and configuration check.

Verifies .env, API URL, production build, and that dist/ contains assets.

Usage (from repo root or backend/):
    python scripts/verify_frontend.py
"""
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_ROOT = os.path.join(REPO_ROOT, "frontend")
NPM_CMD = os.environ.get("NPM_CMD", r"C:\Program Files\nodejs\npm.cmd")


def load_env_file(path):
    values = {}
    if not os.path.isfile(path):
        return values
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def find_npm():
    if os.path.isfile(NPM_CMD):
        return NPM_CMD
    for candidate in ("npm", "npm.cmd"):
        try:
            result = subprocess.run(
                ["where", candidate],
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.returncode == 0:
                return result.stdout.strip().splitlines()[0]
        except OSError:
            pass
    return None


def check_required_files():
    required = [
        "package.json",
        "vite.config.js",
        "src/main.jsx",
        "src/App.jsx",
        "src/api/axios/Instance.js",
        "src/services/api.js",
    ]
    missing = [f for f in required if not os.path.isfile(os.path.join(FRONTEND_ROOT, f))]
    return missing


def check_api_js_paths():
    api_path = os.path.join(FRONTEND_ROOT, "src", "services", "api.js")
    with open(api_path, encoding="utf-8") as handle:
        content = handle.read()
    paths = re.findall(r"['`](/api/v1/[^'`\"]+)['`]", content)
    return paths


def run_build(npm):
    env = os.environ.copy()
    env_file = os.path.join(FRONTEND_ROOT, ".env")
    file_env = load_env_file(env_file)
    for key, val in file_env.items():
        env[key] = val
    result = subprocess.run(
        [npm, "run", "build"],
        cwd=FRONTEND_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode == 0, result.stdout + result.stderr


def main():
    failed = 0
    warnings = 0

    print("=" * 60)
    print("PHASE 3: FRONTEND")
    print("=" * 60)

    print("\n1. Project files")
    missing = check_required_files()
    if missing:
        for f in missing:
            print(f"   [FAIL] Missing {f}")
        return 1
    print("   [OK] Core source files present")

    print("\n2. Environment (frontend/.env)")
    env_path = os.path.join(FRONTEND_ROOT, ".env")
    example_path = os.path.join(FRONTEND_ROOT, ".env.example")
    if not os.path.isfile(env_path):
        if os.path.isfile(example_path):
            import shutil

            shutil.copy(example_path, env_path)
            print("   [WARN] Created frontend/.env from .env.example")
            warnings += 1
        else:
            print("   [FAIL] No frontend/.env or .env.example")
            failed += 1
    env = load_env_file(env_path)
    api_url = env.get("VITE_API_URL", "")
    use_mock = env.get("VITE_USE_MOCK", "false")
    print(f"   VITE_API_URL={api_url or '(default http://localhost:8000)'}")
    print(f"   VITE_USE_MOCK={use_mock}")
    if use_mock.lower() == "true":
        print("   [FAIL] VITE_USE_MOCK=true - app will not call Oracle backend")
        failed += 1
    elif not api_url:
        print("   [WARN] VITE_API_URL not set - using default localhost:8000")
        warnings += 1
    else:
        print("   [OK] API URL configured")

    print("\n3. API client paths (api.js)")
    paths = check_api_js_paths()
    print(f"   [OK] Found {len(paths)} API paths in services/api.js")

    print("\n4. Production build (npm run build)")
    npm = find_npm()
    if not npm:
        print("   [FAIL] npm not found - install Node.js 18+")
        return 1
    build_ok, build_output = run_build(npm)
    if build_ok:
        dist_index = os.path.join(FRONTEND_ROOT, "dist", "index.html")
        dist_assets = os.path.join(FRONTEND_ROOT, "dist", "assets")
        if os.path.isfile(dist_index) and os.path.isdir(dist_assets):
            assets = os.listdir(dist_assets)
            print(f"   [OK] Build succeeded - dist/ has index.html + {len(assets)} asset(s)")
        else:
            print("   [FAIL] Build ran but dist/ output is incomplete")
            failed += 1
    else:
        print("   [FAIL] Build failed:")
        for line in build_output.strip().splitlines()[-15:]:
            print(f"      {line}")
        failed += 1

    print("\n" + "=" * 60)
    if failed:
        print(f"PHASE 3: FAILED ({failed} issue(s))")
        return 1
    if warnings:
        print(f"PHASE 3: PASSED with {warnings} warning(s) - frontend ready")
    else:
        print("PHASE 3: PASSED - frontend ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
