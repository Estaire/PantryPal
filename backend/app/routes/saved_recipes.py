from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user
from app.saved_recipe_models import SavedRecipe


router = APIRouter(prefix="/api/v1/saved-recipes", tags=["Saved Recipes"])


class IngredientItem(BaseModel):
    name: str = Field(max_length=200)
    measure: str = Field(default="", max_length=100)


class SaveRecipeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    image: str = Field(default="", max_length=2048)
    ingredients: list[IngredientItem] = Field(max_length=100)
    instructions: str = Field(default="", max_length=20000)


class SavedRecipeResponse(BaseModel):
    id: str
    name: str
    image: str
    ingredients: list[IngredientItem]
    instructions: str
    saved_at: str


def to_response(row: SavedRecipe) -> SavedRecipeResponse:
    return SavedRecipeResponse(
        id=row.recipe_id,
        name=row.name,
        image=row.image,
        ingredients=row.ingredients,
        instructions=row.instructions,
        saved_at=row.saved_at.isoformat(),
    )


def find_saved(db: Session, user: User, recipe_id: str) -> SavedRecipe | None:
    return db.scalar(
        select(SavedRecipe).where(
            SavedRecipe.user_id == user.id,
            SavedRecipe.recipe_id == recipe_id,
        )
    )


@router.get("", response_model=list[SavedRecipeResponse])
def list_saved_recipes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = db.scalars(
        select(SavedRecipe)
        .where(SavedRecipe.user_id == user.id)
        .order_by(SavedRecipe.saved_at.desc())
    ).all()

    return [to_response(row) for row in rows]


@router.put("/{recipe_id}", response_model=SavedRecipeResponse)
def save_recipe(
    recipe_id: str,
    data: SaveRecipeRequest,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    recipe_id = recipe_id.strip()
    if not recipe_id or len(recipe_id) > 64:
        raise HTTPException(status_code=422, detail="Invalid recipe ID.")

    existing = find_saved(db, user, recipe_id)
    if existing is not None:
        # Idempotent: keep the original snapshot and don't rewrite it.
        response.status_code = status.HTTP_200_OK
        return to_response(existing)

    row = SavedRecipe(
        user_id=user.id,
        recipe_id=recipe_id,
        name=data.name.strip(),
        image=data.image,
        ingredients=[item.model_dump() for item in data.ingredients],
        instructions=data.instructions,
    )
    db.add(row)

    try:
        db.commit()
    except IntegrityError:
        # A concurrent request saved the same recipe first.
        db.rollback()
        existing = find_saved(db, user, recipe_id)
        if existing is None:
            raise
        response.status_code = status.HTTP_200_OK
        return to_response(existing)

    db.refresh(row)
    response.status_code = status.HTTP_201_CREATED
    return to_response(row)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_recipe(
    recipe_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = db.execute(
        delete(SavedRecipe).where(
            SavedRecipe.user_id == user.id,
            SavedRecipe.recipe_id == recipe_id.strip(),
        )
    )
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Saved recipe not found.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)