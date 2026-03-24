#!/bin/bash
# Synchronisiert den aktuellen Branch mit develop

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CURRENT_BRANCH=$(git branch --show-current)

echo -e "${YELLOW}=== Develop in aktuellen Branch mergen ===${NC}"
echo -e "Aktueller Branch: ${GREEN}$CURRENT_BRANCH${NC}"
echo ""

# Prüfen ob wir auf main oder develop sind
if [ "$CURRENT_BRANCH" == "main" ] || [ "$CURRENT_BRANCH" == "develop" ]; then
    echo -e "${RED}Fehler: Dieses Skript ist für Feature-Branches gedacht!${NC}"
    echo "Auf main/develop einfach 'git pull' verwenden."
    exit 1
fi

# Fetch neueste Änderungen
echo -e "→ Hole neueste Änderungen..."
git fetch origin

# Develop mergen
echo -e "→ Merge origin/develop..."
git merge origin/develop

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}⚠ Merge-Konflikte gefunden!${NC}"
    echo ""
    echo "So löst du Konflikte:"
    echo "  1. Öffne die markierten Dateien"
    echo "  2. Löse die Konflikte (<<<<<<< / =======  / >>>>>>>)"
    echo "  3. git add <gelöste-dateien>"
    echo "  4. git commit"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Branch ist synchron mit develop!${NC}"
