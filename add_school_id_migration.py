from alembic import op
import sqlalchemy as sa

"""
Script pour ajouter manuellement la colonne school_id à la table user
et créer la contrainte de clé étrangère correspondante.
"""

def upgrade():
    # Ajouter la colonne school_id à la table user
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('school_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_school_id', 'school', ['school_id'], ['id'])

def downgrade():
    # Supprimer la colonne school_id de la table user
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_school_id', type_='foreignkey')
        batch_op.drop_column('school_id')

if __name__ == '__main__':
    # Ce script doit être exécuté dans le contexte d'une migration Alembic
    print("Ce script contient les fonctions upgrade() et downgrade() pour une migration Alembic.")
    print("Pour l'utiliser, créez une nouvelle migration avec:")
    print("flask db revision -m 'add_school_id_to_user'")
    print("Puis remplacez le contenu du fichier de migration par ce script.")
