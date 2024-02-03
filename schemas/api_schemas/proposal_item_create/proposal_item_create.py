import uuid
from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel


class Values(BaseModel):
    average_sov_lower_boundary: int = 0
    average_sov_upper_boundary: int = 0
    goal: int = 0
    goal_impressions_upper_boundary: int = 0
    saturation: int = 1
    sov: int = 0
    target_sov: int = 0


class BuyMode(BaseModel):
    subtype: str = "plays_per_loop"
    type: str = "frequency"
    values: Values = Values()


class ScreenSelectionMode(BaseModel):
    type: str = "all"


class ProposalItemCreate(BaseModel):
    buy_mode: BuyMode = BuyMode()
    custom_screen_ids: List[str] = []
    dow_mask: int = 127
    end_date: datetime = datetime.now()
    end_time: time = time.max
    is_preemptible: bool = False
    name: str = str(uuid.uuid4())
    price: float = 0
    priority: int = 3
    reference_id: str = ""
    screen_selection_mode: ScreenSelectionMode = ScreenSelectionMode()
    slot_duration: float = 0.1
    start_date: datetime = datetime.now()
    start_time: time = time.min

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.strftime("%Y-%m-%d"),
            time: lambda t: t.strftime("%H:%M:%S")
        }


class ProposalProposalItemCreate(BaseModel):
    line_items: Optional[List[ProposalItemCreate]] = None
    proposal_id: Optional[int] = None
