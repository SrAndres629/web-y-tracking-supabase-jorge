"""Create site_settings table

Revision ID: 449b6eaa75ab
Revises: 997c4c43c564
Create Date: 2026-02-06 04:22:15.410447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '449b6eaa75ab'
down_revision: Union[str, Sequence[str], None] = '997c4c43c564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create site_content table and seed default data"""
    # 1. Create Table
    op.create_table(
        'site_content',
        sa.Column('key', sa.String(50), primary_key=True),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # 2. Seed Initial Data (Broke Superstar Trick: No separate script needed)
    # We move the hardcoded configs from app/services.py to the DB
    op.execute("""
        INSERT INTO site_content (key, value) VALUES 
        ('services_config', '[
            {"id": "microblading", "title": "Microblading Elite", "description": "Cejas perfectas pelo a pelo con resultados naturales.", "icon": "fa-eye", "color": "luxury-gold"},
            {"id": "eyeliner", "title": "Delineado Permanente", "description": "Resalta tu mirada las 24 horas del día.", "icon": "fa-pencil", "color": "luxury-gold"},
            {"id": "lips", "title": "Acuarela de Labios", "description": "Color y definición vibrante para tus labios.", "icon": "fa-kiss", "color": "luxury-gold"}
        ]'),
        ('contact_config', '{
            "whatsapp": "https://wa.me/59164714751",
            "phone": "+591 64714751",
            "email": "contacto@jorgeaguirreflores.com",
            "location": "Santa Cruz de la Sierra, Bolivia",
            "instagram": "https://instagram.com/jorgeaguirreflores"
        }')
    """)


def downgrade() -> None:
    """Drop site_content table"""
    op.drop_table('site_content')
