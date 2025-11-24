#!/bin/bash

# Liste des versions de Python à tester
PYTHON_VERSIONS=("3.13" "3.9" "2.7")

# Liste des versions de Django à tester
DJANGO_VERSIONS=("5.0" "4.2" "3.2")

# Répertoire pour stocker les rapports
REPORT_DIR="test_reports"
mkdir -p "$REPORT_DIR"

for PY in "${PYTHON_VERSIONS[@]}"; do
    for DJ in "${DJANGO_VERSIONS[@]}"; do
        echo "=============================="
        echo "Testing with Python $PY and Django $DJ"
        echo "=============================="

        # Nom unique pour chaque environnement de test
        ENV_NAME="py${PY}_dj${DJ//./}"

        # Crée un environnement pipenv pour cette version de Python
        pipenv --python $PY --rm >/dev/null 2>&1 || true
        pipenv --python $PY install >/dev/null

        # Installe la version spécifique de Django
        pipenv install "django==$DJ" >/dev/null

        # Installe les dépendances du projet si requirements.txt existe
        if [ -f "requirements.txt" ]; then
            pipenv install -r requirements.txt >/dev/null
        fi

        # Lance les tests avec coverage
        REPORT_FILE="$REPORT_DIR/report_${ENV_NAME}.txt"
        COVERAGE_FILE="$REPORT_DIR/coverage_${ENV_NAME}.xml"

        echo "Running tests..." | tee -a "$REPORT_FILE"
        pipenv run coverage run --source=tasks manage.py test tasks 2>&1 | tee -a "$REPORT_FILE"
        pipenv run coverage xml -o "$COVERAGE_FILE"

        echo "Test report saved: $REPORT_FILE"
        echo "Coverage XML saved: $COVERAGE_FILE"
        echo "------------------------------"

        # Nettoyage optionnel
        pipenv --rm >/dev/null 2>&1
    done
done

echo "All tests completed. Reports are in $REPORT_DIR"
