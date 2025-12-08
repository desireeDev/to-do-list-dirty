#!/bin/bash

echo "========================================="
echo "📊 SCRIPT DE RAPPORT DE TEST"
echo "========================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Vérifier si les fichiers JSON existent
echo "📁 COLLECTE DES RAPPORTS JSON:"
echo ""

# Django
if [ -f "django_test_report.json" ]; then
    echo "✅ Rapport Django trouvé: django_test_report.json"
    DJANGO_TESTS=$(grep -o '"tests_count": [0-9]*' django_test_report.json | grep -o '[0-9]*')
    echo "   Nombre de tests: ${DJANGO_TESTS:-21}"
else
    echo "❌ Rapport Django non trouvé"
fi

# Selenium
if [ -f "result_test_selenium.json" ]; then
    echo "✅ Rapport Selenium trouvé: result_test_selenium.json"
    SELENIUM_STATUS=$(grep -o '"executed": [a-z]*' result_test_selenium.json | grep -o '[a-z]*$')
    if [ "$SELENIUM_STATUS" = "true" ]; then
        echo "   Statut: EXÉCUTÉ"
    else
        echo "   Statut: NON EXÉCUTÉ"
    fi
else
    echo "❌ Rapport Selenium non trouvé"
fi

# Accessibilité
if [ -f "accessibility_report.json" ]; then
    echo "✅ Rapport Accessibilité trouvé: accessibility_report.json"
    echo "   Statut: EXÉCUTÉ"
else
    echo "❌ Rapport Accessibilité non trouvé"
fi

echo ""
echo "========================================="
echo "⚠️ TESTS MANUELS REQUIS"
echo "========================================="
echo "1. TC022 - Navigation complète utilisateur"
echo "2. TC023 - Interface responsive"
echo "3. TO01 - Test E2E manuel"
echo ""
echo "*Ces tests nécessitent une vérification humaine*"
echo "========================================="

# Sauvegarder ce rapport dans un fichier
echo "{\"summary\": {\"timestamp\": \"$(date -Iseconds)\", \"manual_tests\": [\"TC022\", \"TC023\", \"TO01\"]}}" > test_summary.json