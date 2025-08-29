# Correction de l'affichage du contenu lors de la modification d'exercices image_labeling

## Problème identifié

Lors de la modification d'un exercice de type `image_labeling`, les étiquettes et zones définies précédemment ne s'affichent pas correctement dans l'interface d'édition. L'image principale est bien chargée, mais les étiquettes et zones associées ne sont pas visibles, ce qui empêche une édition efficace de l'exercice.

## Causes racines

Après analyse approfondie, deux causes principales ont été identifiées :

1. **Absence d'initialisation des variables JavaScript** : Le template `image_labeling_edit.html` fait référence aux variables JavaScript `existingLabels` et `existingZones` qui ne sont jamais définies. Ces variables sont censées contenir les étiquettes et zones existantes de l'exercice.

2. **Absence de vérification de la structure des données** : La route d'édition ne vérifie pas si les structures `labels` et `zones` existent dans le contenu JSON de l'exercice, ce qui peut causer des erreurs JavaScript lors du chargement du template.

## Solution implémentée

### 1. Modification du template `image_labeling_edit.html`

Ajout d'un bloc de script au début du template pour initialiser les variables JavaScript avec les données existantes :

```html
<!-- Initialisation des variables JavaScript pour les étiquettes et zones existantes -->
<script>
    // Initialiser les variables avec les données existantes
    var existingLabels = [];
    var existingZones = [];
    
    {% if content and content.labels %}
        // Charger les étiquettes existantes
        {% for label in content.labels %}
            existingLabels.push({{ label|tojson|safe }});
        {% endfor %}
        console.log('Étiquettes chargées:', existingLabels);
    {% endif %}
    
    {% if content and content.zones %}
        // Charger les zones existantes
        {% for zone in content.zones %}
            existingZones.push({
                x: {{ zone.x }},
                y: {{ zone.y }},
                label: {{ zone.label|tojson|safe }}
            });
        {% endfor %}
        console.log('Zones chargées:', existingZones);
    {% endif %}
</script>
```

### 2. Modification de la route d'édition dans `app.py`

Ajout d'une logique spécifique pour les exercices de type `image_labeling` afin de garantir que les structures de données nécessaires sont présentes et correctement formatées :

```python
# Pour les exercices image_labeling, s'assurer que les structures de données sont correctes
if exercise.exercise_type == 'image_labeling':
    # S'assurer que content.labels existe
    if 'labels' not in content:
        content['labels'] = []
    
    # S'assurer que content.zones existe
    if 'zones' not in content:
        content['zones'] = []
    
    # Vérifier que les zones ont le bon format
    for i, zone in enumerate(content.get('zones', [])):
        # S'assurer que chaque zone a les propriétés x, y et label
        if not isinstance(zone, dict):
            content['zones'][i] = {'x': 0, 'y': 0, 'label': ''}
            continue
        
        if 'x' not in zone:
            zone['x'] = 0
        if 'y' not in zone:
            zone['y'] = 0
        if 'label' not in zone:
            zone['label'] = ''
    
    # Log pour le débogage
    app.logger.info(f"[IMAGE_LABELING_EDIT] Contenu chargé: {content}")
    app.logger.info(f"[IMAGE_LABELING_EDIT] Étiquettes: {content.get('labels', [])}")
    app.logger.info(f"[IMAGE_LABELING_EDIT] Zones: {content.get('zones', [])}")
```

## Bénéfices de la correction

1. **Affichage complet du contenu** : Les étiquettes et zones existantes sont maintenant correctement chargées et affichées dans l'interface d'édition.

2. **Prévention des erreurs JavaScript** : La vérification de la structure des données évite les erreurs JavaScript qui pourraient survenir si les propriétés attendues sont manquantes.

3. **Meilleure expérience utilisateur** : Les enseignants peuvent maintenant voir et modifier facilement les étiquettes et zones existantes, sans avoir à les recréer à chaque modification.

4. **Robustesse accrue** : Le code est plus robuste face à des données incomplètes ou mal formatées dans la base de données.

## Comment vérifier que la correction fonctionne

1. Accéder à un exercice existant de type `image_labeling` via la bibliothèque d'exercices.
2. Cliquer sur le bouton "Modifier" pour accéder à l'interface d'édition.
3. Vérifier que :
   - L'image principale s'affiche correctement
   - Les étiquettes existantes apparaissent dans la section "Étiquettes disponibles"
   - Les zones existantes sont visibles sur l'image avec leurs marqueurs numérotés
   - La liste des zones définies affiche correctement toutes les zones existantes

## Notes techniques supplémentaires

- La fonction `tojson|safe` est utilisée dans le template pour assurer que les chaînes de caractères sont correctement échappées pour JavaScript.
- Les logs de débogage ont été ajoutés pour faciliter le diagnostic en cas de problèmes futurs.
- La correction est compatible avec les exercices existants et n'affecte pas la structure de la base de données.

## Fichiers modifiés

1. `templates/exercise_types/image_labeling_edit.html` : Ajout de l'initialisation des variables JavaScript.
2. `app.py` : Modification de la route d'édition pour vérifier et préparer les structures de données.

## Script de correction

Un script de correction `fix_image_labeling_edit.py` a été créé pour faciliter l'implémentation de cette solution. Ce script :
- Fournit le code à ajouter à la route d'édition
- Inclut des tests pour valider que la correction fonctionne correctement
- Donne des instructions détaillées pour appliquer la correction
