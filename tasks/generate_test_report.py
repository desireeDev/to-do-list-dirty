#!/usr/bin/env python3
"""
Script pour générer result_test_auto.json à partir des tests Django.
Version simplifiée sans configuration Django compliquée.
"""

import json
import subprocess
import sys
import os

def run_django_tests():
    """Exécute les tests Django et génère un rapport JSON."""
    
    print("🚀 Exécution des tests Django...")
    
    # CHANGE : Utilise directement manage.py depuis la racine
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manage_py = os.path.join(project_root, 'manage.py')
    
    if not os.path.exists(manage_py):
        print(f"❌ manage.py non trouvé à: {manage_py}")
        sys.exit(1)
    
    # Exécute les tests Django
    result = subprocess.run(
        [sys.executable, manage_py, 'test', 'tasks', '--noinput', '--verbosity=2'],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    print("📊 Analyse des résultats...")
    
    # Parse la sortie
    test_results = {}
    lines = result.stdout.split('\n')
    
    # IDs de test
    test_mapping = {
        'test_01_index_get': 'TC001',
        'test_02_index_post_valid': 'TC002',
        'test_03_index_post_invalid': 'TC003',
        'test_04_update_task_get_valid_id': 'TC004',
        'test_05_update_task_get_invalid_id': 'TC005',
        'test_06_update_task_post_valid': 'TC006',
        'test_07_update_task_post_invalid': 'TC007',
        'test_08_delete_task_get_valid_id': 'TC008',
        'test_09_delete_task_get_invalid_id': 'TC009',
        'test_10_delete_task_post': 'TC010',
        'test_11_dataset_import': 'TC011',
        'test_12_import_dataset_script': 'TC012',
        'test_13_task_str': 'TC013',
        'test_14_task_created_field': 'TC014',
        'test_15_accessibility_homepage_semantic_structure': 'TC015',
        'test_16_accessibility_form_labels': 'TC016',
        'test_17_accessibility_aria_attributes': 'TC017',
        'test_18_accessibility_keyboard_navigation': 'TC018',
        'test_19_accessibility_update_page': 'TC019',
        'test_20_accessibility_delete_page': 'TC020',
        'test_pa11y_available': 'TC021'
    }
    
    # Initialise tous les tests
    for test_id in test_mapping.values():
        test_results[test_id] = {'status': 'not_found', 'output': 'Non exécuté'}
    
    # Analyse ligne par ligne
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Cherche les résultats
        for test_method, test_id in test_mapping.items():
            if test_method in line:
                if 'OK' in line or '...' in line or '. ' in line:
                    status = 'passed'
                elif 'FAIL' in line or 'FAILED' in line:
                    status = 'failed'
                elif 'ERROR' in line:
                    status = 'error'
                elif 'SKIP' in line or 'skipped' in line.lower():
                    status = 'skipped'
                else:
                    status = 'unknown'
                
                test_results[test_id] = {
                    'status': status,
                    'output': line[:100]
                }
                break
    
    # Ajoute les tests manuels
    test_results['TC022'] = {'status': 'manual', 'note': 'Test manuel requis'}
    test_results['TC023'] = {'status': 'manual', 'note': 'Test visuel requis'}
    
    # Sauvegarde le rapport à la racine
    output_file = os.path.join(project_root, 'result_test_auto.json')
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    # Statistiques
    passed = sum(1 for r in test_results.values() if r.get('status') == 'passed')
    failed = sum(1 for r in test_results.values() if r.get('status') == 'failed')
    manual = sum(1 for r in test_results.values() if r.get('status') == 'manual')
    not_found = sum(1 for r in test_results.values() if r.get('status') == 'not_found')
    
    print(f"\n📈 RÉSUMÉ:")
    print(f"   ✅ Tests passés: {passed}")
    print(f"   ❌ Tests échoués: {failed}")
    print(f"   🔍 Non trouvés: {not_found}")
    print(f"   👤 Tests manuels: {manual}")
    print(f"   📁 Rapport: {output_file}")
    
    return test_results

if __name__ == '__main__':
    run_django_tests()