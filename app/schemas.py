from datetime import date
from pydantic import BaseModel, ConfigDict, Field
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str
    password: str = Field(min_length=8)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class AssetCreate(BaseModel):
    asset_id: str
    name: str
    description: str | None = None
    serial_number: str | None = None
    model: str | None = None
    brand: str | None = None
    purchase_date: date | None = None
    purchase_price: float | None = None
    warranty_expiry: date | None = None
    status: str = "available"
    category_id: int | None = None
    department_id: int | None = None
    location: str | None = None
    notes: str | None = None
class AssetOut(AssetCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
class MaintenanceCreate(BaseModel):
    asset_id: int
    maintenance_type: str = "routine"
    title: str
    description: str | None = None
    scheduled_date: date | None = None
    cost: float | None = None
    status: str = "scheduled"
    performed_by: str | None = None
    notes: str | None = None
class AssignmentCreate(BaseModel):
    asset_id: int
    employee_id: int
    expected_return_date: date | None = None
    condition: str | None = None
    notes: str | None = None
