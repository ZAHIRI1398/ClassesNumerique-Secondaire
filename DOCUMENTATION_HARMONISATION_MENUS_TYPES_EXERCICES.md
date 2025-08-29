# Documentation : Harmonisation des Menus de Types d'Exercices

## Problème Identifié

Suite à l'analyse des captures d'écran des formulaires de création et de modification d'exercices, nous avons constaté plusieurs incohérences entre les deux menus déroulants :

1. **Types d'exercices manquants** dans le formulaire de modification :
   - QCM Multichoix
   - Mots à placer
   - Dictée
   - Cartes mémoire

2. **Différences de nommage** pour le même type d'exercice :
   - "Étiquetage d'image" dans le formulaire de création
   - "Légender une image" dans le formulaire de modification

Ces incohérences pouvaient créer de la confusion pour les utilisateurs et potentiellement des problèmes techniques lors de la modification d'exercices existants.

## Modifications Apportées

### 1. Mise à jour du formulaire de modification (`edit_exercise.html`)

Nous avons ajouté les types d'exercices manquants au menu déroulant :
- QCM Multichoix
- Mots à placer
- Dictée
- Cartes mémoire

Nous avons également corrigé le libellé "Légender une image" pour utiliser "Étiquetage d'image" de manière cohérente avec le formulaire de création.

### 2. Harmonisation du formulaire de création (`create_exercise_in_library.html`)

Pour garantir une cohérence parfaite, nous avons vérifié et confirmé que tous les types d'exercices sont présents dans le même ordre et avec les mêmes libellés dans les deux formulaires.

## Avantages de cette Harmonisation

1. **Expérience utilisateur améliorée** : Les enseignants retrouvent les mêmes options dans les deux formulaires, ce qui réduit la confusion.

2. **Cohérence technique** : Les valeurs utilisées dans les deux formulaires sont maintenant identiques, ce qui évite les problèmes lors de la modification d'exercices.

3. **Maintenance simplifiée** : L'ajout de nouveaux types d'exercices à l'avenir sera plus simple car il suffira de mettre à jour les deux listes de la même manière.

## Recommandations pour l'Avenir

1. **Centralisation des types d'exercices** : Envisager de créer un fichier de configuration ou une fonction helper qui génère la liste des types d'exercices, pour éviter d'avoir à mettre à jour plusieurs fichiers lors de l'ajout de nouveaux types.

2. **Validation côté serveur** : S'assurer que le backend valide correctement tous les types d'exercices disponibles dans les formulaires.

3. **Documentation des types** : Maintenir une documentation à jour des différents types d'exercices et de leurs spécificités pour faciliter la formation des nouveaux enseignants.
