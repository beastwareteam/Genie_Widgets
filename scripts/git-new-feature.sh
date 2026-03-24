#!/bin/bash
# Schnelles Erstellen eines neuen Feature-Branches

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prüfen ob Feature-Name angegeben
if [ -z "$1" ]; then
    echo -e "${RED}Fehler: Feature-Name fehlt!${NC}"
    echo ""
    echo "Verwendung: ./scripts/git-new-feature.sh <feature-name>"
    echo "Beispiel:   ./scripts/git-new-feature.sh add-dark-mode"
    echo ""
    exit 1
fi

FEATURE_NAME=$1
BRANCH_NAME="feature/$FEATURE_NAME"

echo -e "${YELLOW}=== Neuen Feature-Branch erstellen ===${NC}"
echo ""

# Zu develop wechseln
echo -e "→ Wechsle zu develop..."
git checkout develop
if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Wechsel zu develop!${NC}"
    exit 1
fi

# Develop aktualisieren
echo -e "→ Aktualisiere develop..."
git pull origin develop
if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Pull von develop!${NC}"
    exit 1
fi

# Feature-Branch erstellen
echo -e "→ Erstelle Branch: ${GREEN}$BRANCH_NAME${NC}"
git checkout -b "$BRANCH_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Erstellen des Branches!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Feature-Branch erstellt!${NC}"
echo ""
echo "Nächste Schritte:"
echo "  1. Änderungen vornehmen"
echo "  2. git add . && git commit -m 'feat: Beschreibung'"
echo "  3. git push -u origin $BRANCH_NAME"
echo "  4. PR auf GitHub erstellen → Base: develop"
echo ""
