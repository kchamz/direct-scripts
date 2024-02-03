import uuid
from typing import Optional

from pydantic import BaseModel


class Locks(BaseModel):
    book: bool = True
    contact_edit: bool = True
    delete: bool = True
    download: bool = True
    edit: bool = True
    hold: bool = True
    sync: bool = True
    sync_button: bool = True


class ProposalCreate(BaseModel):
    discount: float = 0
    name: str = str(uuid.uuid4())
    owner_email: Optional[str] = None
    owner_user_id: Optional[int] = None
    price: float = 0
    contract_id: str = ""
    contract_number: str = ""
    description: str = ""
    locks: Locks = Locks()
    picture: str = ""
    proposal_amended: bool = False
