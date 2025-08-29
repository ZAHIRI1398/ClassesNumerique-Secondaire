# Documentation de la correction d'affichage des images dans les exercices d'association de paires

## Problème initial

L'interface d'édition des exercices d'association de paires (`pairs_edit.html`) présentait un problème d'affichage des images :

- Les images existantes n'étaient pas prévisualisées lors de l'édition d'un exercice
- Après avoir sélectionné le type "Image" dans les menus déroulants, aucune prévisualisation n'était disponible pour les images déjà enregistrées
- Les utilisateurs ne pouvaient pas voir les images qu'ils avaient précédemment téléchargées ou référencées par URL

## Analyse du problème

Après examen du template `pairs_edit.html`, nous avons identifié les causes suivantes :

1. **Absence de code de prévisualisation** : Contrairement à d'autres templates d'édition (comme `image_labeling_edit.html`), le template ne contenait aucun code pour afficher les images existantes.

2. **Absence de prévisualisation pour les nouvelles images** : Le code JavaScript ne générait pas de prévisualisation lors du téléchargement de nouvelles images.

3. **Gestion incomplète des types d'éléments** : Lors du basculement entre les types "Texte" et "Image", le code ne gérait pas correctement l'affichage/masquage des prévisualisations.

## Solution implémentée

### 1. Ajout de la prévisualisation des images existantes

Pour chaque élément de paire (gauche et droite), nous avons ajouté un bloc de prévisualisation conditionnel :

```html
<!-- Prévisualisation de l'image existante -->
{% if pair.left.type == 'image' and pair.left.content %}
<div class="mt-2 image-preview">
    <img src="{{ pair.left.content }}?v={{ range(100000, 999999) | random }}" 
         alt="Image gauche" class="img-thumbnail" style="max-height: 100px;" 
         onerror="this.onerror=null; this.src='/static/images/placeholder-image.png'; this.style.opacity='0.7';">
</div>
{% endif %}
```

### 2. Ajout de la prévisualisation pour les nouvelles images

Nous avons créé une fonction JavaScript `previewPairImage()` qui génère une prévisualisation en temps réel lors du téléchargement d'une nouvelle image :

```javascript
// Fonction pour prévisualiser les images téléchargées
function previewPairImage(input, side, pairId) {
    const previewDiv = document.getElementById(`${side}-preview-${pairId}`);
    if (!previewDiv) return;
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewDiv.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-height: 100px;">`;
            previewDiv.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}
```

### 3. Amélioration de la fonction de basculement entre types

Nous avons amélioré la fonction `togglePairInput()` pour gérer correctement l'affichage/masquage des prévisualisations :

```javascript
window.togglePairInput = function(side, pairId) {
    const typeSelect = document.querySelector(`select[name="pair_${side}_type_${pairId}"]`);
    const textInput = document.querySelector(`input[name="pair_${side}_${pairId}"]`);
    const fileInput = document.querySelector(`input[name="pair_${side}_image_${pairId}"]`);
    const previewDiv = document.getElementById(`${side}-preview-${pairId}`);
    
    if (typeSelect && textInput && fileInput) {
        if (typeSelect.value === 'image') {
            textInput.placeholder = 'URL de l\'image (optionnel si fichier uploadé)';
            textInput.required = false;
            fileInput.style.display = 'block';
            if (previewDiv) previewDiv.style.display = 'block';
        } else {
            textInput.placeholder = 'Texte';
            textInput.required = true;
            fileInput.style.display = 'none';
            if (previewDiv) previewDiv.style.display = 'none';
        }
    }
};
```

### 4. Ajout de styles CSS pour les prévisualisations

Nous avons ajouté des styles CSS pour améliorer l'apparence des prévisualisations :

```css
.image-preview {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
    background-color: #f8f9fa;
    margin-top: 5px;
}
.image-preview img {
    display: block;
    margin: 0 auto;
}
```

### 5. Ajout de conteneurs pour les prévisualisations dynamiques

Pour les nouvelles paires ajoutées dynamiquement, nous avons créé des conteneurs de prévisualisation :

```html
<div class="mt-2 image-preview" id="left-preview-${pairCount}" style="display: none;"></div>
```

## Améliorations apportées

1. **Cache-busting** : Ajout d'un paramètre aléatoire à l'URL des images (`?v={{ random }}`) pour éviter les problèmes de cache du navigateur.

2. **Gestion des erreurs d'image** : Ajout d'un gestionnaire `onerror` pour afficher une image de remplacement en cas d'échec de chargement.

3. **Prévisualisation en temps réel** : Les nouvelles images téléchargées sont immédiatement prévisualisées sans rechargement de la page.

4. **Interface utilisateur améliorée** : Meilleure organisation visuelle avec des bordures et un espacement approprié.

## Résultat final

- ✅ Les images existantes sont correctement prévisualisées lors de l'édition d'un exercice
- ✅ Les nouvelles images téléchargées sont immédiatement prévisualisées
- ✅ L'interface bascule correctement entre les modes texte et image
- ✅ Les prévisualisations sont stylisées de manière cohérente avec le reste de l'interface
- ✅ Le système est robuste face aux erreurs de chargement d'images

Cette correction s'aligne avec l'approche utilisée dans les autres templates d'édition d'exercices qui fonctionnaient correctement, comme `image_labeling_edit.html`.
