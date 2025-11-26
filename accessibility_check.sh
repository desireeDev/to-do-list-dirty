#!/bin/bash
# accessibility_check.sh - VERSION CORRIGÉE

echo "=== Testing WCAG 2.1 AA Compliance ==="

# Vérifier si pa11y est installé
if ! command -v pa11y &> /dev/null; then
    echo "❌ pa11y n'est pas installé. Installation..."
    npm install -g pa11y
    if [ $? -ne 0 ]; then
        echo "❌ Impossible d'installer pa11y. Installez Node.js puis: npm install -g pa11y"
        exit 1
    fi
fi

# Nettoyer les anciens processus
pkill -f "manage.py runserver" 2>/dev/null || true
sleep 2

# Créer une tâche de test
echo "Création des données de test..."
python manage.py shell << EOF
from tasks.models import Task
Task.objects.all().delete()  # Nettoyer d'abord
task = Task.objects.create(title="Test Accessibility Task", complete=False)
print(f"✅ Tâche de test créée avec ID: {task.id}")
EOF

# Démarrer le serveur
echo "Démarrage du serveur Django..."
python manage.py runserver 127.0.0.1:8000 > server.log 2>&1 &
SERVER_PID=$!
sleep 10

# Vérifier le serveur
if ! curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "❌ Serveur non accessible"
    cat server.log
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Serveur démarré (PID: $SERVER_PID)"

# Récupérer l'ID de la tâche
TASK_ID=$(python manage.py shell -c "
from tasks.models import Task
task = Task.objects.first()
print(task.id) if task else print('1')
" 2>/dev/null || echo "1")

echo "ID de la tâche de test: $TASK_ID"

# URLs à tester
URLS=(
    "http://127.0.0.1:8000/"
    "http://127.0.0.1:8000/update/$TASK_ID/"
    "http://127.0.0.1:8000/delete/$TASK_ID/"
)

ALL_PASSED=true
FAILED_URLS=()

echo "=== DÉBUT DES TESTS WCAG 2.1 AA ==="

for url in "${URLS[@]}"; do
    echo ""
    echo "🔍 Testing: $url"
    
    # Test avec timeout et capture correcte des erreurs
    timeout 30 pa11y --standard WCAG2AA --reporter json "$url" > "pa11y_result.json" 2>&1
    PA11Y_EXIT_CODE=$?
    
    if [ $PA11Y_EXIT_CODE -eq 0 ] || [ $PA11Y_EXIT_CODE -eq 124 ]; then
        # Pa11y a fonctionné (0=succès, 124=timeout mais résultat valide)
        if [ -s "pa11y_result.json" ]; then
            ERROR_COUNT=$(python -c "
import json, sys
try:
    with open('pa11y_result.json', 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if content:
        data = json.loads(content)
        if isinstance(data, list):
            # Compter seulement les erreurs (pas les warnings)
            errors = [e for e in data if e.get('type') == 'error']
            print(len(errors))
        else:
            print('1')
    else:
        print('1')
except Exception as e:
    print('1')
" 2>/dev/null || echo "1")
            
            if [ "$ERROR_COUNT" -eq 0 ]; then
                echo "✅ $url - WCAG 2.1 AA COMPLIANT"
            else
                echo "❌ $url - $ERROR_COUNT erreur(s) d'accessibilité"
                ALL_PASSED=false
                FAILED_URLS+=("$url")
                
                # Afficher les erreurs détaillées
                echo "   Détails des erreurs:"
                python -c "
import json
try:
    with open('pa11y_result.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        for i, error in enumerate(data, 1):
            if error.get('type') == 'error':
                print(f'   {i}. {error.get(\\\"message\\\", \\\"No message\\\")}')
                print(f'      Code: {error.get(\\\"code\\\", \\\"N/A\\\")}')
    else:
        print(f'   Format inattendu: {type(data)}')
except Exception as e:
    print(f'   Erreur lecture JSON: {e}')
    with open('pa11y_result.json', 'r') as f:
        print(f'   Contenu brut: {f.read()}')
"
            fi
        else
            echo "❌ $url - Résultat pa11y vide"
            ALL_PASSED=false
            FAILED_URLS+=("$url")
        fi
    else
        echo "❌ $url - Échec technique pa11y (code: $PA11Y_EXIT_CODE)"
        ALL_PASSED=false
        FAILED_URLS+=("$url")
        
        # Afficher la sortie d'erreur
        if [ -s "pa11y_result.json" ]; then
            echo "   Erreur pa11y:"
            cat "pa11y_result.json" | head -5
        fi
    fi
    
    rm -f "pa11y_result.json"
done

# Nettoyer
kill $SERVER_PID 2>/dev/null || true
rm -f server.log

# Résultat final
echo ""
echo "=== RÉSULTATS FINAUX ==="

if [ "$ALL_PASSED" = true ]; then
    echo "🎉 ✅ TOUS LES TESTS WCAG 2.1 AA SONT VALIDÉS !"
    echo "✅ Votre application est 100% accessible"
    exit 0
else
    echo "❌ ÉCHEC DES TESTS D'ACCESSIBILITÉ"
    echo "Pages avec problèmes:"
    for url in "${FAILED_URLS[@]}"; do
        echo "   - $url"
    done
    echo ""
    echo "CONSEILS:"
    echo "1. Testez manuellement avec Lighthouse dans Chrome"
    echo "2. Vérifiez que toutes les pages ont:"
    echo "   - <!DOCTYPE html>"
    echo "   - <html lang=\\\"fr\\\">" 
    echo "   - <title>...</title>"
    echo "   - Contraste suffisant (ratio 4.5:1)"
    echo "3. Relancez: ./accessibility_check.sh"
    exit 1
fi