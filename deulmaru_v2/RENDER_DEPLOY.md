# Render 배포 메모

들마루 v2는 `render.yaml` Blueprint 기준으로 Render Web Service에 배포한다.

## 1. Render에서 연결

1. Render.com에 로그인한다.
2. `New +` -> `Blueprint`를 선택한다.
3. GitHub 저장소 `SCNULMH/farmer-deulmaru`를 연결한다.
4. 루트의 `render.yaml`을 감지하면 그대로 생성한다.

## 2. 필수 환경변수

Blueprint 생성 화면 또는 서비스의 `Environment` 메뉴에서 아래 secret 값을 채운다.

- `SUPPORT_API_SERVICE_KEY`: 공공데이터포털 청년농 지원사업 API 인증키
- `NCPMS_API_KEY`: NCPMS 병해충 API 인증키
- `NONGSARO_API_KEY`: 농사로 API 인증키
- `FIREBASE_CREDENTIALS_JSON`: Firebase 서비스 계정 JSON 전체 내용

아래 값은 Blueprint가 자동으로 설정한다.

- `DATABASE_BACKEND=firebase`
- `USE_DEMO_DATA=false`
- `SUPPORT_API_BASE_URL=http://apis.data.go.kr/1390000/youngV2`
- `NCPMS_API_BASE_URL=http://ncpms.rda.go.kr/npmsAPI/service`
- `APP_SECRET_KEY`: Render가 자동 생성

## 3. 자동 배포

`main` 브랜치에 push하면 Render가 자동으로 다시 배포한다. Cloud Run GitHub Actions는 수동 실행으로만 남겨 두어 Firebase/Cloud Run 비용과 IAM 오류가 자동으로 반복되지 않게 한다.

## 4. 확인 URL

배포가 끝나면 Render 서비스 URL에서 아래 경로를 확인한다.

- `/health`
- `/login`
- `/support`
- `/diagnosis`
- `/pest`
