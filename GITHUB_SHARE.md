# GitHub 공유 상태

이 저장소는 GitHub private repository에 연결되어 있습니다.

- 원격 저장소: `https://github.com/SCNULMH/farmer-deulmaru.git`
- 기본 브랜치: `main`
- 최초 공유 커밋: `2d4a14c Prepare Deulmaru v2 contest app`

추가 작업 후 공유할 때는 아래 명령을 실행합니다.

```powershell
cd C:\Users\user\Desktop\farmer-deulmaru
git status
git add <변경한 파일>
git commit -m "Update contest app"
git push -u origin main
```

## 주의

다음 파일은 절대 GitHub에 올리지 않습니다. 현재 `.gitignore`에 제외 규칙을 추가해두었습니다.

- `deulmaru_v2/.env`
- `deulmaru_v2/*firebase-adminsdk*.json`
- `deulmaru_v2/service-account*.json`
- `src/main/resources/application.properties`
- `model.pth`
- `models/*.pth`
