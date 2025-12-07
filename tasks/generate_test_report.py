#!/usr/bin/env python3
"""
Script pour exécuter les tests Django et générer result_test_auto.json
Inclut tests fonctionnels (TC), priorité (TP) et tests manuels.
"""

import json
import subprocess
import sys
import os
import re


def run_django_tests():
    """Exécute les tests Django et génère un rapport JSON."""

    print("🚀 Exécution des tests Django...")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manage_py = os.path.join(project_root, 'manage.py')

    if not os.path.exists(manage_py):
        print("❌ manage.py non trouvé")
        sys.exit(1)

    # Utiliser verbosity=3 pour afficher tous les tests
    cmd = [
        sys.executable, manage_py, 'test', 'tasks.tests',
        '--noinput', '--verbosity=3'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

    print("📊 Analyse des résultats...")

    test_results = {}

    # Mapping de tous les tests (TC + TP)
    test_mapping = {
        # Tests fonctionnels
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
        'test_pa11y_available': 'TC021',

        # Tests priorité
        'test_create_task_with_priority_field': 'TP001',
        'test_priority_default_value_is_false': 'TP002',
        'test_create_priority_task': 'TP003',
        'test_task_form_includes_priority_field': 'TP004',
        'test_priority_in_create_view': 'TP005',
        'test_tasks_ordered_by_priority': 'TP006',
        'test_priority_display_in_template': 'TP007'
    }

    full_output = result.stdout + result.stderr

    # Regex pour détecter tous les tests
    test_pattern = re.compile(
        r'(\w+)\.(test_\w+)\s+\([^)]+\)\s+\.\.\.\s+(ok|FAIL|ERROR|skipped|SKIP)',
        re.IGNORECASE
    )

    for match in test_pattern.finditer(full_output):
        # Ex: TestTask
        test_method = match.group(2)          # Ex: test_01_index_get
        status_raw = match.group(3).lower()   # ok, fail, error, skipped

        if test_method in test_mapping:
            test_id = test_mapping[test_method]

            # Normaliser le statut
            if status_raw == 'ok':
                status = 'passed'
            elif status_raw == 'fail':
                status = 'failed'
            elif status_raw == 'error':
                status = 'error'
            elif status_raw in ['skipped', 'skip']:
                status = 'skipped'
            else:
                status = 'unknown'

            test_results[test_id] = {
                'status': status,
                'test_method': test_method,
                'output': match.group(0)[:200]
            }

    # Fallback parsing ligne par ligne si regex échoue
    if not test_results:
        print("⚠️ Regex n'a rien trouvé")
        lines = full_output.split('\n')
        for line in lines:
            line_lower = line.lower()
            for test_method, test_id in test_mapping.items():
                if test_method.lower() in line_lower and test_id not in test_results:
                    if any(word in line_lower for word in ['ok', '...', 'pass']):
                        status = 'passed'
                    elif 'fail' in line_lower:
                        status = 'failed'
                    elif 'error' in line_lower:
                        status = 'error'
                    elif 'skip' in line_lower:
                        status = 'skipped'
                    else:
                        status = 'passed'
                    test_results[test_id] = {
                        'status': status,
                        'test_method': test_method,
                        'output': line.strip()[:200]
                    }

    # Si toujours rien, utiliser le code retour
    if not test_results:
        if result.returncode == 0:
            for test_id in test_mapping.values():
                test_results[test_id] = {
                    'status': 'passed',
                    'note': 'Détecté via code retour 0'
                }
        else:
            print("❌ Aucun test détecté et code retour non nul")
            print(full_output)
            sys.exit(1)

    # Ajouter tests manuels
    test_results['TC022'] = {'status': 'manual', 'note': 'Test manuel requis'}
    test_results['TC023'] = {'status': 'manual', 'note': 'Test visuel requis'}

    # Écriture du JSON
    output_file = os.path.join(project_root, 'result_test_auto.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    # Statistiques
    passed = sum(1 for r in test_results.values() if r.get('status') == 'passed')
    failed = sum(1 for r in test_results.values() if r.get('status') == 'failed')
    skipped = sum(1 for r in test_results.values() if r.get('status') == 'skipped')
    manual = sum(1 for r in test_results.values() if r.get('status') == 'manual')
    detected = len(test_results) - 2  # exclut manuels

    print("\n📈 RÉSUMÉ:")
    print(f"   ✅ Tests passés: {passed}")
    print(f"   ❌ Tests échoués: {failed}")
    print(f"   ⚠️ Tests skipped: {skipped}")
    print(f"   🔍 Tests détectés: {detected}")
    print(f"   👤 Tests manuels: {manual}")
    print(f"   📁 Rapport JSON: {output_file}")

    return test_results


if __name__ == '__main__':
    run_django_tests()
