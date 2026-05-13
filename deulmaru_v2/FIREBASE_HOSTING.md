# Firebase Hosting 배포 메모

FastAPI는 정적 사이트가 아니므로 Firebase Hosting 단독으로 실행할 수 없습니다. 이 프로젝트는 다음 구조로 배포합니다.

- Firebase Hosting: 공개 URL과 라우팅
- Cloud Run: FastAPI 서버 실행
- Firestore: 사용자, 관심 지원사업, 진단 이력 저장

현재 Firebase Hosting 설정은 완료되어 있습니다. 단, Hosting rewrite가 연결될 Cloud Run 서비스 `deulmaru-v2`가 먼저 존재해야 합니다.

로컬 PC에는 `gcloud`가 설치되어 있지 않으므로 가장 빠른 방법은 Google Cloud Console의 Cloud Shell에서 아래 명령을 실행하는 것입니다.

## 1. Cloud Run 배포

Cloud Shell에서 저장소를 clone합니다.

```bash
git clone https://github.com/SCNULMH/farmer-deulmaru.git
cd farmer-deulmaru/deulmaru_v2
gcloud config set project growup-39cbf
```

필요 API를 활성화합니다.

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com firebasehosting.googleapis.com
```

FastAPI 앱을 Cloud Run에 배포합니다.

```bash
gcloud run deploy deulmaru-v2 \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_BACKEND=firebase,USE_DEMO_DATA=false,APP_SECRET_KEY=change-this-in-production
```

Cloud Run에서는 같은 Google Cloud 프로젝트의 기본 서비스 계정으로 Firestore에 접근할 수 있습니다. 권한 문제가 나면 Cloud Run 실행 서비스 계정에 `Cloud Datastore User` 또는 Firestore 접근 권한을 부여합니다.

공공데이터 API 키는 GitHub에 올리지 말고 Cloud Run 환경변수로만 넣습니다.

```bash
gcloud run services update deulmaru-v2 \
  --region asia-northeast3 \
  --set-env-vars SUPPORT_API_SERVICE_KEY="값",NONGSARO_API_KEY="값",NCPMS_API_KEY="값",KAKAO_CLIENT_ID="값"
```

로컬 PC에 Google Cloud SDK가 설치되어 있다면 같은 명령을 PowerShell에서도 실행할 수 있습니다.

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

## 2. Firebase Hosting 배포

루트 폴더에서 실행합니다.

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru
firebase deploy --only hosting --project growup-39cbf
```

`firebase.json`은 모든 요청을 `asia-northeast3`의 Cloud Run 서비스 `deulmaru-v2`로 rewrite합니다.

이번 로컬 배포 시도는 Cloud Run 서비스가 아직 없어 실패했습니다.

주요 메시지:

```text
Cloud Run service `deulmaru-v2` does not exist in region `asia-northeast3` in this project.
```

Cloud Run 배포를 먼저 완료한 뒤 Hosting 배포를 다시 실행하면 됩니다.

## 3. 확인

- Firebase Hosting URL 접속
- `/login`에서 `demo / demo1234` 로그인
- 지원사업 표시
- 관심 등록 후 Firestore 확인
- AI 진단 저장 후 Firestore 확인
