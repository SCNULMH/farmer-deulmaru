# Firebase Hosting 배포 메모

FastAPI는 정적 사이트가 아니므로 Firebase Hosting 단독으로 실행할 수 없습니다. 이 프로젝트는 다음 구조로 배포합니다.

- Firebase Hosting: 공개 URL과 라우팅
- Cloud Run: FastAPI 서버 실행
- Firestore: 사용자, 관심 지원사업, 진단 이력 저장

## 1. Cloud Run 배포

Google Cloud SDK가 설치되어 있고 `gcloud auth login`이 완료되어 있어야 합니다.

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru\deulmaru_v2

gcloud config set project growup-39cbf
gcloud run deploy deulmaru-v2 `
  --source . `
  --region asia-northeast3 `
  --allow-unauthenticated `
  --set-env-vars DATABASE_BACKEND=firebase,USE_DEMO_DATA=false `
  --set-env-vars APP_SECRET_KEY=change-this-in-production
```

Cloud Run에는 Firebase 서비스 계정 JSON도 환경변수로 넣어야 합니다.

```powershell
gcloud run services update deulmaru-v2 `
  --region asia-northeast3 `
  --set-env-vars FIREBASE_CREDENTIALS_JSON="<서비스 계정 JSON 전체>"
```

공공데이터 API 키도 Cloud Run 환경변수로 넣습니다.

## 2. Firebase Hosting 배포

루트 폴더에서 실행합니다.

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru
firebase deploy --only hosting --project growup-39cbf
```

`firebase.json`은 모든 요청을 `asia-northeast3`의 Cloud Run 서비스 `deulmaru-v2`로 rewrite합니다.

## 3. 확인

- Firebase Hosting URL 접속
- `/login`에서 `demo / demo1234` 로그인
- 지원사업 표시
- 관심 등록 후 Firestore 확인
- AI 진단 저장 후 Firestore 확인
