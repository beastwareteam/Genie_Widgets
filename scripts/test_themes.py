import os
import sys
import subprocess

# Test-Skript: Lädt alle Themes und prüft auf Qt/QSS-Fehler

def main():
    themes_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
    qss_files = [f for f in os.listdir(themes_dir) if f.endswith('.qss')]
    failed = False
    for qss_file in qss_files:
        print(f"Teste Theme: {qss_file}")
        # Dummy-Test: QSS-Validierungsskript aufrufen
        result = subprocess.run([sys.executable, 'scripts/check_qss_validity.py'], capture_output=True)
        if result.returncode != 0:
            print(f"FEHLER in {qss_file}:\n{result.stdout.decode()}\n{result.stderr.decode()}")
            failed = True
    if failed:
        print("Mindestens ein Theme ist fehlerhaft!")
        sys.exit(1)
    print("Alle Themes bestanden den Test.")

if __name__ == "__main__":
    main()
