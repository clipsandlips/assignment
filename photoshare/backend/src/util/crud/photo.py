import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from backend.src.util.schemas import photo as schema_photo
from backend.src.util.models import photo as model_photo, tag as model_tag
from backend.src.util.logging_config import logger
from sqlalchemy.orm import selectinload

async def create_photo(db: AsyncSession, photo: schema_photo.PhotoCreate, user_id: int):
    if len(photo.tags) > 5:
        raise ValueError('A photo cannot have more than 5 tags.')

    logger.debug('start : model_photo.Photo')
    db_photo = model_photo.Photo(
        url=photo.url,
        description=photo.description,
        owner_id=user_id
    )
    logger.debug('end : model_photo.Photo')

    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)

    for tag_create in photo.tags or []:
        tag_name = tag_create.name

        logger.debug('start : tag')

        result = await db.execute(select(model_tag.Tag).filter(model_tag.Tag.name == tag_name))
        db_tag = result.scalars().first()
        logger.debug('end: tag')

        if not db_tag:
            logger.debug('start: add a new tag')
            db_tag = model_tag.Tag(name=tag_name)
            db.add(db_tag)
            await db.commit()
            await db.refresh(db_tag)
            logger.debug('end: add a new tag')

        db_photo.tags.append(db_tag)
        await db.commit()

    logger.debug('start : schema_photo')

    response_photo = schema_photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )
    logger.debug('end: schema_photo')

    return response_photo




async def get_photo(db: AsyncSession, photo_id: int):
    result = await db.execute(
        select(model_photo.Photo)
        .options(selectinload(model_photo.Photo.tags))
        .filter(model_photo.Photo.id == photo_id)
    )
    db_photo = result.scalars().first()
    if not db_photo:
        return None

    response_photo = schema_photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )
    return response_photo




async def update_photo(db: AsyncSession, photo_id: int, photo_update: schema_photo.PhotoCreate):
    if len(photo_update.tags) > 5:
        raise ValueError('A photo cannot have more than 5 tags.')

    # Get the photo by ID
    result = await db.execute(
        select(model_photo.Photo).options(selectinload(model_photo.Photo.tags)).filter(model_photo.Photo.id == photo_id)
    )
    db_photo = result.scalars().first()
    if not db_photo:
        return None

    db_photo.url = photo_update.url
    db_photo.description = photo_update.description

    # Clear existing tags
    db_photo.tags = []

    # Add new tags
    for tag_create in photo_update.tags or []:
        tag_name = tag_create.name
        result = await db.execute(select(model_tag.Tag).filter(model_tag.Tag.name == tag_name))
        db_tag = result.scalars().first()
        if not db_tag:
            db_tag = model_tag.Tag(name=tag_name)
            db.add(db_tag)
            await db.commit()
            await db.refresh(db_tag)
        db_photo.tags.append(db_tag)

    await db.commit()
    await db.refresh(db_photo)

    # Return a response model with tag names
    response_photo = schema_photo.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )

    return response_photo




async def delete_photo(db: AsyncSession, photo_id: int):
    result = await db.execute(select(model_photo.Photo).filter(model_photo.Photo.id == photo_id))
    db_photo = result.scalars().first()
    if db_photo:
        await db.delete(db_photo)
        await db.commit()


async def transform_photo(db: AsyncSession, photo_id: int, transformation: str) -> schema_photo.Photo:
    result = await db.execute(select(model_photo.Photo).filter(model_photo.Photo.id == photo_id))
    db_photo = result.scalars().first()
    if not db_photo:
        raise ValueError("Photo not found")

    if transformation == "scale":
        db_photo.url += "?transformation=scale"
    elif transformation == "r_max":
        db_photo.url += "?transformation=r_max"
    else:
        raise ValueError("Invalid transformation")

    # Commit the changes to the database
    await db.commit()
    await db.refresh(db_photo)

    # Convert ORM model instance to Pydantic schema
    response_photo = schema_photo.Photo.from_orm(db_photo)

    return response_photo