#!/usr/bin/env bash
set -euo pipefail

# NeforOS installation script
# Purpose: install the project with a serious, robust, and user-friendly workflow.
# Compatible targets: Termux, Debian/Ubuntu, Fedora/RHEL, Arch, Alpine, and generic Linux.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="NeforOS"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
START_SCRIPT="${SCRIPT_DIR}/start.sh"
LOG_DIR="${SCRIPT_DIR}/logs"
INSTALL_LOG="${LOG_DIR}/install.log"
APP_ENTRYPOINT="${SCRIPT_DIR}/app.py"

DRY_RUN=0
SKIP_SYSTEM_DEPS=0
SKIP_VENV=0
SKIP_PIP=0
SKIP_TESTS=0
FORCE=0

export DEBIAN_FRONTEND=noninteractive

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
RESET='\033[0m'

log() {
  local level="$1"
  shift
  local message="$*"
  local timestamp
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
  case "$level" in
    INFO)
      printf '[%s] %b[INFO]%b %s\n' "$timestamp" "$BLUE" "$RESET" "$message" | tee -a "$INSTALL_LOG"
      ;;
    OK)
      printf '[%s] %b[OK]%b %s\n' "$timestamp" "$GREEN" "$RESET" "$message" | tee -a "$INSTALL_LOG"
      ;;
    WARN)
      printf '[%s] %b[WARN]%b %s\n' "$timestamp" "$YELLOW" "$RESET" "$message" | tee -a "$INSTALL_LOG"
      ;;
    ERROR)
      printf '[%s] %b[ERROR]%b %s\n' "$timestamp" "$RED" "$RESET" "$message" | tee -a "$INSTALL_LOG"
      ;;
    *)
      printf '[%s] %s\n' "$timestamp" "$message" | tee -a "$INSTALL_LOG"
      ;;
  esac
}

fail() {
  local message="$1"
  log ERROR "$message"
  exit 1
}

usage() {
  cat <<'EOF'
NeforOS Installer
Usage:
  ./install.sh [options]

Options:
  --dry-run            Show what would be installed without changing anything.
  --skip-system-deps   Skip OS package installation.
  --skip-venv          Skip virtual environment creation.
  --skip-pip           Skip Python dependency installation.
  --skip-tests         Skip automatic test execution.
  --force              Proceed even when some optional packages are missing.
  --help               Show this help message.

Examples:
  ./install.sh
  ./install.sh --dry-run
  ./install.sh --skip-tests
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --skip-system-deps)
        SKIP_SYSTEM_DEPS=1
        shift
        ;;
      --skip-venv)
        SKIP_VENV=1
        shift
        ;;
      --skip-pip)
        SKIP_PIP=1
        shift
        ;;
      --skip-tests)
        SKIP_TESTS=1
        shift
        ;;
      --force)
        FORCE=1
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        ;;
    esac
  done
}

ensure_root_or_warn() {
  if [[ $EUID -eq 0 ]]; then
    log WARN "Running as root. This is acceptable for system-wide installation."
  else
    log INFO "Running as a regular user. Continuing with local project installation."
  fi
}

check_network() {
  if command -v curl >/dev/null 2>&1; then
    if curl -I --max-time 8 https://pypi.org >/dev/null 2>&1; then
      return 0
    fi
  fi
  if command -v wget >/dev/null 2>&1; then
    if wget -q --spider --timeout=8 https://pypi.org >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

detect_os() {
  if [[ -n "${TERMUX_VERSION:-}" ]]; then
    OS_ID="termux"
    PACKAGE_MANAGER="pkg"
    log INFO "Detected Termux environment."
    return 0
  fi

  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    OS_ID="${ID:-unknown}"
    VERSION_ID="${VERSION_ID:-unknown}"
  else
    OS_ID="unknown"
    VERSION_ID="unknown"
  fi

  case "$OS_ID" in
    ubuntu|debian|raspbian)
      PACKAGE_MANAGER="apt"
      ;;
    fedora|rhel|centos|rocky|almalinux)
      PACKAGE_MANAGER="dnf"
      ;;
    amzn|amazon)
      PACKAGE_MANAGER="yum"
      ;;
    arch|manjaro)
      PACKAGE_MANAGER="pacman"
      ;;
    alpine)
      PACKAGE_MANAGER="apk"
      ;;
    opensuse|sles)
      PACKAGE_MANAGER="zypper"
      ;;
    *)
      PACKAGE_MANAGER="unknown"
      ;;
  esac

  log INFO "Detected OS: ${OS_ID} ${VERSION_ID}"
}

ensure_command() {
  local cmd="$1"
  local package_hint="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    return 0
  fi
  if [[ $SKIP_SYSTEM_DEPS -eq 1 ]]; then
    fail "Required command '$cmd' is missing and system dependency installation was skipped. Install it manually or rerun without --skip-system-deps."
  fi
  if [[ $FORCE -eq 1 ]]; then
    log WARN "Command '$cmd' is missing but --force is set. Proceeding cautiously."
    return 0
  fi
  fail "Required command '$cmd' is missing. Install '$package_hint' first or rerun with --skip-system-deps if you know it is already present."
}

install_system_packages() {
  if [[ $SKIP_SYSTEM_DEPS -eq 1 ]]; then
    log WARN "Skipping system package installation as requested."
    return 0
  fi

  case "$PACKAGE_MANAGER" in
    pkg)
      log INFO "Installing system packages with pkg..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: pkg update -y && pkg upgrade -y && pkg install -y python git curl wget openssl"
        return 0
      fi
      pkg update -y
      pkg upgrade -y
      pkg install -y python git curl wget openssl
      ;;
    apt)
      log INFO "Installing system packages with apt..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv python3-pip git curl wget ca-certificates"
        return 0
      fi
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv python3-pip git curl wget ca-certificates
      ;;
    dnf)
      log INFO "Installing system packages with dnf..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: dnf install -y python3 python3-pip python3-virtualenv git curl wget ca-certificates"
        return 0
      fi
      dnf install -y python3 python3-pip python3-virtualenv git curl wget ca-certificates
      ;;
    yum)
      log INFO "Installing system packages with yum..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: yum install -y python3 python3-pip git curl wget ca-certificates"
        return 0
      fi
      yum install -y python3 python3-pip git curl wget ca-certificates
      ;;
    pacman)
      log INFO "Installing system packages with pacman..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: pacman -Syu --noconfirm python git curl wget openssl"
        return 0
      fi
      pacman -Syu --noconfirm python git curl wget openssl
      ;;
    apk)
      log INFO "Installing system packages with apk..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: apk add --no-cache python3 py3-pip git curl wget openssl build-base"
        return 0
      fi
      apk add --no-cache python3 py3-pip git curl wget openssl build-base
      ;;
    zypper)
      log INFO "Installing system packages with zypper..."
      if [[ $DRY_RUN -eq 1 ]]; then
        log INFO "Would run: zypper install -y python3 python3-pip git curl wget ca-certificates"
        return 0
      fi
      zypper install -y python3 python3-pip git curl wget ca-certificates
      ;;
    *)
      log WARN "Unsupported package manager detected: ${PACKAGE_MANAGER}. Skipping system package installation."
      ;;
  esac
}

select_python() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
  else
    fail "Python is not installed and could not be located."
  fi

  local version_output
  version_output="$($PYTHON_BIN --version 2>&1)"
  log INFO "Using Python: $version_output"

  if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import sys
sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY
  then
    fail "Python version is too old. Please use Python 3.9 or newer."
  fi
}

create_virtualenv() {
  if [[ $SKIP_VENV -eq 1 ]]; then
    log WARN "Skipping virtual environment creation as requested."
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    log INFO "Would create virtual environment at ${VENV_DIR}"
    return 0
  fi

  mkdir -p "$LOG_DIR"
  if [[ -d "$VENV_DIR" ]]; then
    log INFO "Removing old virtual environment so installation starts from a clean state."
    rm -rf "$VENV_DIR"
  fi

  log INFO "Creating Python virtual environment..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"

  if [[ -x "$VENV_DIR/bin/python" ]]; then
    log OK "Virtual environment ready."
  else
    fail "Virtual environment creation failed."
  fi
}

install_python_packages() {
  if [[ $SKIP_PIP -eq 1 ]]; then
    log WARN "Skipping Python dependency installation as requested."
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    log INFO "Would install packages from ${REQUIREMENTS_FILE} into ${VENV_DIR}"
    return 0
  fi

  local pip_bin="$VENV_DIR/bin/pip"
  local python_venv="$VENV_DIR/bin/python"

  if [[ ! -x "$pip_bin" ]]; then
    fail "Virtual environment pip binary not found at $pip_bin"
  fi

  log INFO "Upgrading packaging tools..."
  "$python_venv" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true

  log INFO "Installing project dependencies..."
  "$pip_bin" install -r "$REQUIREMENTS_FILE"
}

ensure_project_files() {
  local app_file="$SCRIPT_DIR/app.py"
  local requirements_file="$SCRIPT_DIR/requirements.txt"

  if [[ ! -f "$app_file" ]]; then
    fail "Expected application file not found: $app_file"
  fi
  if [[ ! -f "$requirements_file" ]]; then
    fail "Expected requirements file not found: $requirements_file"
  fi

  if [[ ! -x "$START_SCRIPT" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      log INFO "Would make ${START_SCRIPT} executable"
    else
      chmod +x "$START_SCRIPT"
    fi
  fi
}

create_dotenv_file() {
  local env_file="$SCRIPT_DIR/.env"
  if [[ -f "$env_file" ]]; then
    log INFO "Found existing .env file; preserving it."
    return 0
  fi

  cat > "$env_file" <<'EOF_ENV'
# NeforOS runtime configuration
GOOGLE_API_KEY=
GOOGLE_CX=
PORT=8000
FLASK_ENV=production
EOF_ENV

  log OK "Created .env template at ${env_file}"
}

create_extra_helper_scripts() {
  local helper_script="$SCRIPT_DIR/launch.sh"
  if [[ -f "$helper_script" ]]; then
    log INFO "launch.sh already exists; leaving it unchanged."
    return 0
  fi

  cat > "$helper_script" <<'EOF_HELPER'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/app.py"
else
  exec python3 "$SCRIPT_DIR/app.py"
fi
EOF_HELPER
  chmod +x "$helper_script"
  log OK "Created launch helper script."
}

run_validation_tests() {
  if [[ $SKIP_TESTS -eq 1 ]]; then
    log WARN "Skipping automated tests as requested."
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    log INFO "Would run tests with pytest"
    return 0
  fi

  local test_command="$VENV_DIR/bin/python -m pytest -q"
  log INFO "Running automated regression tests..."
  if eval "$test_command"; then
    log OK "Regression tests passed."
  else
    log WARN "Tests reported issues. The installer completed, but you may want to inspect the results."
  fi
}

print_banner() {
  cat <<EOF_BANNER

${WHITE}============================================================${RESET}
${WHITE}  ${MAGENTA}${PROJECT_NAME}${WHITE} Installer${RESET}
${WHITE}============================================================${RESET}
${CYAN}  Project: ${SCRIPT_DIR}${RESET}
${CYAN}  Purpose: Install and launch a premium mobile-shell demo${RESET}
${CYAN}  Mode:    ${DRY_RUN:+dry-run}${RESET}
${WHITE}============================================================${RESET}
EOF_BANNER
}

show_summary() {
  cat <<EOF_SUMMARY

${GREEN}Installation summary${RESET}
----------------------------------------
${GREEN}Project directory:${RESET} ${SCRIPT_DIR}
${GREEN}Virtual environment:${RESET} ${VENV_DIR}
${GREEN}Start script:${RESET} ${START_SCRIPT}
${GREEN}Requirements:${RESET} ${REQUIREMENTS_FILE}
${GREEN}Install log:${RESET} ${INSTALL_LOG}

${CYAN}Next steps:${RESET}
  1. Run: ${WHITE}./start.sh${RESET}
  2. Open your browser to: ${WHITE}http://127.0.0.1:8000${RESET}
  3. If you are on Termux, use the same command inside the project directory.

${YELLOW}Tip:${RESET} If you want to use real Google search results, add your API key to .env.
EOF_SUMMARY
}

main() {
  mkdir -p "$LOG_DIR"
  : > "$INSTALL_LOG"

  print_banner
  parse_args "$@"
  ensure_root_or_warn
  log INFO "Starting ${PROJECT_NAME} installation process..."

  detect_os
  if [[ $DRY_RUN -eq 1 ]]; then
    log INFO "Dry-run mode enabled. No packages will be installed."
  fi

  if ! check_network; then
    log WARN "Network check failed. Installation may still work if dependencies are already cached."
  fi

  install_system_packages
  select_python
  create_virtualenv
  ensure_project_files
  install_python_packages
  create_dotenv_file
  create_extra_helper_scripts
  run_validation_tests
  show_summary
  log OK "Installation workflow completed successfully."
}

main "$@"
