"""INIT

Revision ID: 3437fd525d72
Revises: 
Create Date: 2023-06-12 14:56:46.384044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3437fd525d72'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id_0', sa.String(), nullable=True),
    sa.Column('player_id_1', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('queue',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('searcher', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('notification', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_state',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('turn', sa.Integer(), nullable=True),
    sa.Column('roll', sa.Integer(), nullable=True),
    sa.Column('win_0', sa.Integer(), nullable=True),
    sa.Column('win_1', sa.Integer(), nullable=True),
    sa.Column('player_id_0', sa.String(), nullable=True),
    sa.Column('player_id_1', sa.String(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pieces_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('piece_id', sa.Integer(), nullable=True),
    sa.Column('pos', sa.Integer(), nullable=True),
    sa.Column('player', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pieces_table')
    op.drop_table('game_state')
    op.drop_table('user')
    op.drop_table('queue')
    op.drop_table('games')
    # ### end Alembic commands ###
