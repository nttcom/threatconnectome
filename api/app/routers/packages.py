from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db

router = APIRouter(prefix="/packages", tags=["packages"])


@router.post("", response_model=schemas.PackageResponse)
def create_package(package: schemas.PackageCreate, db: Session = Depends(get_db)):
    existing_package = (
        db.query(schemas.PackageBase)
        .filter(
            schemas.PackageBase.name == package.name,
            schemas.PackageBase.ecosystem == package.ecosystem,
        )
        .first()
    )

    if not existing_package:
        new_package = schemas.PackageBase(name=package.name, ecosystem=package.ecosystem)
        db.add(new_package)
        db.commit()
        db.refresh(new_package)
    else:
        new_package = existing_package

    new_package_version = schemas.PackageBase(
        package_id=new_package.package_id, version=package.version
    )
    db.add(new_package_version)
    try:
        db.commit()
        db.refresh(new_package_version)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Package version already exists.")

    return schemas.PackageResponse(
        package_id=new_package.package_id, name=new_package.name, ecosystem=new_package.ecosystem
    )
