from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.core.settings import settings
from app.routers import api
from app.services.db import authenticate_user, init_db, list_diagnosis_history
from app.services.demo_data import get_dashboard_context

app = FastAPI(
    title="Deulmaru v2",
    description="Public-data based farming decision dashboard for contest demo.",
    version="0.2.0",
)

app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(api.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    session_user = request.session.get("user")
    if not session_user:
        return RedirectResponse(url="/login", status_code=303)

    diagnosis_history = list_diagnosis_history(session_user["id"])
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            **get_dashboard_context(user=session_user, diagnosis_history=diagnosis_history),
            "session_user": session_user,
        },
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, user_id: str = Form(...), password: str = Form(...)) -> HTMLResponse:
    user = authenticate_user(user_id, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "아이디 또는 비밀번호를 확인해 주세요. 데모 계정은 demo / demo1234 입니다.",
            },
            status_code=400,
        )

    request.session["user"] = user
    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
