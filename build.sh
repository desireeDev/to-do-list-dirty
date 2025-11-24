#!/bin/bash

# -----------------------------
# Script de build pour le projet Django
# -----------------------------

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./build.sh <version>"
    exit 1
fi

# Chemin correct vers settings.py
SETTINGS_FILE="todo/settings.py"

# Vérifie que settings.py existe
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Erreur: $SETTINGS_FILE non trouvé !"
    
    exit 1
fi

# Met à jour la version dans settings.py
sed -i "s/^VERSION = .*/VERSION = \"$VERSION\"/" "$SETTINGS_FILE"

# Commit le changement (commit vide si version identique)
git add "$SETTINGS_FILE"
git commit -m "chore: bump version to $VERSION" --allow-empty

# Mise à jour du changelog si présent
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- Description des changements ici\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION" --allow-empty
fi

# Tag Git avec vérification si le tag existe déjà
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Le tag v$VERSION existe déjà, utilisation du tag existant."
else
    git tag -a "v$VERSION" -m "Version $VERSION"
    git push origin "v$VERSION"
fi

# Génère l’archive .zip
# Exclut .git et fichiers compilés Python
if command -v zip >/dev/null 2>&1; then
    zip -r "todolist-$VERSION.zip" todo tasks manage.py -x "*.pyc" "__pycache__/*" ".git/*"
    echo "Archive générée : todolist-$VERSION.zip"
else
    echo "Attention : zip n'est pas installé, l'archive n'a pas été créée."
fi

# Affiche un résumé
echo "-------------------------"
echo "Build terminé pour la version $VERSION"
git log -1 --oneline
echo "-------------------------"
