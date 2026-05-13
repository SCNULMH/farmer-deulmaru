# GitHub 공유 절차

이 폴더는 아직 GitHub 원격 저장소가 연결되어 있지 않습니다. GitHub에서 새 repository를 만든 뒤 아래 명령을 실행합니다.

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru
git remote add origin https://github.com/<YOUR_ID>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

## 주의

다음 파일은 절대 GitHub에 올리지 않습니다.

- `deulmaru_v2/.env`
- `deulmaru_v2/*firebase-adminsdk*.json`
- `src/main/resources/application.properties`
- `model.pth`
- `models/*.pth`

현재 `.gitignore`에 제외 규칙을 추가해두었습니다.
