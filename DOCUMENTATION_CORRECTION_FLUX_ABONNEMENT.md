# Correction du Flux d'Abonnement École

## Problème identifié
Lorsqu'un enseignant choisit l'option d'abonnement "École", il était systématiquement redirigé vers la page de paiement, même si l'école à laquelle il est rattaché avait déjà un abonnement actif. Cela créait une confusion et pouvait mener à des paiements redondants.

## Solution implémentée

### 1. Modification de la route d'abonnement
Dans le fichier `payment_routes.py`, nous avons ajouté une vérification qui détecte si l'enseignant appartient à une école ayant déjà un abonnement actif :

```python
# Si l'utilisateur choisit l'abonnement école, vérifier s'il appartient déjà à une école qui a payé
if current_user.is_authenticated and subscription_type == 'school' and current_user.school_name:
    # Rechercher si un autre utilisateur de la même école a déjà un abonnement actif
    from models import User
    school_subscription = User.query.filter(
        User.school_name == current_user.school_name,
        User.subscription_type == 'school',
        User.subscription_status.in_(['paid', 'approved'])
    ).first()
    
    if school_subscription:
        # L'école a déjà un abonnement actif, approuver automatiquement cet utilisateur
        current_app.logger.info(f"Approbation automatique pour {current_user.email} car l'école {current_user.school_name} a déjà payé")
        current_user.subscription_status = 'approved'
        current_user.subscription_type = 'school'
        current_user.approval_date = datetime.utcnow()
        db.session.commit()
        
        flash(f'Votre école {current_user.school_name} a déjà un abonnement actif. Votre compte a été automatiquement approuvé.', 'success')
        return redirect(url_for('index'))
```

### 2. Amélioration de l'interface utilisateur
Dans le template `subscription_choice.html`, nous avons ajouté une note d'information pour les enseignants, les informant que s'ils appartiennent à une école ayant déjà un abonnement actif, ils seront automatiquement approuvés sans paiement supplémentaire :

```html
<div class="alert alert-info mt-3 mb-0" role="alert">
    <i class="fas fa-info-circle me-2"></i>
    <strong>Enseignants :</strong> Si votre école a déjà un abonnement actif, vous serez automatiquement approuvé sans paiement supplémentaire.
</div>
```

## Fonctionnement du nouveau flux

1. Un enseignant se connecte et choisit l'option d'abonnement "École"
2. Le système vérifie si l'école de l'enseignant (champ `school_name`) a déjà un utilisateur avec un abonnement école actif (`paid` ou `approved`)
3. Si oui :
   - Le statut d'abonnement de l'enseignant est automatiquement mis à jour à `approved`
   - Le type d'abonnement est défini sur `school`
   - L'enseignant est redirigé vers la page d'accueil avec un message de confirmation
4. Si non :
   - L'enseignant est dirigé vers la page de paiement comme avant

## Avantages de cette solution

- Évite les paiements redondants pour les écoles
- Simplifie le processus d'inscription pour les enseignants d'une même école
- Maintient la cohérence des données d'abonnement
- Améliore l'expérience utilisateur avec des messages clairs

## Points à surveiller

- Si un enseignant change d'école, son statut d'abonnement devrait être réévalué
- Les administrateurs devraient pouvoir voir quels enseignants sont rattachés à quelle école dans le tableau de bord
