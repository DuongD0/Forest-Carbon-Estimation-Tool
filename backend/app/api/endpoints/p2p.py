from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.carbon_credit import CreditStatus
from app.models.p2p_listing import ListingStatus
from app.models.transaction import TransactionStatus
from app.services.stripe import stripe_service

router = APIRouter()

@router.get("/listings", response_model=List[schemas.P2PListing])
def read_active_listings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    get all active p2p listings
    """
    # TODO: this needs to be filtered for active status only
    listings = crud.p2p_listing.get_multi(db, skip=skip, limit=limit) 
    return listings

@router.post("/listings", response_model=schemas.P2PListing)
def create_listing(
    *,
    db: Session = Depends(deps.get_db),
    listing_in: schemas.P2PListingCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    make a new p2p listing for a credit.
    """
    # check the credit is real and i own it
    credit = crud.carbon_credit.get(db, id=listing_in.credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="Carbon credit not found")
    
    project = crud.project.get(db, id=credit.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to list this credit")

    # check if i can actually list it
    if credit.status != CreditStatus.ISSUED:
        raise HTTPException(status_code=400, detail=f"Credit has status '{credit.status}' and cannot be listed.")

    # ok, create the listing
    listing = crud.p2p_listing.create_with_seller(db=db, obj_in=listing_in, seller_id=current_user.id)
    
    # and update the credit to show it's listed now
    crud.carbon_credit.update(db=db, db_obj=credit, obj_in={"status": CreditStatus.LISTED})

    return listing

@router.post("/listings/{listing_id}/purchase", response_model=schemas.Transaction)
def purchase_credits(
    *,
    db: Session = Depends(deps.get_db),
    listing_id: str,
    purchase_in: schemas.TransactionCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    buy credits from a p2p listing.
    """
    listing = crud.p2p_listing.get(db, id=listing_id)
    if not listing or listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="Active listing not found")

    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own listing")

    if purchase_in.quantity > listing.quantity:
        raise HTTPException(status_code=400, detail="Not enough credits in listing")

    # make a transaction record first
    total_price = purchase_in.quantity * listing.price_per_ton
    transaction = crud.transaction.create(db, obj_in={
        "listing_id": listing_id,
        "buyer_id": current_user.id,
        "seller_id": listing.seller_id,
        "quantity": purchase_in.quantity,
        "total_price": total_price,
        "status": TransactionStatus.PENDING
    })

    # now try to take payment with stripe
    try:
        charge = stripe_service.create_charge(
            amount=int(total_price * 100), # stripe wants cents
            description=f"Purchase of {purchase_in.quantity} carbon credits"
        )
        # if payment is ok, update transaction
        transaction = crud.transaction.update(db, db_obj=transaction, obj_in={
            "status": TransactionStatus.COMPLETED,
            "stripe_charge_id": charge.id
        })
    except ValueError as e:
        # if payment fails, mark it as failed
        crud.transaction.update(db, db_obj=transaction, obj_in={"status": TransactionStatus.FAILED})
        raise HTTPException(status_code=402, detail=f"Payment failed: {e}")

    # update the listing with new quantity
    remaining_quantity = listing.quantity - purchase_in.quantity
    new_status = ListingStatus.SOLD if remaining_quantity == 0 else ListingStatus.ACTIVE
    crud.p2p_listing.update(db, db_obj=listing, obj_in={
        "quantity": remaining_quantity,
        "status": new_status
    })

    # if we sold all of it, mark credit as sold
    if new_status == ListingStatus.SOLD:
        credit = crud.carbon_credit.get(db, id=listing.credit_id)
        crud.carbon_credit.update(db, db_obj=credit, obj_in={"status": CreditStatus.SOLD})

    return transaction 