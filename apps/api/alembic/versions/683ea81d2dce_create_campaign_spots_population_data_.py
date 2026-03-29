"""create campaign_spots population_data congestion_data tables

Revision ID: 683ea81d2dce
Revises:
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '683ea81d2dce'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'campaign_spots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('spot_type', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('congestion_score', sa.Float(), nullable=True),
        sa.Column('population_score', sa.Float(), nullable=True),
        sa.Column('visit_penalty', sa.Float(), nullable=False),
        sa.Column('last_visited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'congestion_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spot_id', sa.Integer(), nullable=False),
        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('congestion_level', sa.Integer(), nullable=True),
        sa.Column('congestion_score', sa.Float(), nullable=True),
        sa.Column('raw_data', sa.String(length=2000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_congestion_data_measured_at', 'congestion_data', ['measured_at'])
    op.create_index('ix_congestion_data_spot_id', 'congestion_data', ['spot_id'])

    op.create_table(
        'population_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('district_code', sa.String(length=10), nullable=False),
        sa.Column('district_name', sa.String(length=100), nullable=False),
        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_population', sa.Integer(), nullable=True),
        sa.Column('male_population', sa.Integer(), nullable=True),
        sa.Column('female_population', sa.Integer(), nullable=True),
        sa.Column('age_10s', sa.Integer(), nullable=True),
        sa.Column('age_20s', sa.Integer(), nullable=True),
        sa.Column('age_30s', sa.Integer(), nullable=True),
        sa.Column('age_40s', sa.Integer(), nullable=True),
        sa.Column('age_50s', sa.Integer(), nullable=True),
        sa.Column('age_60s_plus', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_population_data_district_code', 'population_data', ['district_code'])
    op.create_index('ix_population_data_measured_at', 'population_data', ['measured_at'])


def downgrade() -> None:
    op.drop_index('ix_population_data_measured_at', table_name='population_data')
    op.drop_index('ix_population_data_district_code', table_name='population_data')
    op.drop_table('population_data')
    op.drop_index('ix_congestion_data_spot_id', table_name='congestion_data')
    op.drop_index('ix_congestion_data_measured_at', table_name='congestion_data')
    op.drop_table('congestion_data')
    op.drop_table('campaign_spots')
