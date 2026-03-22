"""Phase 1 - Manual Testing Guide

📋 Automatisierte Unit Tests: ✅ 28/28 ERFOLGREICH

Jetzt folgt das MANUELLE TESTING gegen die laufende App.
🧪 Bitte teste alle Szenarien AUSFÜHRLICH bevor du die Fortsetzung freigibst.
"""

# =============================================================================
# 🎯 PHASE 1: TAB SELECTOR VISIBILITY - MANUAL TEST GUIDE
# =============================================================================

## ⏸️ PAUSE: MANUAL UI TESTING REQUIRED

### Automatisierte Tests Ergebnis:
✅ 28 Unit Tests passed in 0.63s
- TabSelectorMonitor: 14 Tests ✅
- TabSelectorEventHandler: 5 Tests ✅
- TabSelectorVisibilityController: 8 Tests ✅
- Integration Test: 1 Test ✅

---

### 🚀 Nächste Schritte für den Nutzer:

1. **App starten:**
   ```bash
   # Terminal 1: Aktiviere Virtual Environment
   .venv\Scripts\Activate.ps1
   
   # Terminal 1: Starte die App
   python src/widgetsystem/core/main.py
   # ODER
   python examples/complete_demo.py
   ```

2. **Führe ALLE Test-Szenarien durch:**

---

## 📝 TEST-SZENARIEN

### ✅ TEST 1: Single Tab - Selector AUSGEBLENDET
**Erwartung:** Reiter-Wechsler-Pfeil sollte NICHT sichtbar sein

**Schritte:**
1. App starten
2. Beobachte left_panel (sollte oben links sein)
3. Schaue auf die Title Bar des left_panel
4. **Prüfe:** Pfeil nach unten neben "Left Panel" Text sollte NICHT DA SEIN

**Bestätigung:** ✅ Pfeil ist weg, oder ❌ Pfeil ist noch da?

---

### ✅ TEST 2: Multiple Tabs - Selector SICHTBAR
**Erwartung:** Reiter-Wechsler-Pfeil wird sichtbar wenn 2+ Panels in selbedem Bereich

**Schritte:**
1. Im left_panel Bereich, float das bottom_panel (oder anderes)
2. Docke bottom_panel so an, dass es im SELBEN BEREICH wie left_panel ist
   - Ziehe bottom_panel auf left_panel
   - Lass es als Tab fallen (nicht als neuer Split)
3. **Prüfe:** Pfeil sollte jetzt SICHTBAR sein
4. Klicke auf den Pfeil → Dropdown sollte zeigen:
   - "Left Panel"
   - "Bottom Panel"
5. Klick auf "Bottom Panel" → sollte Tab wechseln

**Bestätigung:** ✅ Pfeil sichtbar + Dropdown funktioniert, oder ❌ Nein?

---

### ✅ TEST 3: Tab Close - Selector WIEDER AUSGEBLENDET
**Erwartung:** Wenn nur noch 1 Tab bleibt, Selector wieder weg

**Schritte:**
1. Von TEST 2: Habe zwei Tabs im selben Bereich (left_panel + bottom_panel)
2. Pfeil ist sichtbar
3. Schließe einen Tab (z.B. klick X auf bottom_panel)
4. **Prüfe:** Pfeil sollte jetzt wieder AUSGEBLENDET sein

**Bestätigung:** ✅ Pfeil weg, oder ❌ Pfeil bleibt sichtbar?

---

### ✅ TEST 4: Multiple Areas Independent
**Erwartung:** Jeder Bereich verwaltet seinen Selector unabhängig

**Schritte:**
1. Float 3-4 verschiedene Panels
2. Gruppe sie in verschiedenen Bereichen zu Tabs:
   - Bereich A: left_panel + center_panel → 2 Tabs
   - Bereich B: bottom_panel (allein) → 1 Tab
3. **Prüfe:**
   - Bereich A Selector: SICHTBAR ✅
   - Bereich B Selector: AUSGEBLENDET ✅

**Bestätigung:** ✅ Unabhängige Kontrolle, oder ❌ Synchronisiert?

---

### ✅ TEST 5: Floating Panels
**Erwartung:** Floating Panels haben keinen Tab-Selector (sind alleinstehend)

**Schritte:**
1. Float ein Panel (bleibt allein im FloatingContainer)
2. **Prüfe:** Floating Container sollte KEINEN Selector haben

**Bestätigung:** ✅ Kein Selector bei Float, oder ❌ Hat einen?

---

## 🔍 DEBUG-TIPPS bei Problemen

### Problem: Pfeil wird bei 2+ Tabs nicht angezeigt

**Debug-Schritte:**
1. Öffne DevTools (falls vorhanden):
   ```python
   # In main.py nach _setup_docking():
   print("Tab Monitor:", self._tab_monitor.get_all_area_counts())
   ```

2. Prüfe ob Monitor erkannt hat dass es 2 Tabs gibt:
   ```
   Tab Monitor: {'area_1': 2}  ← sollte 2 sein!
   ```

3. Wenn nicht 2: CDockManager sendet nicht die Signale richtig

4. Wenn 2 aber Pfeil trotzdem weg: Visibility Controller findet den Selector nicht

### Problem: Pfeil wird angezeigt aber verschwindet nicht bei Tab-Close

1. Das liegt daran dass `_on_dock_widget_removed` nicht richtig aufgerufen wird
2. Prüf die CDockManager Signal-Verbindungen

### Problem: Exception oder Crash äußer beim Tab-Wechsel

1. Schaue in die Terminal-Ausgabe auf Error-Messages
2. Häufiger Fehler: QtAds version ist zu alt
3. Prüfe: `python -c "import PySide6QtAds; print(PySide6QtAds.__version__)"`

---

## ✅ BESTÄTIGUNG NACH TESTING

Wenn alle 5 Test-Szenarien ✅ grün sind:

**Schreibe hier die Bestätigung:**
```
✅ TEST 1: Single Tab - Selector AUSGEBLENDET ← JA/NEIN?
✅ TEST 2: Multiple Tabs - Selector SICHTBAR ← JA/NEIN?
✅ TEST 3: Tab Close - Selector WIEDER WEG ← JA/NEIN?
✅ TEST 4: Multiple Areas Independent ← JA/NEIN?
✅ TEST 5: Floating Panels ← JA/NEIN?

Weitere Bugs oder Auffälligkeiten?
→ Beschreib hier...
```

---

## 📊 Wenn alles grün ist:

Schreib: **"Phase 1 ✅ ERFOLGREICH GETESTET"**

Dann können wir zu **Phase 2: Float-Button Persistierung** übergehen.

---

## 📚 Dokumentation zu Phase 1:

Siehe: `docs/PHASE_1_TAB_SELECTOR.md` für:
- Architektur Details
- Code Erklärung
- Datenfluss
- Bekannte Limitierungen
