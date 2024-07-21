from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.auth import get_db, get_current_active_user
from app.dependencies import get_current_moderator
from app.schemas import Tag

router = APIRouter()

@router.get("/tags/", response_model=list[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = crud.get_tags(db, skip=skip, limit=limit)
    return tags

@router.post("/tags/")
async def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    print('create_tag')
    db_tag = crud.get_tag_by_name(db, name=tag.name)

    if db_tag:
        print(db_tag.name)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")

    # Create and add the new tag to the database
    return crud.create_tag(db=db, tag=tag)
