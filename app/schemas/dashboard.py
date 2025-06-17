from pydantic import BaseModel

class DashboardKPIS(BaseModel):
    new_policies_this_month: int
    outstanding_premiums_total: float
    broker_count: int

class RecentPolicy(BaseModel):
    policy_number: str
    customer_name: str
    broker: str

class DashboardData(BaseModel):
    kpis: DashboardKPIS
    recent_policies: list[RecentPolicy] 