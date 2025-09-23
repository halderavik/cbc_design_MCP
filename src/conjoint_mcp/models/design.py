from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Design(BaseModel):
    """
    Internal design structure used across handlers.
    """

    tasks: List[dict]


