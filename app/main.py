from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models import Account, Proxy, Profile, Binding
from app.services.adspower_client import adspower
from app.services.logger import logger
from app.services.automation import automation
from app.services.antigravity_launcher import antigravity_launcher
from app.api.v1 import router as v1_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="AntiProxy", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.include_router(v1_router)
templates = Jinja2Templates(directory="app/templates")

def get_current_user(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=303, detail="Not authenticated")
    return True

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == settings.ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login", "error": "Invalid password"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    accounts_count = db.query(Account).count()
    bindings = db.query(Binding).all()
    all_accounts = db.query(Account).all()
    all_proxies = db.query(Proxy).all()
    active_profiles_count = db.query(Profile).filter(Profile.status == "active").count()
    adspower_ok = adspower.check_status()
    logs = logger.get_logs()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Dashboard",
        "accounts_count": accounts_count,
        "adspower_ok": adspower_ok,
        "active_profiles_count": active_profiles_count,
        "bindings": bindings,
        "all_accounts": all_accounts,
        "all_proxies": all_proxies,
        "logs": logs
    })

@app.get("/api/logs")
def get_logs():
    return logger.get_logs()

@app.post("/api/bindings/create")
def create_binding(
    account_id: int = Form(None),
    proxy_id: int = Form(None),
    profile_name: str = Form(...),
    db: Session = Depends(get_db)
):
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first() if proxy_id else None
    
    adspower_id = adspower.create_profile(name=profile_name, proxy=proxy)
    
    if not adspower_id:
        adspower_id = f"local_{profile_name}"
    
    profile = Profile(adspower_id=adspower_id, name=profile_name)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    logger.info(f"Created profile: {profile_name} (AdsPower ID: {adspower_id})")
    
    binding = Binding(
        account_id=account_id if account_id else None,
        proxy_id=proxy_id if proxy_id else None,
        profile_id=profile.id
    )
    db.add(binding)
    db.commit()
    
    adspower.start_profile(adspower_id)
    profile.status = "active"
    db.commit()
    logger.info(f"Launched profile: {profile_name}")
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse("<script>window.location.href='/'</script>")

@app.post("/api/launch/{binding_id}")
def launch_binding(binding_id: int, db: Session = Depends(get_db)):
    binding = db.query(Binding).filter(Binding.id == binding_id).first()
    if binding and binding.profile:
        adspower.start_profile(binding.profile.adspower_id)
        binding.profile.status = "active"
        db.commit()
    return {"status": "ok"}

@app.post("/api/launch-antigravity/{binding_id}")
def launch_antigravity(binding_id: int, db: Session = Depends(get_db)):
    binding = db.query(Binding).filter(Binding.id == binding_id).first()
    if binding and binding.profile:
        success = antigravity_launcher.launch(
            profile_name=binding.profile.name,
            proxy=binding.proxy
        )
        if success:
            binding.profile.status = "active"
            db.commit()
            return {"status": "ok"}
    return {"status": "error", "message": "Failed to launch Antigravity"}

@app.post("/api/stop/{binding_id}")
def stop_binding(binding_id: int, db: Session = Depends(get_db)):
    binding = db.query(Binding).filter(Binding.id == binding_id).first()
    if binding and binding.profile:
        adspower.stop_profile(binding.profile.adspower_id)
        binding.profile.status = "stopped"
        db.commit()
        logger.info(f"Stopped profile: {binding.profile.name}")
    return {"status": "ok"}

@app.get("/accounts")
def accounts_view(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    accounts = db.query(Account).all()
    return templates.TemplateResponse("accounts.html", {"request": request, "title": "Accounts", "accounts": accounts})

@app.post("/api/accounts")
def create_account(email: str = Form(...), password: str = Form(None), db: Session = Depends(get_db)):
    acc = Account(email=email, password=password)
    db.add(acc)
    db.commit()
    from fastapi.responses import HTMLResponse
    return HTMLResponse("<script>window.location.href='/accounts'</script>")

@app.get("/proxies")
def proxies_view(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    proxies = db.query(Proxy).all()
    return templates.TemplateResponse("proxies.html", {"request": request, "title": "Proxies", "proxies": proxies})

@app.post("/api/proxies")
def create_proxy(
    name: str = Form(...), host: str = Form(...), port: int = Form(...),
    username: str = Form(None), password: str = Form(None), protocol: str = Form("socks5"),
    db: Session = Depends(get_db)
):
    prox = Proxy(name=name, host=host, port=port, username=username, password=password, protocol=protocol)
    db.add(prox)
    db.commit()
    from fastapi.responses import HTMLResponse
    return HTMLResponse("<script>window.location.href='/proxies'</script>")

@app.get("/automation")
def automation_view(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login")
    bindings = db.query(Binding).all()
    return templates.TemplateResponse("automation.html", {
        "request": request,
        "title": "Automation",
        "bindings": bindings
    })

@app.post("/api/automation/run")
async def run_automation(binding_id: int = Form(...), script: str = Form(...), db: Session = Depends(get_db)):
    binding = db.query(Binding).filter(Binding.id == binding_id).first()
    if not binding or not binding.profile:
        return {"status": "error", "message": "Binding or profile not found"}
    
    # Check if we are launching in AdsPower or Antigravity
    # For now, assume AdsPower if adspower is reachable, else try CDP on 9223
    ws_endpoint = None
    res = adspower.start_profile(binding.profile.adspower_id)
    if res and "ws" in res:
        ws_endpoint = res["ws"]["puppeteer"]
    else:
        # Fallback to Antigravity port if AdsPower fails
        ws_endpoint = "ws://localhost:9223/devtools/browser"
        logger.info(f"AdsPower not responding. Trying Antigravity CDP on {ws_endpoint}")
    
    import asyncio
    asyncio.create_task(automation.run_script(ws_endpoint, script))
    
    return {"status": "ok", "message": "Automation started"}

@app.post("/api/ai/command")
async def ai_command(command: str = Form(...), binding_id: int = Form(...), db: Session = Depends(get_db)):
    binding = db.query(Binding).filter(Binding.id == binding_id).first()
    if not binding or not binding.profile:
        return {"status": "error", "message": "Binding not found"}
    
    logger.info(f"AI Agent processing command: {command}")
    
    # In a real scenario, this would call an LLM.
    # For now, we map keywords to existing scripts or custom logic.
    script = "warmup"
    if "login" in command.lower() or "google" in command.lower():
        script = "check_login"
    
    # Trigger automation
    return await run_automation(binding_id=binding_id, script=script, db=db)

@app.post("/api/proxies/check/{proxy_id}")
def check_proxy(proxy_id: int, db: Session = Depends(get_db)):
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        return {"status": "error", "message": "Proxy not found"}
    
    # For SOCKS5, use socks5h to ensure DNS resolution happens through the proxy
    protocol = proxy.protocol
    if protocol == "socks5":
        protocol = "socks5h"
        
    proxies = {
        "http": f"{protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}" if proxy.username else f"{protocol}://{proxy.host}:{proxy.port}",
        "https": f"{protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}" if proxy.username else f"{protocol}://{proxy.host}:{proxy.port}"
    }
    
    try:
        import requests
        # Using a reliable IP check service
        res = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
        if res.ok:
            ip = res.json().get("ip")
            logger.info(f"Proxy {proxy.name} is working. IP: {ip}")
            return {"status": "ok", "ip": ip}
        else:
            return {"status": "error", "message": f"HTTP {res.status_code}"}
    except Exception as e:
        logger.error(f"Proxy {proxy.name} failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    return {"status": "error", "message": "Unknown error"}
