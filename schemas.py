from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field


# What company wants to buy
class PurchaseRequest(BaseModel):
    department: str
    item: str
    quantity: int = Field(gt=0)
    max_budget: int = Field(gt=0)
    required_delivery_days: int = Field(gt=0)
    
# Supplier's offer
class SupplierQuote(BaseModel):
    supplier: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_price: float = Field(gt=0)
    delivery_days: int = Field(gt=0)
    warranty_months: int
    
# Whether the supplier is approved
class SupplierStatus(BaseModel):
    supplier: str
    status: bool
    
# Result of budget check tool
class BudgetResult(BaseModel):
    department: str
    remaining_budget: float
    requested_budget: float = Field(gt=0)
    within_budget: bool
    
# What RAG found in Policy documents
class PolicyResult(BaseModel):
    content: str
    source: str
    
# Procurement Agent result
class ProcurementState(BaseModel):
    request: PurchaseRequest
    supplier_statuses: List[SupplierStatus] = []
    quotes: List[SupplierQuote] = []
    budget_results: List[BudgetResult] = []
    policy_results: List[PolicyResult] = []
    recommendation: Optional[str] = None