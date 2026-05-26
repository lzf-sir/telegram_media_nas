"""
Accounts API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import TelegramAccount
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import account_service

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
):
    """List all Telegram accounts"""
    accounts = await account_service.list_accounts(db)
    return [AccountResponse(**acc.to_dict()) for acc in accounts]


@router.post("/", response_model=AccountResponse)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new Telegram account"""
    try:
        account = await account_service.create_account(
            db=db,
            phone=data.phone,
            api_id=data.api_id,
            api_hash=data.api_hash,
            session_name=data.session_name,
            is_default=data.is_default or False,
        )
        return AccountResponse(**account.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{account_id}/activate", response_model=AccountResponse)
async def activate_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Activate a Telegram account (start session)"""
    try:
        account = await account_service.activate_account(db, account_id)
        return AccountResponse(**account.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{account_id}/deactivate", response_model=AccountResponse)
async def deactivate_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a Telegram account"""
    try:
        account = await account_service.deactivate_account(db, account_id)
        return AccountResponse(**account.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a Telegram account"""
    try:
        await account_service.delete_account(db, account_id)
        return {"message": "Account deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/default", response_model=AccountResponse)
async def get_default_account(
    db: AsyncSession = Depends(get_db),
):
    """Get the default Telegram account"""
    account = await account_service.get_default_account(db)
    if not account:
        raise HTTPException(status_code=404, detail="No default account found")
    return AccountResponse(**account.to_dict())


@router.post("/{account_id}/set-default", response_model=AccountResponse)
async def set_default_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Set an account as the default"""
    from app.models.account import TelegramAccount

    # Remove default from all accounts
    result = await db.execute(select(TelegramAccount))
    for acc in result.scalars().all():
        acc.is_default = False

    # Set new default
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_default = True
    await db.commit()

    return AccountResponse(**account.to_dict())
