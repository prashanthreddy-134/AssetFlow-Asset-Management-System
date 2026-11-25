from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Asset, AssetCategory, Department, Employee, AssetAssignment, MaintenanceRecord, AssetAudit, AssetDisposal
from ..schemas import UserCreate, Token, AssetCreate, AssetOut, MaintenanceCreate, AssignmentCreate
from ..auth import hash_password, verify_password, create_access_token, get_current_user
router = APIRouter(prefix="/api")

@router.post("/auth/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first():
        raise HTTPException(409, "Username or email already exists")
    db.add(User(username=payload.username, email=payload.email, hashed_password=hash_password(payload.password)))
    db.commit()
    return {"message":"User registered"}

@router.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect username or password")
    return {"access_token":create_access_token(user.username), "token_type":"bearer"}

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"assets":db.query(Asset).count(),"available":db.query(Asset).filter_by(status="available").count(),
            "assigned":db.query(Asset).filter_by(status="assigned").count(),
            "maintenance":db.query(Asset).filter(Asset.status.in_(["maintenance","repair"])).count(),
            "employees":db.query(Employee).count()}

@router.get("/assets", response_model=list[AssetOut])
def list_assets(q: str = "", status: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query=db.query(Asset)
    if q: query=query.filter((Asset.name.contains(q)) | (Asset.asset_id.contains(q)) | (Asset.serial_number.contains(q)))
    if status: query=query.filter(Asset.status==status)
    return query.order_by(Asset.created_at.desc()).all()

@router.post("/assets", response_model=AssetOut)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.query(Asset).filter_by(asset_id=payload.asset_id).first(): raise HTTPException(409,"Asset ID already exists")
    item=Asset(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.get("/assets/{pk}", response_model=AssetOut)
def get_asset(pk:int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    item=db.get(Asset,pk)
    if not item: raise HTTPException(404,"Asset not found")
    return item

@router.put("/assets/{pk}", response_model=AssetOut)
def update_asset(pk:int, payload:AssetCreate, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    item=db.get(Asset,pk)
    if not item: raise HTTPException(404,"Asset not found")
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    db.commit(); db.refresh(item); return item

@router.delete("/assets/{pk}")
def delete_asset(pk:int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    item=db.get(Asset,pk)
    if not item: raise HTTPException(404,"Asset not found")
    if item.status=="assigned": raise HTTPException(400,"Return assigned asset before deletion")
    db.delete(item); db.commit(); return {"message":"Asset deleted"}

@router.get("/categories")
def categories(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(AssetCategory).order_by(AssetCategory.name).all()

@router.post("/categories")
def add_category(name:str, description:str="", db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    if db.query(AssetCategory).filter_by(name=name).first(): raise HTTPException(409,"Category already exists")
    x=AssetCategory(name=name,description=description); db.add(x); db.commit(); db.refresh(x); return x

@router.get("/departments")
def departments(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(Department).all()

@router.post("/departments")
def add_department(name:str, code:str, description:str="", db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    x=Department(name=name,code=code,description=description); db.add(x); db.commit(); db.refresh(x); return x

@router.get("/employees")
def employees(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(Employee).all()

@router.post("/employees")
def add_employee(employee_id:str,name:str,email:str,department_id:int|None=None,phone:str="",position:str="",db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    x=Employee(employee_id=employee_id,name=name,email=email,department_id=department_id,phone=phone,position=position)
    db.add(x); db.commit(); db.refresh(x); return x

@router.get("/assignments")
def assignments(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(AssetAssignment).order_by(AssetAssignment.assigned_date.desc()).all()

@router.post("/assignments")
def assign(payload:AssignmentCreate, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    asset=db.get(Asset,payload.asset_id); employee=db.get(Employee,payload.employee_id)
    if not asset or not employee: raise HTTPException(404,"Asset or employee not found")
    if asset.status!="available": raise HTTPException(400,"Only available assets can be assigned")
    x=AssetAssignment(**payload.model_dump()); asset.status="assigned"; db.add(x); db.commit(); db.refresh(x)
    return {"message":"Asset assigned","assignment_id":x.id}

@router.post("/assignments/{pk}/return")
def return_asset(pk:int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    x=db.get(AssetAssignment,pk)
    if not x or x.returned_date: raise HTTPException(404,"Active assignment not found")
    x.returned_date=datetime.utcnow(); x.asset.status="available"; db.commit()
    return {"message":"Asset returned"}

@router.get("/maintenance")
def maintenance(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(MaintenanceRecord).order_by(MaintenanceRecord.id.desc()).all()

@router.post("/maintenance")
def add_maintenance(payload:MaintenanceCreate, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    asset=db.get(Asset,payload.asset_id)
    if not asset: raise HTTPException(404,"Asset not found")
    x=MaintenanceRecord(**payload.model_dump())
    if x.status in ("scheduled","in_progress"): asset.status="maintenance"
    db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/maintenance/{pk}/complete")
def complete_maintenance(pk:int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    x=db.get(MaintenanceRecord,pk)
    if not x: raise HTTPException(404,"Maintenance not found")
    x.status="completed"; x.completed_date=datetime.utcnow().date()
    if x.asset.status=="maintenance": x.asset.status="available"
    db.commit(); return {"message":"Maintenance completed"}

@router.get("/audits")
def audits(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    return db.query(AssetAudit).order_by(AssetAudit.audit_date.desc()).all()

@router.post("/audits")
def add_audit(asset_id:int,auditor:str="",condition:str="",findings:str="",status:str="pending",db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if not db.get(Asset,asset_id): raise HTTPException(404,"Asset not found")
    x=AssetAudit(asset_id=asset_id,auditor=auditor,condition=condition,findings=findings,status=status)
    db.add(x); db.commit(); db.refresh(x); return x

@router.post("/disposals")
def dispose_asset(asset_id:int,reason:str,notes:str="",disposal_value:float|None=None,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    asset=db.get(Asset,asset_id)
    if not asset: raise HTTPException(404,"Asset not found")
    if asset.status=="assigned": raise HTTPException(400,"Return assigned asset before disposal")
    x=AssetDisposal(asset_id=asset_id,reason=reason,notes=notes,disposal_value=disposal_value)
    asset.status="disposed"; db.add(x); db.commit(); return {"message":"Asset disposed"}
