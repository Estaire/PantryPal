from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.pantry_models import PantryIngredient
from app.routes.auth import get_current_user
from app.services.recommendations import normalize_ingredient


router = APIRouter(prefix="/api/v1/pantry", tags=["Pantry"])


class PantryResponse(BaseModel):
    ingredients: list[str]


class PantryUpdate(BaseModel):
    ingredients: list[str] = Field(max_length=200)


def canonical_pantry(values) -> list[str]:
    """Canonical, de-duplicated ingredient names in first-seen order."""
    names = (normalize_ingredient(value) for value in values)
    return list(dict.fromkeys(name for name in names if name))


@router.get("", response_model=PantryResponse)
def get_pantry(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stored = db.scalars(
        select(PantryIngredient.ingredient).where(
            PantryIngredient.user_id == user.id
        )
    ).all()

    # Canonicalize on read too, so rows saved before this change are fixed.
    return PantryResponse(ingredients=sorted(canonical_pantry(stored)))


@router.put("", response_model=PantryResponse)
def save_pantry(
    data: PantryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    normalized = canonical_pantry(data.ingredients)

    if any(len(name) > 100 for name in normalized):
        raise HTTPException(
            status_code=422,
            detail="Ingredient names must be 100 characters or fewer.",
        )

    db.execute(
        delete(PantryIngredient).where(
            PantryIngredient.user_id == user.id
        )
    )
    db.add_all(
        [
            PantryIngredient(user_id=user.id, ingredient=name)
            for name in normalized
        ]
    )
    db.commit()

    return PantryResponse(ingredients=normalized)