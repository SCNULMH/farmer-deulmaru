# 들마루 v2

공모전 제출용으로 새로 구성하는 Python/FastAPI 버전입니다. 기존 Spring 프로젝트는 보존하고, v2는 `개인화 농업 의사결정 대시보드`를 중심으로 다시 설계합니다.

## 목표

- 공공데이터 활용성이 첫 화면에서 드러나는 구조
- 청년농/귀농 초기 사용자를 위한 맞춤 지원사업, 재배 일정, 병해충 진단 흐름
- 기존 팀 코드와 UI를 그대로 재사용하지 않는 새 구현
- 실제 API/AI 모델 연결 전에도 공모전 시연이 가능한 데모 모드

## 실행

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru\deulmaru_v2
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## 데모 로그인

- 아이디: `demo`
- 비밀번호: `demo1234`

현재 로그인은 SQLite 사용자 테이블을 사용하는 데모 로그인입니다. 실제 서비스 계정 정책은 추후 비밀번호 해시 강화와 카카오 로그인 연결로 확장합니다.

## API 키 설정

현재 v2는 기존 Spring 프로젝트의 API 키를 `.env`로 옮겨 실제 API 호출을 수행합니다. API 장애나 빈 응답이 있으면 샘플 데이터 fallback을 사용합니다.

```powershell
Copy-Item .env.example .env
```

`.env`에 다음 값을 채웁니다.

- `SUPPORT_API_SERVICE_KEY`: 청년농 지원사업 API 키
- `NCPMS_API_KEY`: NCPMS API 키
- `NONGSARO_API_KEY`: 농사로 API 키
- `KAKAO_CLIENT_ID`: 카카오 로그인 client id

`USE_DEMO_DATA=false`이면 실제 API를 우선 호출합니다. `USE_DEMO_DATA=true`이면 실제 API 대신 샘플 데이터를 사용합니다.

현재 로컬 검증 완료:

- 청년농 지원사업 API: 실제 목록 수신 완료
- 농사로 작물 재배 일정 API: 토마토 일정 수신 완료
- NCPMS 병해충 API: 고추 병해충 목록 수신 완료

## DB

저장소는 환경변수로 선택합니다.

- 로컬 기본값: `DATABASE_BACKEND=sqlite`
- 제출/배포 권장값: `DATABASE_BACKEND=firebase`

SQLite는 로컬 개발에는 빠르지만 Render 배포 환경에서는 파일 저장이 안정적이지 않습니다. 공모전 제출용 공개 URL은 Firebase Firestore를 권장합니다. 자세한 구성안은 `DEPLOYMENT_PLAN.md`를 참고하세요.

## 배포

Render 배포용 파일을 포함했습니다.

- `render.yaml`
- `Procfile`
- `runtime.txt`

Render에서 GitHub repo를 연결하고, 환경변수에 API 키와 `APP_SECRET_KEY`를 넣으면 됩니다.

## 구조

```text
deulmaru_v2/
  app/
    main.py
    core/
      settings.py
    routers/
      api.py
    services/
      db.py
      demo_data.py
      diagnosis.py
    templates/
      login.html
      dashboard.html
    static/
      css/dashboard.css
      js/dashboard.js
  data/
  requirements.txt
```

## 다음 작업

1. 실제 공공데이터 API 클라이언트 추가
   - 청년농 지원사업: 완료
   - 농사로 작물 일정: 완료
   - NCPMS 병해충 정보: 완료

2. 진단 모델 어댑터 교체
   - 현재 `app/services/diagnosis.py`는 데모 응답을 반환합니다.
   - 이후 PyTorch 모델을 연결해도 라우트와 화면은 유지됩니다.

3. Firebase Firestore 전환
   - Render 환경변수에 `DATABASE_BACKEND=firebase`를 등록합니다.
   - Render 환경변수에 `FIREBASE_CREDENTIALS_JSON`을 등록합니다.

4. 기획서 문장과 화면 문구 정리
   - 공공데이터 활용성, 구체성, 독창성, 발전 가능성, 시의성을 발표자료에 맞춰 다듬습니다.
