from __future__ import annotations

from fastapi import File, FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError, field_validator
from starlette.middleware.sessions import SessionMiddleware

from app.core.settings import settings
from app.routers import api
from app.services.db import (
    authenticate_user,
    create_user,
    init_db,
    list_diagnosis_history,
    list_interests,
    update_user_profile,
)
from app.services.demo_data import REGION_OPTIONS, get_crop_schedule, get_dashboard_context, get_grants, get_pest_guides, normalize_region
from app.services.diagnosis import predict_disease
from app.services.public_data import CROP_NAMES, fetch_support_detail, search_consults, search_pests

app = FastAPI(
    title="Deulmaru v2",
    description="Public-data based farming decision dashboard for contest demo.",
    version="0.4.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app_secret_key,
    session_cookie="__session",
    same_site="lax",
    https_only=True,
)
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
    interests = list_interests(session_user["id"])
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            **get_dashboard_context(user=session_user, diagnosis_history=diagnosis_history),
            "session_user": session_user,
            "interests": interests,
        },
    )


@app.post("/")
async def dashboard_post_redirect() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


def require_user(request: Request) -> dict | RedirectResponse:
    session_user = request.session.get("user")
    if not session_user:
        return RedirectResponse(url="/login", status_code=303)
    return session_user


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    user_id: str = Form(""),
    password: str = Form(""),
    userId: str = Form(""),
    userPw: str = Form(""),
) -> HTMLResponse:
    login_id = (user_id or userId).strip()
    login_password = password or userPw
    if not login_id or not login_password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "아이디와 비밀번호를 입력해 주세요.",
            },
            status_code=400,
        )

    try:
        user = authenticate_user(login_id, login_password)
    except Exception:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "로그인 처리 중 서버 오류가 발생했습니다. Firestore 권한과 환경변수를 확인해 주세요.",
            },
            status_code=500,
        )

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


@app.get("/auth/login", response_class=HTMLResponse)
@app.get("/auth/deulmaru_Login", response_class=HTMLResponse)
async def legacy_login_page(request: Request) -> HTMLResponse:
    return await login_page(request)


@app.post("/auth/login", response_class=HTMLResponse)
async def legacy_login(
    request: Request,
    user_id: str = Form(""),
    password: str = Form(""),
    userId: str = Form(""),
    userPw: str = Form(""),
) -> HTMLResponse:
    return await login(request, user_id=user_id, password=password, userId=userId, userPw=userPw)


@app.get("/auth/logout")
async def legacy_logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request) -> HTMLResponse:
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@app.get("/auth/register-options", response_class=HTMLResponse)
@app.get("/auth/signin", response_class=HTMLResponse)
@app.get("/auth/deulmaru_SignIn_Main", response_class=HTMLResponse)
async def legacy_register_options(request: Request) -> HTMLResponse:
    return await signup_page(request)


@app.get("/auth/register", response_class=HTMLResponse)
@app.get("/auth/deulmaru_SignIn", response_class=HTMLResponse)
async def legacy_register_page(request: Request) -> HTMLResponse:
    return await signup_page(request)


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


@app.post("/auth/register", response_class=HTMLResponse)
async def legacy_register(
    request: Request,
    userId: str = Form(...),
    userPw: str = Form(...),
    userNickname: str = Form(...),
    userEmail: str = Form(""),
    userLocate: str = Form("지역 미입력"),
    userBirth: str = Form(""),
    userGender: str = Form(""),
) -> HTMLResponse:
    return await signup(
        request,
        user_id=userId,
        password=userPw,
        name=userNickname or userEmail or userId,
        region=userLocate,
        crop="토마토",
    )


@app.get("/support", response_class=HTMLResponse)
async def support_page(
    request: Request,
    keyword: str = "",
    region: str = "",
    age: int | None = None,
    status: str = "",
    start_date: str = "",
    end_date: str = "",
) -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    selected_region = normalize_region(region or session_user.get("region", "전국"))
    grants = get_grants(
        session_user,
        keyword=keyword,
        region=selected_region,
        age=age,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return templates.TemplateResponse(
        "support.html",
        {
            "request": request,
            "session_user": session_user,
            "grants": grants,
            "filters": {
                "keyword": keyword,
                "region": selected_region,
                "age": age or "",
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
            },
            "region_options": REGION_OPTIONS,
        },
    )


@app.get("/supportApi/support", response_class=HTMLResponse)
async def legacy_support_page(
    request: Request,
    keyword: str = "",
    region: str = "",
    age: int | None = None,
    status: str = "",
    start_date: str = "",
    end_date: str = "",
) -> HTMLResponse:
    return await support_page(
        request,
        keyword=keyword,
        region=region,
        age=age,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@app.get("/support/{grant_id}", response_class=HTMLResponse)
async def support_detail_page(request: Request, grant_id: str) -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    fallback = next((item for item in get_grants(session_user) if item["id"] == grant_id), None)
    detail = fetch_support_detail(grant_id)
    if not detail and fallback:
        detail = {
            "id": fallback["id"],
            "title": fallback["title"],
            "target": fallback["reason"],
            "period": fallback["deadline"],
            "agency": fallback["source"],
            "content": fallback["reason"],
            "url": "",
        }
    return templates.TemplateResponse(
        "support_detail.html",
        {"request": request, "session_user": session_user, "grant": detail, "grant_id": grant_id},
    )


@app.get("/supportApi/detail/{seq}", response_class=HTMLResponse)
async def legacy_support_detail_page(request: Request, seq: str) -> HTMLResponse:
    return await support_detail_page(request, seq)


@app.get("/dictionary", response_class=HTMLResponse)
async def dictionary_page(request: Request, query: str = "토마토", search_type: str = "crop") -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    return templates.TemplateResponse(
        "dictionary.html",
        {
            "request": request,
            "session_user": session_user,
            "query": query,
            "search_type": search_type,
            "pests": get_pest_guides(query),
        },
    )


@app.get("/auth/deulmaru_dictionary", response_class=HTMLResponse)
async def legacy_dictionary_page(request: Request) -> HTMLResponse:
    return await dictionary_page(request)


@app.get("/diagnosis", response_class=HTMLResponse)
async def diagnosis_page(request: Request) -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    return templates.TemplateResponse(
        "diagnosis.html",
        {
            "request": request,
            "session_user": session_user,
            "history": list_diagnosis_history(session_user["id"]),
            "crop_names": CROP_NAMES,
        },
    )


@app.get("/auth/deulmaru_Diagnosis", response_class=HTMLResponse)
async def legacy_diagnosis_page(request: Request) -> HTMLResponse:
    return await diagnosis_page(request)


@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request) -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    return templates.TemplateResponse(
        "mypage.html",
        {
            "request": request,
            "session_user": session_user,
            "interests": list_interests(session_user["id"]),
            "history": list_diagnosis_history(session_user["id"]),
            "schedule": get_crop_schedule(session_user["crop"]),
            "crop_names": CROP_NAMES,
            "message": None,
        },
    )


@app.get("/auth/mypage", response_class=HTMLResponse)
async def legacy_auth_mypage(request: Request) -> HTMLResponse:
    return await mypage(request)


@app.post("/mypage", response_class=HTMLResponse)
async def update_mypage(
    request: Request,
    name: str = Form(...),
    region: str = Form(...),
    crop: str = Form(...),
    password: str = Form(""),
) -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    user = update_user_profile(session_user["id"], name=name, region=region, crop=crop, password=password)
    request.session["user"] = user
    return templates.TemplateResponse(
        "mypage.html",
        {
            "request": request,
            "session_user": user,
            "interests": list_interests(user["id"]),
            "history": list_diagnosis_history(user["id"]),
            "schedule": get_crop_schedule(user["crop"]),
            "crop_names": CROP_NAMES,
            "message": "회원 정보가 저장되었습니다.",
        },
    )


@app.post("/mypage/update-profile", response_class=HTMLResponse)
async def legacy_update_profile(
    request: Request,
    userNickname: str = Form(...),
    userPw: str = Form(""),
    userLocate: str = Form(...),
    userCrop: str = Form("토마토"),
) -> HTMLResponse:
    return await update_mypage(
        request,
        name=userNickname,
        region=userLocate,
        crop=userCrop,
        password=userPw,
    )


@app.post("/mypage/update-crop")
async def legacy_update_crop(request: Request, userCrop: str = Form(...)) -> dict:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return {"ok": False, "message": "로그인이 필요합니다."}
    user = update_user_profile(
        session_user["id"],
        name=session_user["name"],
        region=session_user["region"],
        crop=userCrop,
    )
    request.session["user"] = user
    return {"ok": True, "message": "재배작물 정보가 업데이트되었습니다."}


@app.get("/qna", response_class=HTMLResponse)
async def qna_page(request: Request, query: str = "토마토") -> HTMLResponse:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return session_user
    return templates.TemplateResponse(
        "qna.html",
        {"request": request, "session_user": session_user, "query": query},
    )


@app.get("/auth/deulmaru_QnA", response_class=HTMLResponse)
async def legacy_qna_page(request: Request) -> HTMLResponse:
    return await qna_page(request)


@app.get("/ncpms/search")
async def legacy_ncpms_search(query: str, type: str = "sick") -> dict:
    return {"items": search_pests(query, "crop" if type == "crop" else "sick")}


@app.get("/ncpms/sick_detail")
async def legacy_ncpms_sick_detail(sick_key: str) -> dict:
    # Existing frontend can still use the list payload; detailed fallback keeps the route alive.
    return {"sick_key": sick_key, "detail": "상세 정보는 병해충 사전 검색 결과와 NCPMS 원문을 함께 확인하세요."}


@app.get("/ncpms/consult")
async def legacy_ncpms_consult(query: str, page: int = 1) -> dict:
    return {"items": search_consults(query, page)}


@app.get("/ncpms/consult_detail")
async def legacy_ncpms_consult_detail(consult_id: str) -> dict:
    return {"consult_id": consult_id, "detail": "상담 상세 정보는 검색 결과 요약을 기준으로 확인하세요."}


@app.post("/upload")
async def legacy_upload(
    request: Request,
    file: UploadFile = File(...),
    cropName: str = Form("토마토"),
) -> dict:
    session_user = require_user(request)
    if isinstance(session_user, RedirectResponse):
        return {"message": "로그인이 필요합니다."}
    result = await predict_disease(crop_name=cropName, file=file)
    if result.get("ok"):
        return {
            "prediction": f"{result['disease']} ({result['confidence']}%)",
            "imageUrl": "",
            **result,
        }
    return {"message": result.get("message", "진단에 실패했습니다.")}


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
