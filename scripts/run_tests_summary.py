"""Quick test runner to get summary only."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
    capture_output=True,
    text=True,
    timeout=120
)

# Print last 20 lines only
lines = result.stdout.split('\n')
for line in lines[-20:]:
    print(line)

print(f"\nExit code: {result.returncode}")
