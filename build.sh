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

# 1️⃣ Linter + tests + coverage avant la version
echo "=== Lancement du linter ==="
pipenv run flake8 tasks manage.py || exit 1

echo "=== Lancement des tests Django ==="
pipenv run python manage.py test tasks || exit 1

echo "=== Lancement de la couverture de tests ==="
pipenv run coverage run --source='tasks' manage.py test tasks || exit 1
pipenv run coverage report
pipenv run coverage html

# 2️⃣ Met à jour la version dans settings.py
SETTINGS_FILE="todo/settings.py"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Erreur: $SETTINGS_FILE non trouvé !"
    exit 1
fi

sed -i "s/^VERSION = .*/VERSION = \"$VERSION\"/" "$SETTINGS_FILE"

git add "$SETTINGS_FILE"
git commit -m "chore: bump version to $VERSION" --allow-empty

# 3️⃣ Mise à jour du changelog si présent
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- Description des changements ici\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION" --allow-empty
fi

# 4️⃣ Tag Git
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Le tag v$VERSION existe déjà, utilisation du tag existant."
else
    git tag -a "v$VERSION" -m "Version $VERSION"
    git push origin "v$VERSION"
fi

# 5️⃣ Génère l’archive .zip
if command -v zip >/dev/null 2>&1; then
    zip -r "todolist-$VERSION.zip" todo tasks manage.py -x "*.pyc" "__pycache__/*" ".git/*"
    echo "Archive générée : todolist-$VERSION.zip"
else
    echo "Erreur : zip n'est pas installé, l'archive n'a pas été créée."
    exit 1
fi

echo "-------------------------"
echo "Build terminé pour la version $VERSION"
git log -1 --oneline
echo "-------------------------"
