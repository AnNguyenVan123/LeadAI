from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class AnalyzeRequest(BaseModel):
    kind: Literal["url", "text"] = "text"
    value: str = Field(min_length=10, max_length=20000)
    live: bool = False          # True = scan Reddit now instead of the cached corpus


class Evidence(BaseModel):
    label: str
    present: bool
    quote: str = ""


class Lead(BaseModel):
    title: str
    subreddit: str
    author: str
    url: str
    author_url: str = ""
    age: str
    tier: Literal["hot", "warm", "cool"]
    score: int
    factors: dict[str, int]
    problem: str
    one_line: str
    evidence: list[Evidence]
    why: str
    risk: str = ""
    gate: str = ""
    draft: str


class ICP(BaseModel):
    product: str
    problem: str
    buyer: str
    not_buyer: list[str] = []
    subreddits: list[str] = []
    confidence: Literal["high", "medium", "low"] = "medium"
    note: str = ""


class RunResult(BaseModel):
    run_id: str
    icp: ICP
    scanned: int
    funnel: list[dict]
    leads: list[Lead]          # only the unlocked ones unless an email was given
    locked_count: int
    unlocked: bool


class UnlockRequest(BaseModel):
    run_id: str
    email: EmailStr


class SaveLeadRequest(BaseModel):
    run_id: str = ""
    title: str = ""
    author: str = ""
    url: str = ""
    problem: str = ""
    stage: str = ""


class UpdateLeadRequest(BaseModel):
    notes: str | None = None
    status: str | None = None


class SavedLead(BaseModel):
    id: str
    run_id: str
    title: str
    author: str
    url: str
    problem: str
    stage: str
    saved_at: float
    notes: str
    status: str
