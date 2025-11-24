
# To-Do List App

Une application **To-Do List** développée avec **Django**, permettant de **créer, mettre à jour et supprimer des tâches** facilement.

<br>

![todolist](https://user-images.githubusercontent.com/65074901/125083144-a5e03900-e0e5-11eb-9092-da716a30a5f3.JPG)

---

## Fonctionnalités

* Créer de nouvelles tâches.
* Mettre à jour les tâches existantes.
* Supprimer des tâches.
* Visualiser toutes les tâches dans une interface simple et intuitive.
* Support pour l’importation de jeux de données (`dataset.json`) pour initialiser la base.

---

## Gestion des commits et des versions

Nous utilisons :

* **Conventional Commits** pour nommer nos commits : chaque commit doit refléter clairement la nature du changement (feat, fix, chore, docs, etc.).
* **Versioning sémantique (SemVer)** pour numéroter les versions du projet.
* Les **tags Git** sont utilisés pour identifier les versions publiées.

**Exemple :**

```bash
git commit -m "feat: ajouter la fonctionnalité de suppression des tâches"
git tag -a "v1.2.0" -m "Version 1.2.0"
```

Cela permet de suivre clairement l’évolution du projet et de générer automatiquement les changelogs si nécessaire.

---

## Tests

* Les tests unitaires et fonctionnels couvrent :

  * Les routes principales (`/`, `/update_task/<id>`, `/delete/<id>`).
  * Les opérations POST pour la création, la mise à jour et la suppression de tâches.
  * L’importation du dataset JSON.
* Un script est disponible pour tester le projet sous différentes versions de Python et de Django.

---

## Installation

1. Cloner le projet :

```bash
git clone <url_du_projet>
cd to-do-list
```

2. Installer les dépendances avec **Pipenv** :

```bash
pipenv install
pipenv shell
```

3. Appliquer les migrations :

```bash
python manage.py migrate
```

4. Lancer le serveur :

```bash
python manage.py runserver
```

5. Accéder à l’application via `http://127.0.0.1:8000/`.



