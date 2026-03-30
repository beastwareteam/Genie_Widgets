import subprocess
import sys

# Build-Skript für Theme-System: QSS-Generierung + Validierung

def main():
    # 1. QSS generieren
    print("[1/2] Generiere QSS aus Tokens ...")
    subprocess.run([sys.executable, "scripts/generate_qss.py"], check=True)
    # 2. QSS validieren
    print("[2/2] Prüfe QSS auf ungültige Properties ...")
    subprocess.run([sys.executable, "scripts/check_qss_validity.py"], check=True)
    print("Build erfolgreich: Theme-System ist konsistent.")

if __name__ == "__main__":
    main()
