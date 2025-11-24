#!/bin/bash

# -----------------------------
# Script de build pour le projet Django
# -----------------------------

# Récupère la version depuis le paramètre
VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./build.sh 1.0.1"
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

# Commit le changement
git add "$SETTINGS_FILE"
git commit -m "chore: bump version to $VERSION"

# Optionnel: mise à jour du changelog si présent
if [ -f "CHANGELOG.md" ]; then
    echo -e "## Version $VERSION - $(date +%Y-%m-%d)\n- Description des changements ici\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "docs: update changelog for $VERSION"
fi

# Tag Git avec préfixe v
git tag -a "v$VERSION" -m "Version $VERSION"
git push origin "v$VERSION"

# Génère l’archive .zip
# Exclut .git et fichiers .pyc
zip -r "todolist-$VERSION.zip" todo tasks manage.py -x "*.pyc" "__pycache__/*" ".git/*"

# Affiche un résumé
echo "-------------------------"
echo "Build terminé pour la version $VERSION"
git log -1 --oneline
echo "Archive générée : todolist-$VERSION.zip"
echo "-------------------------"
