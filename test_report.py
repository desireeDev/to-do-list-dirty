#!/usr/bin/env python3
"""
Script de rapport de tests - Exercice 5
Lecture de test_list.yaml et result_test_auto.json.
"""

import yaml
import json
import os

def load_test_list():
    """Charge la liste des tests depuis YAML."""
    try:
        with open('test_list.yaml', 'r') as f:
            data = yaml.safe_load(f)
            return data.get('tests', {})
    except FileNotFoundError:
        print("❌ test_list.yaml non trouvé")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Erreur YAML: {e}")
        return {}

def load_test_results():
    """Charge les résultats des tests depuis JSON."""
    try:
        with open('result_test_auto.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  result_test_auto.json non trouvé")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur JSON: {e}")
        return {}

def main():
    """Génère le rapport de tests visuel."""
    
    print("Lecture des tests auto via result_test_auto.json…")
    print()
    print("OK")
    
    tests = load_test_list()
    results = load_test_results()
    
    # Affiche chaque test
    for test_id in sorted(tests.keys()):
        test_info = tests[test_id]
        test_type = test_info.get('type', 'unknown')
        
        if test_type == 'manuel':
            print(f"{test_id} | manual | 💬Manual test needed")
        
        elif test_type == 'auto-unittest':
            result = results.get(test_id, {})
            status = result.get('status', 'not_found')
            
            if status == 'passed':
                print(f"{test_id} | auto | ✔Passed")
            elif status == 'failed':
                print(f"{test_id} | auto | ✘Failed")
            else:  # not_found, error, etc.
                print(f"{test_id} | auto | 💬Not found")

if __name__ == '__main__':
    main()