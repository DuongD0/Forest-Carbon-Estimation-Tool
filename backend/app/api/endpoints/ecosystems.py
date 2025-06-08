from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Ecosystem])
def read_ecosystems(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all ecosystems.
    """
    ecosystems = crud.ecosystem.get_multi(db, skip=skip, limit=limit)
    return ecosystems

@router.post("/", response_model=schemas.Ecosystem)
def create_ecosystem(
    *,
    db: Session = Depends(deps.get_db),
    ecosystem_in: schemas.EcosystemCreate,
    current_user: models.User = Security(deps.get_current_user, scopes=["manage:ecosystems"]),
) -> Any:
    """
    Create new ecosystem. (Admin only)
    """
    ecosystem = crud.ecosystem.create(db=db, obj_in=ecosystem_in)
    return ecosystem

@router.put("/{ecosystem_id}", response_model=schemas.Ecosystem)
def update_ecosystem(
    *,
    db: Session = Depends(deps.get_db),
    ecosystem_id: str,
    ecosystem_in: schemas.EcosystemUpdate,
    current_user: models.User = Security(deps.get_current_user, scopes=["manage:ecosystems"]),
) -> Any:
    """
    Update an ecosystem. (Admin only)
    """
    ecosystem = crud.ecosystem.get(db=db, id=ecosystem_id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    ecosystem = crud.ecosystem.update(db=db, db_obj=ecosystem, obj_in=ecosystem_in)
    return ecosystem

@router.get("/{ecosystem_id}", response_model=schemas.Ecosystem)
def read_ecosystem(
    *,
    db: Session = Depends(deps.get_db),
    ecosystem_id: str,
) -> Any:
    """
    Get ecosystem by ID.
    """
    ecosystem = crud.ecosystem.get(db=db, id=ecosystem_id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    return ecosystem

@router.delete("/{ecosystem_id}", response_model=schemas.Ecosystem)
def delete_ecosystem(
    *,
    db: Session = Depends(deps.get_db),
    ecosystem_id: str,
    current_user: models.User = Security(deps.get_current_user, scopes=["manage:ecosystems"]),
) -> Any:
    """
    Delete an ecosystem. (Admin only)
    """
    ecosystem = crud.ecosystem.get(db=db, id=ecosystem_id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    ecosystem = crud.ecosystem.remove(db=db, id=ecosystem_id)
    return ecosystem 