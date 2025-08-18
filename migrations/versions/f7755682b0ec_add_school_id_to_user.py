"""add_school_id_to_user

Revision ID: f7755682b0ec
Revises: 451b669686ec
Create Date: 2025-08-17 19:19:29.647085

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7755682b0ec'
down_revision = '451b669686ec'
branch_labels = None
depends_on = None


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
