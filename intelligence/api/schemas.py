from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StrategySummary(BaseModel):
    strategy_id: str
    name: str
    version: str
    stage: str
    ssr: float
    status: str


class StrategyMetricView(BaseModel):
    snapshot_id: str
    stage: str
    ssr: float
    total_trades: int
    max_drawdown: float
    avg_r: float
    expectancy: float
    created_at: datetime


class SymbolMetricView(BaseModel):
    symbol: str
    total_trades: int
    ssr: float
    avg_r: float
