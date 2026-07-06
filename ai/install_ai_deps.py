import os
import sys
import subprocess
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PYTHON_DIR = PROJECT_ROOT / "runtime" / "python311"
PYTHON_EXE = PYTHON_DIR / "python.exe"
PTH_FILE = PYTHON_DIR / "python311._pth"

AI_DIR = PROJECT_ROOT / "ai"
REQUIREMENTS_FILE = AI_DIR / "requirements.txt"
DEPS_MARKER = AI_DIR / ".deps_installed"

GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
GET_PIP_FILE = AI_DIR / "get-pip.py"


def run_command(command, cwd=None):
    print()
    print("Rulez comanda:")
    print(" ".join(str(x) for x in command))
    print()

    subprocess.check_call(
        command,
        cwd=str(cwd or PROJECT_ROOT),
    )


def ensure_embedded_python_exists():
    if not PYTHON_EXE.exists():
        raise FileNotFoundError(
            f"Nu am găsit Python-ul inclus aici:\n{PYTHON_EXE}"
        )

    if not PTH_FILE.exists():
        raise FileNotFoundError(
            f"Nu am găsit fișierul python311._pth aici:\n{PTH_FILE}"
        )


def relaunch_with_embedded_python_if_needed():
    current_python = Path(sys.executable).resolve()
    embedded_python = PYTHON_EXE.resolve()

    if current_python != embedded_python:
        print("Scriptul nu rulează cu Python-ul inclus.")
        print(f"Python curent: {current_python}")
        print(f"Python inclus: {embedded_python}")
        print("Repornez scriptul cu Python-ul inclus...")

        run_command([str(PYTHON_EXE), str(Path(__file__).resolve())])
        sys.exit(0)


def patch_python_pth():
    """
    Python embeddable folosește python311._pth pentru sys.path.
    Trebuie să activăm import site și să ne asigurăm că Lib/site-packages
    este inclus, altfel pip și pachetele instalate nu vor fi vizibile.
    """

    site_packages_dir = PYTHON_DIR / "Lib" / "site-packages"
    site_packages_dir.mkdir(parents=True, exist_ok=True)

    text = PTH_FILE.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    changed = False

    if "Lib/site-packages" not in lines and r"Lib\site-packages" not in lines:
        lines.append("Lib/site-packages")
        changed = True

    new_lines = []
    has_import_site = False

    for line in lines:
        if line == "#import site":
            new_lines.append("import site")
            has_import_site = True
            changed = True
        else:
            new_lines.append(line)
            if line == "import site":
                has_import_site = True

    if not has_import_site:
        new_lines.append("import site")
        changed = True

    if changed:
        PTH_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("Am actualizat python311._pth.")
    else:
        print("python311._pth este deja configurat corect.")


def ensure_requirements_file():
    if REQUIREMENTS_FILE.exists():
        return

    REQUIREMENTS_FILE.write_text(
        "\n".join(
            [
                "fastapi",
                "uvicorn",
                "requests",
                "pydantic",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Am creat requirements.txt aici:\n{REQUIREMENTS_FILE}")


def download_get_pip():
    if GET_PIP_FILE.exists():
        print("get-pip.py există deja.")
        return

    print("Descarc get-pip.py...")
    urllib.request.urlretrieve(GET_PIP_URL, GET_PIP_FILE)
    print("get-pip.py descărcat.")


def pip_is_available():
    try:
        subprocess.check_call(
            [str(PYTHON_EXE), "-m", "pip", "--version"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def ensure_pip():
    if pip_is_available():
        print("pip este deja instalat.")
        return

    download_get_pip()

    print("Instalez pip în Python-ul inclus...")
    run_command([str(PYTHON_EXE), str(GET_PIP_FILE)])

    if not pip_is_available():
        raise RuntimeError("pip nu s-a instalat corect.")

    print("pip instalat corect.")


def install_requirements():
    print("Instalez/actualizez dependențele AI...")

    run_command(
        [
            str(PYTHON_EXE),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
        ]
    )

    run_command(
        [
            str(PYTHON_EXE),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-r",
            str(REQUIREMENTS_FILE),
        ]
    )

    DEPS_MARKER.write_text(
        "AI dependencies installed successfully.\n",
        encoding="utf-8",
    )

    print()
    print("Dependențele AI au fost instalate cu succes.")


def main():
    print("=== Order of the Dragon - AI Dependencies Installer ===")

    ensure_embedded_python_exists()
    patch_python_pth()
    relaunch_with_embedded_python_if_needed()
    ensure_requirements_file()
    ensure_pip()
    install_requirements()

    print()
    print("Gata. Python-ul inclus este pregătit pentru serverul AI.")
    print(f"Marker creat: {DEPS_MARKER}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print()
        print("A apărut o eroare la instalarea dependențelor AI:")
        print(exc)
        print()
        input("Apasă Enter pentru a închide...")
        raise