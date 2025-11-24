#!/bin/bash

# Liste des versions de Python à tester
PYTHON_VERSIONS=("3.13" "3.9" "2.7")

# Liste des versions de Django à tester
DJANGO_VERSIONS=("5.0" "4.2" "3.2")

for PY in "${PYTHON_VERSIONS[@]}"; do
    for DJ in "${DJANGO_VERSIONS[@]}"; do
        echo "=============================="
        echo "Testing with Python $PY and Django $DJ"
        echo "=============================="

        # Crée un environnement pipenv pour cette version de Python
        pipenv --python $PY run pip install "django==$DJ"

        # Lance les tests
        pipenv run python manage.py test tasks

        # Nettoyage optionnel : réinitialisation de l'environnement
        echo "------------------------------"
    done
done
