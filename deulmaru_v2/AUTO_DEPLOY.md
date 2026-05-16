# Cloud Run 자동 배포 설정

GitHub `main` 브랜치에 `deulmaru_v2/**` 변경이 push되면 GitHub Actions가 Cloud Run 서비스 `deulmaru-v2`를 자동 배포합니다.

## 1. GitHub Secret 등록

GitHub 저장소에서 다음 위치로 이동합니다.

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

등록할 Secret:

| Name | Value |
| --- | --- |
| `GCP_SA_KEY` | Firebase/Google Cloud 서비스 계정 JSON 전체 내용 |

JSON 파일은 저장소에 커밋하지 않습니다.

## 2. 서비스 계정 권한

`GCP_SA_KEY`에 사용하는 서비스 계정에는 최소한 다음 권한이 필요합니다.

| Role | 목적 |
| --- | --- |
| `roles/run.admin` | Cloud Run 서비스 배포 |
| `roles/iam.serviceAccountUser` | Cloud Run 실행 서비스 계정 사용 |
| `roles/cloudbuild.builds.editor` | `--source` 배포 시 Cloud Build 실행 |
| `roles/artifactregistry.writer` | 컨테이너 이미지 저장 |
| `roles/storage.admin` | Cloud Build 소스 업로드/빌드 산출물 처리 |

이미 Cloud Shell 수동 배포가 되는 계정과 동일한 권한을 서비스 계정에 부여하면 됩니다.

## 3. 자동 배포 범위

자동 배포는 Cloud Run 앱 코드만 배포합니다.

- 앱 화면, API, 정적 파일 변경: 자동 배포됨
- Firebase Hosting rewrite 변경: 별도 `firebase deploy --only hosting --project growup-39cbf` 필요
- Cloud Run 환경변수 변경: 별도 `gcloud run services update ...` 필요

현재 Firebase Hosting은 Cloud Run으로 rewrite되어 있으므로, 일반적인 앱 코드 변경은 Cloud Run 자동 배포만으로 `https://growup-39cbf.web.app`에 반영됩니다.

## 4. 수동 실행

GitHub Actions 화면에서 `Deploy Cloud Run` 워크플로를 선택한 뒤 `Run workflow`로 수동 배포할 수도 있습니다.
