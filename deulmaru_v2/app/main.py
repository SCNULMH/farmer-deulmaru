from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError, field_validator
from starlette.middleware.sessions import SessionMiddleware

from app.core.settings import settings
from app.routers import api
from app.services.db import authenticate_user, create_user, init_db, list_diagnosis_history
from app.services.demo_data import get_dashboard_context

app = FastAPI(
    title="Deulmaru v2",
    description="Public-data based farming decision dashboard for contest demo.",
    version="0.4.0",
)

app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(api.router, prefix="/api")


class SignupForm(BaseModel):
    user_id: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=2, max_length=40)
    region: str = Field(min_length=2, max_length=60)
    crop: str = Field(min_length=1, max_length=40)

    @field_validator("user_id", "name", "region", "crop", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    def to_user_dict(self) -> dict[str, str]:
        return {
            "id": self.user_id,
            "password": self.password,
            "name": self.name,
            "region": self.region,
            "crop": self.crop,
        }


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
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
async def login_page(request: Request) -> HTMLResponse:
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, user_id: str = Form(...), password: str = Form(...)) -> HTMLResponse:
    user = authenticate_user(user_id.strip(), password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "아이디 또는 비밀번호가 맞지 않습니다. 데모 계정은 demo / demo1234 입니다.",
            },
            status_code=400,
        )

    request.session["user"] = user
    return RedirectResponse(url="/", status_code=303)


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request) -> HTMLResponse:
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@app.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    user_id: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    region: str = Form(...),
    crop: str = Form(...),
) -> HTMLResponse:
    try:
        form = SignupForm(
            user_id=user_id,
            password=password,
            name=name,
            region=region,
            crop=crop,
        )
        user = create_user(form.to_user_dict())
    except ValidationError:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "아이디는 영문/숫자/_/- 3자 이상, 비밀번호는 8자 이상으로 입력해 주세요.",
            },
            status_code=400,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": str(exc)},
            status_code=400,
        )

    request.session["user"] = user
    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "database_backend": settings.database_backend,
        "use_demo_data": settings.use_demo_data,
    }
