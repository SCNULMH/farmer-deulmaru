# 들마루 v2

청년농/귀농 초기 사용자를 위한 FastAPI 기반 공공데이터 맞춤형 대시보드입니다. 회원가입 후 사용자 지역과 작물을 저장하고, 지원사업 추천, 재배 일정, 병해충 가이드, AI 진단 기록을 한 화면에서 확인합니다.

## 실행

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru\deulmaru_v2
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

접속: `http://127.0.0.1:8000`

데모 계정:

- 아이디: `demo`
- 비밀번호: `demo1234`

## 회원가입과 저장소

- `/signup`에서 아이디, 비밀번호, 이름, 지역, 주요 작물을 입력합니다.
- 로컬 개발 기본값은 `DATABASE_BACKEND=sqlite`이며 `data/deulmaru.sqlite3`에 저장됩니다.
- 배포 환경은 `DATABASE_BACKEND=firebase`를 사용해 Firestore `users/{user_id}` 문서에 저장합니다.
- 관심 지원사업과 진단 기록은 Firestore에서는 사용자 문서 하위 컬렉션으로 저장됩니다.

## 환경변수

`.env.example`을 복사해 `.env`를 만들고 필요한 값을 채웁니다.

```powershell
Copy-Item .env.example .env
```

주요 값:

- `APP_SECRET_KEY`: 세션 서명 키
- `DATABASE_BACKEND`: `sqlite` 또는 `firebase`
- `USE_DEMO_DATA`: `true`면 외부 API 대신 데모 데이터를 우선 사용
- `SUPPORT_API_SERVICE_KEY`, `NCPMS_API_KEY`, `NONGSARO_API_KEY`: 공공데이터 API 키
- `FIREBASE_CREDENTIALS_JSON`: 서비스 계정 JSON을 한 줄 환경변수로 등록
- `GOOGLE_APPLICATION_CREDENTIALS`: 로컬 서비스 계정 파일 경로

## API Fallback

`USE_DEMO_DATA=true`이면 항상 `app/services/demo_data.py`의 데모 데이터를 사용합니다. `USE_DEMO_DATA=false`여도 외부 API 키가 없거나 통신 장애가 발생하면 데모 데이터로 자동 fallback합니다.

## 배포

Firebase Hosting은 고정 제출 URL을 제공하고, Cloud Run은 FastAPI 서버를 실행합니다.

1. GitHub 저장소를 Cloud Shell에서 pull 합니다.
2. `deulmaru_v2` 폴더를 Cloud Run 서비스 `deulmaru-v2`로 배포합니다.
3. Firebase Hosting rewrite가 Cloud Run으로 요청을 전달합니다.
4. 필요한 공공데이터 API 키를 Cloud Run 환경변수에 등록합니다.
5. 배포 후 `/health`가 `{"status":"ok"}`를 반환하는지 확인합니다.

컨테이너 배포 환경의 ephemeral filesystem 제약 때문에 사용자 업로드 이미지는 저장하지 않습니다. 진단 기능은 파일 내용을 읽어 결과만 DB에 기록합니다.

## 구조

```text
deulmaru_v2/
  app/
    main.py                 # 페이지 라우트, 로그인, 회원가입
    routers/api.py          # 대시보드 API
    services/db.py          # SQLite/Firestore 저장소 추상화
    services/demo_data.py   # 외부 API fallback 데이터
    services/public_data.py # 공공데이터 API 클라이언트
    services/diagnosis.py   # 교체 가능한 진단 어댑터
    templates/
    static/
  render.yaml
  requirements.txt
```
