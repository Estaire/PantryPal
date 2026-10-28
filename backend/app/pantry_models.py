from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PantryIngredient(Base):
    __tablename__ = "pantry_ingredients"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "ingredient",
            name="uq_pantry_user_ingredient",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ingredient: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
