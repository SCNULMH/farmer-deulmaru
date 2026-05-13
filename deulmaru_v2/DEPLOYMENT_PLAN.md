# 들마루 v2 제출용 DB/호스팅 구성안

## 빠른 제출용 추천

- Backend: FastAPI
- DB: Firebase Firestore
- Hosting: Render Web Service
- Storage: Firebase Storage 또는 Cloudinary
- Secrets: Render Environment Variables

## 왜 Firebase인가

SQLite는 로컬 개발에는 빠르지만 Render 같은 무료 호스팅에서는 재배포나 재시작 시 DB 파일 보존이 안정적이지 않습니다. 공모전 제출용으로는 외부 관리형 DB가 더 적합합니다.

Firebase Firestore는 다음 장점이 있습니다.

- 서버 재배포와 무관하게 데이터가 유지됩니다.
- 콘솔에서 저장 데이터를 바로 확인할 수 있습니다.
- 사용자, 관심 지원사업, 진단 이력처럼 문서형 데이터 저장에 잘 맞습니다.
- 팀원이 DB 상태를 함께 확인하기 쉽습니다.

## 현재 구현

`app/services/db.py`는 저장소를 자동 선택합니다.

- `DATABASE_BACKEND=sqlite`: 로컬 SQLite 사용
- `DATABASE_BACKEND=firebase`: Firebase Firestore 사용

현재 로컬 환경은 `growup` Firebase 프로젝트의 서비스 계정 파일을 `.env`의 `GOOGLE_APPLICATION_CREDENTIALS`로 연결해 Firestore 저장 테스트를 완료했습니다.

Firestore 사용 시 저장 구조는 다음과 같습니다.

```text
users/{user_id}
users/{user_id}/interests/{grant_id}
users/{user_id}/diagnosis_history/{auto_id}
```

## Firebase 연결 절차

1. Firebase Console에서 프로젝트 생성
2. Firestore Database 생성
3. 프로젝트 설정 > 서비스 계정 > 새 비공개 키 생성
4. Render 환경변수에 `DATABASE_BACKEND=firebase` 입력
5. Render 환경변수에 `FIREBASE_CREDENTIALS_JSON`으로 서비스 계정 JSON 전체 입력
6. 배포 후 `/login`, 관심 등록, 진단 저장 확인

로컬에서는 서비스 계정 JSON 파일 경로를 `GOOGLE_APPLICATION_CREDENTIALS`에 넣어도 됩니다.

## Render 환경변수

- `APP_SECRET_KEY`
- `DATABASE_BACKEND=firebase`
- `FIREBASE_CREDENTIALS_JSON`
- `SUPPORT_API_SERVICE_KEY`
- `NCPMS_API_KEY`
- `NONGSARO_API_KEY`
- `KAKAO_CLIENT_ID`
- `KAKAO_REDIRECT_URI`

## 제출 전 체크리스트

1. Firebase Firestore 생성 완료
2. 로컬 Firebase 저장 테스트 완료
3. Render에 GitHub repo 연결
4. Render env에 Firebase 서비스 계정 JSON 입력
5. Render env에 공공데이터 API 키 입력
6. `/health`, `/login`, `/`, `/api/diagnosis` 확인
7. Firebase Console에서 `users/demo`와 진단 이력 저장 확인

## API 키 정책

기존 Spring 프로젝트의 키는 그대로 소스에 두지 말고 `.env` 또는 Render env로 옮깁니다. GitHub에 올릴 때는 `.env`와 서비스 계정 JSON 파일을 커밋하지 않습니다.
