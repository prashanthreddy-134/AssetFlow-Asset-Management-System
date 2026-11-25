from datetime import datetime, date
from sqlalchemy import String, Integer, Text, DateTime, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AssetCategory(Base):
    __tablename__ = "asset_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assets = relationship("Asset", back_populates="category")

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    employees = relationship("Employee", back_populates="department")
    assets = relationship("Asset", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="employees")
    assignments = relationship("AssetAssignment", back_populates="employee")

class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(Numeric(10,2), nullable=True)
    warranty_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("asset_categories.id"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("AssetCategory", back_populates="assets")
    department = relationship("Department", back_populates="assets")
    assignments = relationship("AssetAssignment", back_populates="asset")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")

class AssetAssignment(Base):
    __tablename__ = "asset_assignments"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    assigned_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    returned_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expected_return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    maintenance_type: Mapped[str] = mapped_column(String(20), default="routine")
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric(10,2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    performed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset = relationship("Asset", back_populates="maintenance_records")

class AssetAudit(Base):
    __tablename__ = "asset_audits"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    audit_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    auditor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    asset = relationship("Asset")

class AssetDisposal(Base):
    __tablename__ = "asset_disposals"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), unique=True)
    disposal_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reason: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposal_value: Mapped[float | None] = mapped_column(Numeric(10,2), nullable=True)
    asset = relationship("Asset")

class AssetReport(Base):
    __tablename__ = "asset_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[str] = mapped_column(String(50))
    generated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
