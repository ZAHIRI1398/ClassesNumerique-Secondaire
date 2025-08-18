# Correction du bouton "Voir mes classes" dans le tableau de bord enseignant

## Problème identifié

Une erreur `BuildError` se produisait lors de l'accès au tableau de bord enseignant :

```
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'view_classes'. Did you mean 'view_class' instead?
```

Cette erreur était causée par une référence à un endpoint `view_classes` qui n'existe pas dans l'application. Le template `teacher/dashboard.html` contenait un lien vers cet endpoint inexistant à la ligne 14 :

```html
<a href="{{ url_for('view_classes') }}" class="btn btn-primary">Voir mes classes</a>
```

## Analyse du code

Après analyse des routes disponibles dans `app.py`, nous avons constaté que :

1. Il existe une route `view_class` (avec un ID de classe) pour voir une classe spécifique :
   ```python
   @app.route('/class/<int:class_id>/view')
   @login_required
   def view_class(class_id):
       # ...
   ```

2. Il existe une route `view_student_classes` pour les étudiants :
   ```python
   @app.route('/student/classes')
   @login_required
   def view_student_classes():
       # ...
   ```

3. Mais il n'existe pas de route `view_classes` pour les enseignants.

## Solution implémentée

Nous avons modifié le template `teacher/dashboard.html` pour utiliser la route `create_class` qui existe déjà et permet de gérer les classes :

```html
<a href="{{ url_for('create_class') }}" class="btn btn-primary">Gérer mes classes</a>
```

Cette modification permet aux enseignants d'accéder à la gestion des classes depuis le tableau de bord sans erreur.

## Résultat

- ✅ Le tableau de bord enseignant s'affiche correctement
- ✅ Le bouton "Gérer mes classes" fonctionne et redirige vers la page de création/gestion des classes
- ✅ Plus d'erreur BuildError lors de l'accès au tableau de bord

## Recommandation

Pour une meilleure expérience utilisateur, il serait recommandé de créer une route dédiée `view_teacher_classes` qui afficherait la liste des classes de l'enseignant, similaire à `view_student_classes` pour les étudiants.
