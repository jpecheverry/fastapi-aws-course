"""add many to many

Revision ID: 8b444e4e4446
Revises: 2e8ce7948c8b
Create Date: 2023-09-06 22:26:39.727447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b444e4e4446'
down_revision: Union[str, None] = '2e8ce7948c8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('read_books',
    sa.Column('Id', sa.INTEGER(), nullable=False),
    sa.Column('Book_Id', sa.INTEGER(), nullable=False),
    sa.Column('Read_Id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['Book_Id'], ['books.Id'], ),
    sa.ForeignKeyConstraint(['Read_Id'], ['readers.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    op.drop_index('ix_books_ReaderId', table_name='books')
    op.drop_constraint('books_ReaderId_fkey', 'books', type_='foreignkey')
    op.drop_column('books', 'ReaderId')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('ReaderId', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('books_ReaderId_fkey', 'books', 'readers', ['ReaderId'], ['Id'])
    op.create_index('ix_books_ReaderId', 'books', ['ReaderId'], unique=False)
    op.drop_table('read_books')
    # ### end Alembic commands ###