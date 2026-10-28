from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "recipe_id",
            name="uq_saved_recipe_user_recipe",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recipe_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ingredients: Mapped[list] = mapped_column(JSON, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")

    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )