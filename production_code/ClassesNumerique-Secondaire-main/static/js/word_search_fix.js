// Solution définitive pour l'ajout de mots dans "Mots mêlés"
// Ce fichier contient une logique robuste qui fonctionne dans tous les cas

function addWordReliable() {
    console.log('[RELIABLE] Fonction addWordReliable appelée');
    
    const container = document.getElementById('word_search_container');
    if (!container) {
        console.error('[RELIABLE] Conteneur non trouvé');
        return false;
    }
    
    // Créer le nouvel élément
    const wordDiv = document.createElement('div');
    wordDiv.className = 'input-group mb-2';
    wordDiv.style.display = 'block';
    wordDiv.style.visibility = 'visible';
    wordDiv.style.opacity = '1';
    
    // Générer un ID unique pour éviter les conflits
    const uniqueId = 'word_' + Date.now();
    
    wordDiv.innerHTML = `
        <input type="text" name="word_search_words[]" class="form-control" 
               placeholder="Entrez un mot à cacher" id="${uniqueId}">
        <button type="button" class="btn btn-outline-danger" 
                onclick="removeWordReliable(this)">
            <i class="bi bi-trash"></i>
        </button>
    `;
    
    // Ajouter au conteneur
    container.appendChild(wordDiv);
    
    // Forcer le reflow pour garantir l'affichage
    container.style.display = 'none';
    container.offsetHeight; // Force reflow
    container.style.display = 'block';
    
    console.log('[RELIABLE] Nouveau mot ajouté avec ID:', uniqueId);
    return true;
}

function removeWordReliable(button) {
    console.log('[RELIABLE] Suppression d\'un mot');
    const wordDiv = button.closest('.input-group');
    if (wordDiv) {
        wordDiv.remove();
        console.log('[RELIABLE] Mot supprimé avec succès');
    }
}

// Initialisation robuste au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('[RELIABLE] Initialisation du système de mots mêlés');
    
    // Attendre que tout soit chargé
    setTimeout(function() {
        // Chercher le bouton "Ajouter un mot" et le corriger
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.textContent.includes('Ajouter un mot')) {
                console.log('[RELIABLE] Bouton trouvé, correction en cours...');
                
                // Supprimer l'ancien onclick défaillant
                btn.removeAttribute('onclick');
                btn.onclick = null;
                
                // Ajouter le nouveau gestionnaire fiable
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('[RELIABLE] Clic détecté sur bouton corrigé');
                    addWordReliable();
                });
                
                console.log('[RELIABLE] Bouton corrigé avec succès');
                break;
            }
        }
    }, 500);
});

// Fonction de test accessible globalement
window.testAddWord = function() {
    console.log('[TEST] Test d\'ajout de mot...');
    return addWordReliable();
};

console.log('[RELIABLE] Fichier word_search_fix.js chargé');
