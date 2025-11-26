#!/bin/bash

# -----------------------------
# Script de build pour le projet Django avec pipenv
# -----------------------------

set -e  # Stoppe le script si une commande échoue

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./build.sh <version>"
    exit 1
fi

echo "=== BUILD v$VERSION DÉMARRÉ ==="

# 1️⃣ Linter
echo "=== Lancement du linter ==="
pipenv run flake8 tasks manage.py || exit 1
echo "✅ Linter passed"

# 2️⃣ Tests Django
echo "=== Lancement des tests Django ==="
pipenv run python manage.py test tasks || exit 1
echo "✅ Tests Django passed"

# 3️⃣ Couverture de tests
echo "=== Lancement de la couverture de tests ==="
pipenv run coverage run --source='tasks' manage.py test tasks || exit 1
pipenv run coverage report
pipenv run coverage html
echo "✅ Couverture de tests passed"

# 4️⃣ TESTS D'ACCESSIBILITÉ WCAG 2.1 AA (NOUVEAU)
echo "=== Lancement des tests d'accessibilité WCAG 2.1 AA ==="
if [ -f "./accessibility_check.sh" ]; then
    chmod +x ./accessibility_check.sh
    ./accessibility_check.sh || exit 1
    echo "✅ Tests d'accessibilité WCAG 2.1 AA passed"
else
    echo "❌ Script accessibility_check.sh non trouvé"
    exit 1
fi

# 5️⃣ Met à jour la version dans settings.py
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

# 6️⃣ Mise à jour du changelog si présent
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- Tests d'accessibilité WCAG 2.1 AA automatisés\n- Conformité totale aux normes d'accessibilité\n- Scripts de validation automatique\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION" --allow-empty
    echo "✅ Changelog mis à jour"
fi

# 7️⃣ Tag Git
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Le tag v$VERSION existe déjà, utilisation du tag existant."
else
    git tag -a "v$VERSION" -m "Version $VERSION - Accessibilité WCAG 2.1 AA"
    git push origin "v$VERSION"
    echo "✅ Tag v$VERSION créé"
fi

# 8️⃣ Génère l'archive .zip
if command -v zip >/dev/null 2>&1; then
    # Inclure les nouveaux scripts d'accessibilité
    zip -r "todolist-$VERSION.zip" todo tasks manage.py accessibility_check.sh -x "*.pyc" "__pycache__/*" ".git/*"
    echo "✅ Archive générée : todolist-$VERSION.zip"
else
    echo "❌ Erreur : zip n'est pas installé"
    exit 1
fi

echo ""
echo "=========================="
echo "🎉 BUILD v$VERSION TERMINÉ AVEC SUCCÈS"
echo "📦 todolist-$VERSION.zip"
echo "♿ Accessibilité WCAG 2.1 AA validée"
echo "✅ Tests automatisés passés"
echo "=========================="