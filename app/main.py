import io, os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from .database import Base, engine, get_db
from .models import Asset, Employee, Department, MaintenanceRecord, AssetAudit, AssetCategory
from .routers.api import router
APP_NAME=os.getenv("APP_NAME","Asset Management System")
Base.metadata.create_all(bind=engine)
app=FastAPI(title=APP_NAME,version="1.0.0",description="Asset tracking, assignment, maintenance and lifecycle management")
app.include_router(router)
app.mount("/static",StaticFiles(directory="app/static"),name="static")
templates=Jinja2Templates(directory="app/templates")

@app.get("/",response_class=HTMLResponse)
def dashboard(request:Request,db:Session=Depends(get_db)):
    stats={"Total assets":db.query(Asset).count(),"Available":db.query(Asset).filter_by(status="available").count(),
           "Assigned":db.query(Asset).filter_by(status="assigned").count(),"In maintenance":db.query(Asset).filter(Asset.status.in_(["maintenance","repair"])).count(),
           "Employees":db.query(Employee).count(),"Departments":db.query(Department).count()}
    recent=db.query(Asset).order_by(Asset.created_at.desc()).limit(8).all()
    return templates.TemplateResponse("dashboard.html",{"request":request,"stats":stats,"assets":recent})

@app.get("/assets",response_class=HTMLResponse)
def asset_page(request:Request,db:Session=Depends(get_db)):
    return templates.TemplateResponse("assets.html",{"request":request,"assets":db.query(Asset).order_by(Asset.created_at.desc()).all()})

@app.get("/maintenance-page",response_class=HTMLResponse)
def maintenance_page(request:Request,db:Session=Depends(get_db)):
    return templates.TemplateResponse("maintenance.html",{"request":request,"records":db.query(MaintenanceRecord).all()})

@app.get("/api/reports/summary")
def report_summary(db:Session=Depends(get_db)):
    return {"total_assets":db.query(Asset).count(),"status_counts":{s:db.query(Asset).filter_by(status=s).count() for s in ["available","assigned","maintenance","repair","disposed","lost"]},
            "employees":db.query(Employee).count(),"maintenance_records":db.query(MaintenanceRecord).count(),"audits":db.query(AssetAudit).count()}

@app.get("/reports/assets.xlsx")
def excel_report(db:Session=Depends(get_db)):
    wb=Workbook(); ws=wb.active; ws.title="Asset Inventory"
    ws.append(["Asset ID","Name","Brand","Model","Status","Location","Purchase Price"])
    for a in db.query(Asset).all(): ws.append([a.asset_id,a.name,a.brand,a.model,a.status,a.location,float(a.purchase_price or 0)])
    stream=io.BytesIO(); wb.save(stream); stream.seek(0)
    return StreamingResponse(stream,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=asset_inventory.xlsx"})

@app.get("/reports/assets.pdf")
def pdf_report(db:Session=Depends(get_db)):
    stream=io.BytesIO(); c=canvas.Canvas(stream,pagesize=A4); width,height=A4
    c.setFont("Helvetica-Bold",16); c.drawString(42,height-45,"Asset Inventory Report")
    y=height-78; c.setFont("Helvetica",9)
    for a in db.query(Asset).order_by(Asset.asset_id).all():
        c.drawString(42,y,f"{a.asset_id} | {a.name[:28]} | {a.status} | {a.location or '-'}"); y-=15
        if y<45: c.showPage(); y=height-45; c.setFont("Helvetica",9)
    c.save(); stream.seek(0)
    return StreamingResponse(stream,media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=asset_inventory.pdf"})

@app.get("/health")
def health(): return {"status":"ok","application":APP_NAME}
