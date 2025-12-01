# Exercices 13 & 14 - TDD et ATDD

## TDD (Test-Driven Development) - Développement Piloté par les Tests

**Définition** : Approche de développement où on écrit les tests **unitaire** avant d'écrire le code de production.

**Cycle TDD (Red-Green-Refactor)** :
1. **RED** : Écrire un test qui échoue (car le code n'existe pas encore)
2. **GREEN** : Écrire le code minimal pour faire passer le test
3. **REFACTOR** : Améliorer le code tout en gardant les tests verts

**Caractéristiques TDD** :
- Niveau **développeur**
- Tests **unitaires** (une fonction/méthode)
- Focus sur la **qualité technique** du code
- Exemple : Les tests TP001-TP010 que nous avons créés pour la priorité

## ATDD (Acceptance Test-Driven Development) - Développement Piloté par les Tests d'Acceptation

**Définition** : Approche où on écrit les tests **d'acceptation** avant le développement, en collaboration avec le client.

**Cycle ATDD** :
1. **Collaboration** : Client, développeurs et testeurs définissent les critères d'acceptation
2. **Spécification** : Écrire les tests d'acceptation (souvent en Gherkin)
3. **Développement** : Implémenter pour passer les tests
4. **Validation** : Client valide que le besoin est satisfait

**Caractéristiques ATDD** :
- Niveau **fonctionnel/business**
- Tests **d'acceptation** (scénarios utilisateur)
- Collaboration avec les **parties prenantes** (client, PO, etc.)
- Focus sur la **bonne fonctionnalité** (le "quoi" plus que le "comment")
- Langage souvent en **Gherkin** (Given-When-Then)

## Différences Clés

| Aspect | TDD | ATDD |
|--------|-----|------|
| **Objectif** | Code de qualité | Bonne fonctionnalité |
| **Niveau** | Unitaire (détail) | Acceptation (fonctionnel) |
| **Qui écrit** | Développeurs | Équipe + Client |
| **Quand** | Avant chaque fonction | Avant chaque feature |
| **Format** | Code (Python/Java) | Langage naturel (Gherkin) |
| **Focus** | Comment ça marche | Ce que ça doit faire |

## Exemple concret dans notre projet

### TDD (Exercice 15) :
```python
# Test unitaire écrit AVANT le code
def test_create_task_with_priority_field(self):
    task = Task(title="Test")
    self.assertTrue(hasattr(task, 'priority'))