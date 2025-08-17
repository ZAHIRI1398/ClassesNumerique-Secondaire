# Amélioration du Flux d'Abonnement École

## Problème identifié
Lorsqu'un enseignant choisit l'option d'abonnement "École", il devrait pouvoir sélectionner une école existante qui a déjà un abonnement actif, plutôt que d'être automatiquement associé à une école basée sur son champ `school_name`.

## Solution implémentée

### 1. Nouvelle route de sélection d'école
Nous avons créé une nouvelle route `/payment/select_school` qui permet aux enseignants de voir et sélectionner une école parmi celles qui ont déjà un abonnement actif.

```python
@payment_bp.route('/select_school')
@login_required
def select_school():
    """Page de sélection d'une école déjà abonnée"""
    # Vérifier que l'utilisateur est un enseignant
    if not current_user.role == 'teacher':
        flash('Cette page est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer la liste des écoles ayant un abonnement actif
    from models import User
    from sqlalchemy import func
    
    # Trouver toutes les écoles avec au moins un utilisateur ayant un abonnement actif
    schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
        filter(User.school_name != None).\
        filter(User.school_name != '').\
        filter(User.subscription_type == 'school').\
        filter(User.subscription_status.in_(['paid', 'approved'])).\
        group_by(User.school_name).all()
    
    # Si aucune école n'est trouvée
    if not schools_with_subscription:
        flash('Aucune école avec un abonnement actif n\'a été trouvée. Veuillez procéder au paiement pour un abonnement école.', 'info')
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    return render_template('payment/select_school.html', schools=schools_with_subscription)
```

### 2. Route d'association à une école
Une nouvelle route `/payment/join_school` permet à un enseignant de s'associer à une école sélectionnée et d'être automatiquement approuvé.

```python
@payment_bp.route('/join_school', methods=['POST'])
@login_required
def join_school():
    """Associer un enseignant à une école déjà abonnée"""
    # Vérifier que l'utilisateur est un enseignant
    if not current_user.role == 'teacher':
        flash('Cette fonctionnalité est réservée aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    # Récupérer le nom de l'école sélectionnée
    school_name = request.form.get('school_name')
    if not school_name:
        flash('Veuillez sélectionner une école.', 'error')
        return redirect(url_for('payment.select_school'))
    
    # Vérifier que l'école a bien un abonnement actif
    from models import User
    school_subscription = User.query.filter(
        User.school_name == school_name,
        User.subscription_type == 'school',
        User.subscription_status.in_(['paid', 'approved'])
    ).first()
    
    if not school_subscription:
        flash('Cette école n\'a pas d\'abonnement actif.', 'error')
        return redirect(url_for('payment.select_school'))
    
    # Associer l'enseignant à l'école et activer son abonnement
    current_user.school_name = school_name
    current_user.subscription_status = 'approved'
    current_user.subscription_type = 'school'
    current_user.approval_date = datetime.utcnow()
    db.session.commit()
    
    current_app.logger.info(f"Enseignant {current_user.email} associé à l'école {school_name} avec abonnement approuvé")
    flash(f'Vous avez été associé avec succès à l\'école {school_name}. Votre compte a été automatiquement approuvé.', 'success')
    
    return redirect(url_for('index'))
```

### 3. Modification de la route d'abonnement
La route `/payment/subscribe/<subscription_type>` a été modifiée pour rediriger les enseignants vers la page de sélection d'école lorsqu'ils choisissent l'abonnement "École".

```python
# Si l'utilisateur est un enseignant et choisit l'abonnement école, rediriger vers la sélection d'école
if current_user.is_authenticated and subscription_type == 'school' and current_user.role == 'teacher':
    return redirect(url_for('payment.select_school'))
```

### 4. Nouveau template de sélection d'école
Un nouveau template `select_school.html` a été créé pour afficher la liste des écoles avec un abonnement actif et permettre à l'enseignant de sélectionner son école.

## Fonctionnement du nouveau flux

1. Un enseignant se connecte et choisit l'option d'abonnement "École"
2. Il est redirigé vers la page de sélection d'école
3. Il voit la liste des écoles ayant déjà un abonnement actif
4. Il sélectionne son école et clique sur "Rejoindre cette école"
5. Son compte est automatiquement associé à l'école et son abonnement est approuvé
6. Il est redirigé vers la page d'accueil avec un message de confirmation

Si aucune école n'a d'abonnement actif ou si l'enseignant ne trouve pas son école dans la liste, il peut toujours procéder à un nouveau paiement pour un abonnement école.

## Avantages de cette solution

- Interface utilisateur plus intuitive pour les enseignants
- Meilleure gestion des écoles avec plusieurs enseignants
- Évite les erreurs de saisie du nom de l'école
- Permet de voir combien d'utilisateurs sont déjà associés à chaque école
- Maintient la possibilité de créer un nouvel abonnement école si nécessaire

## Points à surveiller

- S'assurer que les noms d'écoles sont cohérents dans la base de données
- Vérifier que les enseignants ont bien le rôle 'teacher' dans la base de données
- Considérer l'ajout d'une fonctionnalité de recherche si la liste des écoles devient trop longue
