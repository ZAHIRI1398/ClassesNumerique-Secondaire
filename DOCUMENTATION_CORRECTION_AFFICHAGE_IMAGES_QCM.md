# Documentation : Correction de l'affichage des images d'explication dans les exercices QCM

## Problème identifié

Lors de la création ou de la modification d'exercices de type QCM, l'image d'explication optionnelle n'était pas affichée dans l'interface d'édition, bien que cette fonctionnalité soit correctement gérée dans le backend et dans l'affichage final de l'exercice.

### Symptômes observés
- L'image d'explication était correctement sauvegardée dans la base de données
- L'image était visible lors de l'affichage de l'exercice (template `qcm.html`)
- L'image n'était pas visible lors de la modification de l'exercice (template `qcm_edit.html`)
- Aucune interface n'était disponible pour télécharger ou remplacer l'image dans l'interface d'édition

## Cause racine

Le template `qcm_edit.html` ne contenait pas de section dédiée à l'affichage et à la gestion de l'image d'explication, contrairement au template d'affichage `qcm.html` qui lui affichait correctement l'image.

Le backend gérait pourtant correctement cette fonctionnalité :
- L'image était sauvegardée dans `exercise.image_path`
- L'image était également synchronisée dans `content['image']` pour assurer la cohérence
- La route d'édition gérait correctement l'upload et le remplacement d'images

## Solution implémentée

### 1. Ajout d'une section d'image dans le template d'édition

Une nouvelle section a été ajoutée au début du template `qcm_edit.html` pour :
- Afficher l'image existante si elle est présente
- Permettre le téléchargement d'une nouvelle image
- Fournir des informations sur les formats acceptés

```html
<!-- Section pour l'image d'explication -->
<div class="card mb-4">
    <div class="card-header bg-light">
        <h5 class="mb-0">Image d'explication (optionnelle)</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <div class="form-group mb-3">
                    <label for="exercise_image" class="form-label">Choisir une image</label>
                    <input type="file" class="form-control" id="exercise_image" name="exercise_image" accept="image/*">
                    <div class="form-text">Format recommandé : JPG ou PNG, max 2MB</div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="text-center">
                    {% if exercise.image_path or (content and content.image) %}
                        <p class="mb-2">Image actuelle :</p>
                        <img src="{{ exercise.image_path or content.image }}?v={{ range(1000000, 9999999) | random }}" 
                             alt="Image d'explication" class="img-fluid rounded shadow" 
                             style="max-height: 200px; object-fit: contain;"
                             onerror="this.style.display='none'; document.getElementById('no-image-msg').style.display='block';">
                        <div id="no-image-msg" class="alert alert-warning mt-2" style="display: none;">
                            <i class="fas fa-exclamation-triangle"></i> L'image n'a pas pu être chargée
                        </div>
                    {% else %}
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> Aucune image n'est actuellement associée à cet exercice
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2. Caractéristiques de la solution

- **Affichage conditionnel** : L'image est affichée uniquement si elle existe dans `exercise.image_path` ou `content.image`
- **Prévention du cache** : Ajout d'un paramètre aléatoire à l'URL pour éviter les problèmes de cache
- **Gestion des erreurs** : Si l'image ne peut pas être chargée, un message d'erreur s'affiche
- **Interface responsive** : Utilisation de Bootstrap pour une mise en page adaptative
- **Compatibilité** : Fonctionne avec le code backend existant sans modification nécessaire

## Bénéfices

1. **Expérience utilisateur améliorée** : Les enseignants peuvent maintenant voir et modifier l'image d'explication directement dans l'interface d'édition
2. **Cohérence** : L'interface d'édition reflète maintenant fidèlement toutes les fonctionnalités disponibles pour les exercices QCM
3. **Prévention des erreurs** : Les utilisateurs peuvent vérifier visuellement l'image associée à l'exercice avant de sauvegarder

## Comment tester la correction

1. Connectez-vous en tant qu'enseignant
2. Créez un nouvel exercice de type QCM
3. Téléchargez une image d'explication
4. Sauvegardez l'exercice
5. Modifiez l'exercice existant
6. Vérifiez que l'image précédemment téléchargée est visible dans l'interface d'édition
7. Essayez de remplacer l'image par une nouvelle image
8. Sauvegardez et vérifiez que la nouvelle image est correctement affichée

## Notes techniques

- Cette correction n'a nécessité aucune modification du backend, car celui-ci gérait déjà correctement les images d'explication
- La solution utilise les mêmes conventions que les autres types d'exercices pour assurer la cohérence
- Le template vérifie à la fois `exercise.image_path` et `content.image` pour une robustesse maximale
