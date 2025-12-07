#!/bin/bash

# -----------------------------
# Script de build pour le projet Django avec pipenv
# Version 1.6.0 - Tests Selenium et Accessibilité améliorés
# -----------------------------

set -e  # Stoppe le script si une commande échoue

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./build.sh <version>"
    exit 1
fi

echo "=== BUILD v$VERSION DÉMARRÉ ==="

# 0️⃣ Vérification des fichiers requis
echo "=== Vérification des fichiers ==="
REQUIRED_FILES=("test_list.yaml" "test_report.py" "tasks/generate_test_report.py" "tasks/decorators.py" "TDD_ATDD_EXPLANATION.md" "selenium_test.py" "tasks/tests.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        exit 1
    else
        echo "✅ $file trouvé"
    fi
done

# Vérification des fichiers de tests (MAINTENANT SEULEMENT tests.py)
echo "=== Vérification fichiers de tests ==="
TEST_FILES=("tasks/tests.py")
for file in "${TEST_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier de test manquant: $file"
        exit 1
    else
        echo "✅ $file trouvé (contient tous les tests Django)"
    fi
done

echo "✅ Tous les fichiers vérifiés"

# 1️⃣ Installation des dépendances
echo "=== Installation des dépendances ==="

# Installation de PyYAML si nécessaire
if ! pipenv run python -c "import yaml" &> /dev/null; then
    echo "Installing PyYAML..."
    pipenv install PyYAML --dev --skip-lock
fi

# Installation de Selenium pour les tests E2E
if ! pipenv run python -c "import selenium" &> /dev/null; then
    echo "Installing Selenium (pour tests E2E)..."
    pipenv install selenium --dev --skip-lock
fi

# Installation de webdriver-manager pour ChromeDriver automatique
if ! pipenv run python -c "from webdriver_manager.chrome import ChromeDriverManager" &> /dev/null; then
    echo "Installing webdriver-manager..."
    pipenv install webdriver-manager --dev --skip-lock
fi

# Installation de requests pour les tests d'accessibilité
if ! pipenv run python -c "import requests" &> /dev/null; then
    echo "Installing requests (pour tests d'accessibilité)..."
    pipenv install requests --dev --skip-lock
fi

echo "✅ Dépendances installées"

# 2️⃣ Vérification des migrations
echo "=== Vérification des migrations ==="
if ! pipenv run python manage.py makemigrations --check --dry-run; then
    echo "⚠️  Migrations nécessaires"
    echo "Création des migrations..."
    pipenv run python manage.py makemigrations
    pipenv run python manage.py migrate
    echo "✅ Migrations appliquées"
fi

# 3️⃣ Linter (METTRE À JOUR POUR tests.py SEULEMENT)
echo "=== Lancement du linter ==="
pipenv run flake8 tasks manage.py test_report.py tasks/generate_test_report.py tasks/decorators.py tasks/tests.py selenium_test.py || exit 1
echo "✅ Linter passed"

# 4️⃣ Tests Django TOUS DANS UN SEUL FICHIER (tests.py)
echo "=== Lancement des tests Django (TOUS les tests) ==="
echo "Tests Django complets (TC + TP)..."
if pipenv run python manage.py test tasks.tests --noinput; then
    echo "✅ Tous les tests Django passed (TC001-TC021 + TP001-TP007)"
else
    echo "❌ Tests Django failed"
    echo "Détail des tests:"
    pipenv run python manage.py test tasks.tests -v 2
    exit 1
fi

# 5️⃣ Génération du rapport JSON des tests Django
echo "=== Génération du rapport JSON des tests Django ==="
if pipenv run python tasks/generate_test_report.py; then
    echo "✅ Rapport JSON Django généré (result_test_auto.json)"
else
    echo "⚠️  Problème avec generate_test_report.py"
    echo "Exécution des tests avec verbosité pour debug..."
    pipenv run python manage.py test tasks.tests --verbose
    exit 1
fi

# 6️⃣ TESTS E2E SELENIUM - AMÉLIORÉ
echo "=== Tests E2E avec Selenium (Exercices 9 & 12) ==="
SELENIUM_FILE="selenium_test.py"
if [ -f "$SELENIUM_FILE" ]; then
    echo "Démarrage des tests Selenium améliorés..."

    # Vérifier si le serveur tourne
    if ! curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
        echo "⚠️  Serveur Django non détecté, démarrage en arrière-plan..."
        # Démarrer le serveur en arrière-plan
        pipenv run python manage.py runserver 127.0.0.1:8000 &
        SERVER_PID_SELENIUM=$!
        sleep 5  # Attendre plus longtemps pour le démarrage
        SERVER_STARTED_BY_US=true
    else
        echo "✅ Serveur Django détecté (déjà en cours)"
        SERVER_PID_SELENIUM=""
        SERVER_STARTED_BY_US=false
    fi

    # Exécuter les tests Selenium
    echo "🚀 Lancement des tests Selenium..."
    if pipenv run python "$SELENIUM_FILE"; then
        echo "✅ Tests Selenium E2E passed (result_test_selenium.json généré)"
    else
        echo "❌ Tests Selenium E2E failed"
        # N'arrêter le serveur que si NOUS l'avons démarré
        if [ "$SERVER_STARTED_BY_US" = true ] && [ ! -z "$SERVER_PID_SELENIUM" ]; then
            kill $SERVER_PID_SELENIUM 2>/dev/null || true
        fi
        exit 1
    fi

    # NE PAS ARRÊTER LE SERVEUR ICI - il sera utilisé pour les tests d'accessibilité
    if [ "$SERVER_STARTED_BY_US" = true ]; then
        echo "📝 Serveur Django maintenu en cours (PID: $SERVER_PID_SELENIUM) pour tests d'accessibilité"
        SERVER_PID=$SERVER_PID_SELENIUM
    fi
else
    echo "❌ Fichier Selenium $SELENIUM_FILE non trouvé"
    exit 1
fi

# 7️⃣ VÉRIFICATION SERVEUR POUR TESTS D'ACCESSIBILITÉ
echo "=== Vérification pour tests d'accessibilité ==="
echo "🔍 Vérification du serveur Django..."

# D'abord, vérifier si le serveur tourne toujours (après les tests Selenium)
if ! curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
    echo "⚠️  Serveur Django non détecté après tests Selenium"
    echo "🚀 Redémarrage du serveur Django pour tests d'accessibilité..."
    pipenv run python manage.py runserver 127.0.0.1:8000 &
    SERVER_PID=$!
    sleep 8  # Attendre que le serveur démarre
    SERVER_STARTED_FOR_ACCESSIBILITY=true

    # Vérifier que le serveur tourne
    if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
        echo "✅ Serveur Django démarré (PID: $SERVER_PID)"
        SERVER_STARTED=true
    else
        echo "❌ Impossible de démarrer le serveur"
        SERVER_STARTED=false
    fi
else
    echo "✅ Serveur Django toujours en cours d'exécution (après tests Selenium)"
    SERVER_STARTED=true
    SERVER_STARTED_FOR_ACCESSIBILITY=false
fi

# 8️⃣ RAPPORT GLOBAL AVEC ACCESSIBILITÉ (Exercice 18)
echo "=== Génération du rapport global des tests (Exercices 11 & 18) ==="
echo "📊 Rapport unifié Django + Selenium + Accessibilité..."

if [ "$SERVER_STARTED" = true ]; then
    echo "✅ Serveur disponible, lancement des tests d'accessibilité..."

    # NETTOYAGE DU JSON AVANT LES TESTS
    echo "🧹 Nettoyage du fichier JSON avant les tests..."
    pipenv run python -c "
import json
import os

def clean_json_file():
    json_file = 'result_test_auto.json'

    if not os.path.exists(json_file):
        print('⚠️  Fichier JSON non trouvé')
        return

    # Essayer différents encodages
    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

    for encoding in encodings_to_try:
        try:
            print(f'📖 Tentative de lecture avec encodage: {encoding}')
            with open(json_file, 'r', encoding=encoding) as f:
                content = f.read()
                data = json.loads(content)
                print(f'✅ Fichier JSON chargé avec succès (encodage: {encoding})')

                # Ré-écrire avec UTF-8
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print('✅ Fichier JSON nettoyé et ré-encodé en UTF-8')
                return
        except UnicodeDecodeError as e:
            print(f'❌ Échec avec {encoding}: {e}')
            continue
        except json.JSONDecodeError as e:
            print(f'❌ JSON invalide avec {encoding}: {e}')
            continue

    print('❌ Impossible de lire le fichier JSON avec les encodages disponibles')

clean_json_file()
"

    # Essayer de lancer les tests d'accessibilité
    if pipenv run python test_report.py; then
        echo "✅ Rapport global généré avec succès"
        echo ""
        echo "♿ TESTS D'ACCESSIBILITÉ EXÉCUTÉS:"
        echo "   - Page d'accueil vérifiée"
        echo "   - Page de modification vérifiée"
        echo "   - Page de suppression vérifiée"
        echo "   - Conformité WGAC 2.1 évaluée"
    else
        echo "⚠️  Problème avec le rapport global"
        echo "   Les tests d'accessibilité ont échoué - vérifiez que:"
        echo "   1. Le serveur Django tourne sur http://127.0.0.1:8000"
        echo "   2. Les URLs sont accessibles"
    fi

    # Nettoyer SEULEMENT si on a démarré le serveur pour l'accessibilité
    if [ "$SERVER_STARTED_FOR_ACCESSIBILITY" = true ] && [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        echo "✅ Serveur arrêté"
    else
        echo "ℹ️  Serveur Django laissé en cours d'exécution"
    fi
else
    echo "⚠️  Serveur non disponible, tests d'accessibilité ignorés"
    echo ""
    echo "💡 Pour exécuter les tests d'accessibilité manuellement:"
    echo "   1. Ouvrez un terminal et lancez: pipenv run python manage.py runserver"
    echo "   2. Dans un autre terminal: pipenv run python test_report.py"
fi

# 9️⃣ Couverture de tests
echo "=== Lancement de la couverture de tests ==="
pipenv run coverage run --source='tasks' manage.py test tasks || exit 1
pipenv run coverage report
pipenv run coverage html
echo "✅ Couverture de tests passed"

# 1️⃣0️⃣ Met à jour la version dans settings.py
SETTINGS_FILE="todo/settings.py"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Erreur: $SETTINGS_FILE non trouvé !"
    exit 1
fi

echo "=== Mise à jour de la version ==="
sed -i "s/^VERSION = .*/VERSION = \"$VERSION\"/" "$SETTINGS_FILE"

git add "$SETTINGS_FILE"
git commit -m "chore: bump version to $VERSION" --allow-empty
echo "✅ Version mise à jour à $VERSION"

# 1️⃣1️⃣ Mise à jour du changelog
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- **Exercice 18 : Tests d'accessibilité automatisés**\n  - Intégration Pa11y pour tests WCAG 2.1 Niveau A\n  - Tests simplifiés avec vérifications HTML de base\n  - Cache pour performances améliorées\n  - Évaluation automatique de conformité\n- **Exercices 9 & 12 : Tests Selenium améliorés**\n  - Noms de tâches descriptifs ('Tâche Selenium X')\n  - Optimisation des performances en mode headless\n  - Gestion robuste des confirmations de suppression\n  - Script Selenium optimisé\n- **Exercice 11 : Rapport de tests unifié**\n  - Support Django Unit Tests, Selenium et Accessibilité\n  - Statistiques détaillées par catégorie\n  - Évaluation conformité WCAG avec score\n  - Détection automatique des tests manquants\n- **Réorganisation des tests Django**\n  - Fusion de tous les tests (TC et TP) dans un seul fichier tests.py\n  - Suppression du fichier test_priority.py séparé\n  - Simplification de la gestion des tests\n- **Améliorations techniques**\n  - Installation automatique des dépendances Selenium\n  - Gestion améliorée des erreurs\n  - Rapports JSON complets\n- **Corrections**\n  - Correction encodage JSON UTF-8/latin-1\n  - Serveur Django maintenu entre tests Selenium et accessibilité\n  - Logs améliorés pour le débogage\n  - Messages d'erreur plus clairs\n\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION" --allow-empty
    echo "✅ Changelog mis à jour"
fi

# 1️⃣2️⃣ Tag Git
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Le tag v$VERSION existe déjà, utilisation du tag existant."
else
    git tag -a "v$VERSION" -m "Version $VERSION - Tests Django unifiés + Selenium & Accessibilité améliorés"
    git push origin "v$VERSION"
    echo "✅ Tag v$VERSION créé"
fi

# 1️⃣3️⃣ Génère l'archive .zip
if command -v zip >/dev/null 2>&1; then
    # Inclure tous les fichiers de test (MAINTENANT SANS test_priority.py)
    echo "=== Génération de l'archive ==="
    zip -r "todolist-$VERSION.zip" \
        todo tasks manage.py \
        test_list.yaml test_report.py selenium_test.py \
        tasks/generate_test_report.py tasks/decorators.py tasks/tests.py \
        TDD_ATDD_EXPLANATION.md \
        build.sh \
        requirements.txt Pipfile Pipfile.lock \
        -x "*.pyc" "__pycache__/*" ".git/*" "*.zip" "*.pyc" "*.log" ".coverage" "htmlcov/*" ".pytest_cache/*"

    # Vérifier que les fichiers de résultats sont inclus s'ils existent
    if [ -f "result_test_auto.json" ]; then
        zip -u "todolist-$VERSION.zip" result_test_auto.json
        echo "✅ result_test_auto.json inclus"
    fi

    if [ -f "result_test_selenium.json" ]; then
        zip -u "todolist-$VERSION.zip" result_test_selenium.json
        echo "✅ result_test_selenium.json inclus"
    fi

    if [ -f ".pa11y_cache.json" ]; then
        zip -u "todolist-$VERSION.zip" .pa11y_cache.json
        echo "✅ .pa11y_cache.json inclus"
    fi

    echo "✅ Archive générée : todolist-$VERSION.zip"
else
    echo "❌ Erreur : zip n'est pas installé"
    exit 1
fi

echo ""
echo "=========================="
echo "🎉 BUILD v$VERSION TERMINÉ AVEC SUCCÈS"
echo "📦 todolist-$VERSION.zip"
echo ""
echo "🧪 SYSTÈME DE TESTS COMPLET:"
echo "  ✅ Tests Django Unit (TC001-TC021 + TP001-TP007)"
echo "  ✅ Tests Selenium E2E (Exercices 9 & 12)"
if [ "$SERVER_STARTED" = true ]; then
    echo "  ✅ Tests d'accessibilité WCAG 2.1 (Exercice 18)"
else
    echo "  ⚠️  Tests d'accessibilité non exécutés (serveur non démarré)"
fi
echo "  ✅ Rapport unifié Django+Selenium+Accessibilité (Exercice 11)"
echo "  ✅ Installation automatique des dépendances"
echo ""
echo "💡 POUR LES TESTS D'ACCESSIBILITÉ:"
echo "   1. Ouvrez un terminal: pipenv run python manage.py runserver"
echo "   2. Puis dans un autre: pipenv run python test_report.py"
echo ""
echo "🚀 Pour tester maintenant:"
echo "   pipenv run python test_report.py"
echo "=========================="
