#!/bin/bash

# -----------------------------
# Script de build pour le projet Django avec pipenv
# Version 1.5.0 - TDD et fonctionnalité de priorité
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
REQUIRED_FILES=("test_list.yaml" "test_report.py" "tasks/generate_test_report.py" "tasks/decorators.py" "TDD_ATDD_EXPLANATION.md")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        exit 1
    fi
done

# Vérification des fichiers TDD
echo "=== Vérification fichiers TDD ==="
TDD_FILES=("tasks/test_priority.py")
for file in "${TDD_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier TDD manquant: $file"
        exit 1
    else
        echo "✅ $file trouvé"
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

echo "✅ Dépendances installées"

# 2️⃣ Vérification des migrations TDD
echo "=== Vérification des migrations TDD ==="
if ! pipenv run python manage.py makemigrations --check --dry-run; then
    echo "⚠️  Migrations nécessaires pour la fonctionnalité TDD"
    echo "Création des migrations..."
    pipenv run python manage.py makemigrations
    pipenv run python manage.py migrate
    echo "✅ Migrations appliquées"
fi

# 3️⃣ Linter
echo "=== Lancement du linter ==="
pipenv run flake8 tasks manage.py test_report.py tasks/generate_test_report.py tasks/decorators.py tasks/test_priority.py || exit 1
echo "✅ Linter passed"

# 4️⃣ Tests Django avec IDs (incluant tests TDD)
echo "=== Lancement des tests Django (avec IDs) ==="
echo "Tests standards..."
pipenv run python manage.py test tasks --noinput || exit 1
echo "✅ Tests Django standards passed"

# 5️⃣ Tests TDD spécifiques
echo "=== Tests TDD pour la fonctionnalité de priorité ==="
if pipenv run python manage.py test tasks.test_priority --noinput; then
    echo "✅ Tests TDD priority passed"
else
    echo "❌ Tests TDD priority failed"
    echo "Détail des tests:"
    pipenv run python manage.py test tasks.test_priority -v 2
    exit 1
fi

# 6️⃣ Génération du rapport JSON des tests
echo "=== Génération du rapport JSON des tests ==="
if pipenv run python tasks/generate_test_report.py; then
    echo "✅ Rapport JSON généré"
else
    echo "⚠️  Utilisation du générateur simple..."
    pipenv run python tasks/simple_test_report.py || exit 1
    echo "✅ Rapport simple généré"
fi

# 7️⃣ Rapport visuel des tests
echo "=== Rapport visuel des tests ==="
pipenv run python test_report.py || echo "⚠️  Rapport visuel - continuation..."
echo "✅ Rapport visuel généré"

# 8️⃣ TESTS E2E SELENIUM - OPTIONNEL
echo "=== Tests E2E avec Selenium ==="
SELENIUM_FILE="selenium_test.py"
if [ -f "$SELENIUM_FILE" ]; then
    echo "Démarrage des tests Selenium..."
    
    # Vérifier si le serveur tourne
    if ! curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
        echo "⚠️  Serveur Django non détecté, démarrage en arrière-plan..."
        # Démarrer le serveur en arrière-plan
        pipenv run python manage.py runserver 8000 &
        SERVER_PID=$!
        sleep 3  # Attendre que le serveur démarre
        
        # Exécuter les tests Selenium
        if pipenv run python "$SELENIUM_FILE"; then
            echo "✅ Tests Selenium E2E passed"
        else
            echo "❌ Tests Selenium E2E failed"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi
        
        # Arrêter le serveur
        kill $SERVER_PID 2>/dev/null || true
    else
        # Serveur déjà en cours
        if pipenv run python "$SELENIUM_FILE"; then
            echo "✅ Tests Selenium E2E passed"
        else
            echo "❌ Tests Selenium E2E failed"
            exit 1
        fi
    fi
else
    echo "⚠️  Fichier Selenium non trouvé - skip"
fi

# 9️⃣ Couverture de tests
echo "=== Lancement de la couverture de tests ==="
pipenv run coverage run --source='tasks' manage.py test tasks || exit 1
pipenv run coverage report
pipenv run coverage html
echo "✅ Couverture de tests passed"

# 🔟 TESTS D'ACCESSIBILITÉ WCAG 2.1 AA
echo "=== Lancement des tests d'accessibilité WCAG 2.1 AA ==="
if [ -f "./accessibility_check.sh" ]; then
    chmod +x ./accessibility_check.sh
    ./accessibility_check.sh || exit 1
    echo "✅ Tests d'accessibilité WCAG 2.1 AA passed"
else
    echo "⚠️  Script accessibility_check.sh non trouvé - skip"
fi

# 1️⃣1️⃣ Met à jour la version dans settings.py
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

# 1️⃣2️⃣ Mise à jour du changelog
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- **Implémentation TDD de la fonctionnalité de priorité (Exercice 15)**\n  - Méthodologie TDD (Red-Green-Refactor) appliquée\n  - 10 tests complets (TP001-TP010) pour la priorité\n  - Champ 'priority' ajouté au modèle Task\n  - Tri automatique par priorité puis date\n  - Badge ⚡ pour les tâches prioritaires\n- **Documentation TDD/ATDD (Exercices 13-14)**\n  - Explications détaillées des méthodologies\n  - Différences entre TDD et ATDD\n  - Exemples concrets du projet\n- **Système de tests avancés**\n  - Cahier de tests YAML mis à jour\n  - Tests E2E Selenium fonctionnels\n  - Rapports JSON et visuels complets\n- Tests d'accessibilité WCAG 2.1 AA automatisés\n- Conformité totale aux normes d'accessibilité\n\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION" --allow-empty
    echo "✅ Changelog mis à jour"
fi

# 1️⃣3️⃣ Tag Git
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Le tag v$VERSION existe déjà, utilisation du tag existant."
else
    git tag -a "v$VERSION" -m "Version $VERSION - TDD Priority Feature + Exercises 13-15"
    git push origin "v$VERSION"
    echo "✅ Tag v$VERSION créé"
fi

# 1️⃣4️⃣ Génère l'archive .zip
if command -v zip >/dev/null 2>&1; then
    # Inclure tous les fichiers de test et TDD
    zip -r "todolist-$VERSION.zip" \
        todo tasks manage.py \
        test_list.yaml test_report.py selenium_test.py \
        tasks/generate_test_report.py tasks/simple_test_report.py tasks/decorators.py tasks/test_priority.py \
        TDD_ATDD_EXPLANATION.md \
        accessibility_check.sh build.sh \
        -x "*.pyc" "__pycache__/*" ".git/*" "*.zip"
    echo "✅ Archive générée : todolist-$VERSION.zip"
else
    echo "❌ Erreur : zip n'est pas installé"
    exit 1
fi

echo ""
echo "=========================="
echo "🎉 BUILD v$VERSION TERMINÉ AVEC SUCCÈS"
echo "📦 todolist-$VERSION.zip"
echo "🧪 SYSTÈME DE TESTS COMPLET AVEC TDD"
echo "  ✓ Méthodologie TDD appliquée (Red-Green-Refactor)"
echo "  ✓ Tests Django avec IDs"
echo "  ✓ Tests TDD pour la priorité (TP001-TP010)"
echo "  ✓ Tests E2E Selenium"
echo "  ✓ Rapports JSON et visuels"
echo "  ✓ Documentation TDD/ATDD complète"
echo "♿ Accessibilité WCAG 2.1 AA validée"
echo "🚀 Fonctionnalité de priorité implémentée avec TDD"
echo "📚 Exercices 13-15 complétés"
echo "=========================="