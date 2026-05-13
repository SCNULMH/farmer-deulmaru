# 들마루 프로젝트 인수인계 요약

## 1. 프로젝트 개요

들마루는 초보 농업인과 청년 농업인을 대상으로 작물 재배 일정, 농업 지원사업, 병해충 정보, 병해충 상담 이력, AI 병해충 이미지 판별을 한 곳에서 제공하는 농민 정착 지원 서비스다.

기존 산출물과 코드 기준 핵심 가치는 다음과 같다.

- 농촌진흥청/공공데이터 기반 지원사업 정보 제공
- 사용자가 관심 등록한 지원사업 기반 추천과 마감 알림
- 사용자 재배 작물 기반 농사 일정 제공
- NCPMS 기반 병해충 사전과 병해충 상담 조회
- 이미지 업로드 후 Python 모델로 병해충 예측
- 카카오 로그인/연동과 일반 회원가입/로그인

## 2. 기술 스택

- Backend: Java 17, Spring Boot 3.4.3, Spring MVC, Spring Data JPA
- Frontend: Thymeleaf, HTML, CSS, JavaScript, jQuery, Bootstrap
- DB: MySQL
- External APIs: 카카오 OAuth, NCPMS, 농사로, 청년농 지원사업 API
- AI: Python 예측 스크립트와 `.pth` 모델 파일

## 3. 주요 기능별 코드 위치

### 회원/인증

- `AuthController`: 일반 로그인, 로그아웃, 회원가입, 보호 페이지 접근 제어
- `KakaoController`: 카카오 OAuth 로그인, 신규 회원가입 연결, 기존 계정 연동/해제
- `UserService`: 회원 등록, 로그인 검증, 프로필 수정
- `UserEntity`: `TB_USER` 매핑

현재 비밀번호는 평문 저장/비교 구조다. 공모전 재정비 시 가장 먼저 해시 저장 방식으로 바꾸는 것이 좋다.

### 지원사업 정보/관심 등록/추천

- `SupportController`: 지원사업 목록/상세 페이지 라우팅
- `SupportService`: 청년농 지원사업 API 호출
- `UserInterestController`: 관심 지원사업 체크/등록/취소/목록
- `UserInterestService`: 관심 목록 저장 로직
- `RecommendationController`, `RecommendationService`: 전체 인기 지원금, 성별/연령/지역 기반 추천
- `UserInterest`: `TB_USER_INTEREST` 매핑

관심 등록 테이블은 `(USER_ID, GRANT_ID)` 유니크 제약으로 중복 등록을 막는 구조다.

### 농사 일정

- `CropScheduleController`: `/api/crop-schedule?cropName=작물명`
- `CropScheduleService`: 작물명과 농사로 `cntntsNo` 매핑 후 `<htmlCn>` 일정 HTML 추출

작물 매핑이 Java 코드 안에 긴 static Map으로 박혀 있다. CSV/DB/설정 파일로 분리하면 새 멤버가 유지보수하기 훨씬 쉽다.

### 병해충 사전/상담

- `NcpmsController`: `/ncpms/search`, `/ncpms/sick_detail`, `/ncpms/consult`, `/ncpms/consult_detail`
- `NcpmsService`: NCPMS API URL 조립과 XML 응답 반환
- 화면: `templates/ncpms/deulmaru_dictionary.html`, `deulmaru_QnA.html`
- JS: `static/js/deulmaru_dictionary_search.js`, `deulmaru_QNA.js`

현재 JS 일부가 `http://localhost:8082` 절대 주소를 직접 호출한다. 배포/포트 변경을 생각하면 상대 경로로 정리하는 것이 좋다.

### AI 병해충 판별

- `FileUploadController`: `/upload`에서 이미지 저장 후 Python 예측 스크립트 실행
- `IdentiController`: 판별 결과 저장/조회/삭제
- `IdentiService`: 이미지 저장, 진단 이력 저장/조회/삭제
- `IdentiEntity`: `tb_identi` 매핑
- Python: `predict.py`, `predict22.py`
- 모델: `model.pth`, `models/model_epoch_30.pth`

예측 스크립트 경로와 Python 인터프리터 경로가 `application.properties`에 개인 PC 기준으로 박혀 있다. 새 환경에서 바로 깨질 가능성이 높다.

## 4. DB 산출물 기준 테이블

### `tb_user`

사용자 계정 테이블. 주요 컬럼은 `user_id`, `user_pw`, `user_email`, `user_nickname`, `user_birth`, `user_gender`, `user_locate`, `kakao_id`, `user_crop`, `joined_at`.

### `tb_user_interest`

관심 지원사업 테이블. 주요 컬럼은 `interest_idx`, `user_id`, `grant_id`, `appl_ed_dt`, `alarm_enabled`, `notify_yn`, `title`, `added_at`.

### `tb_identi`

AI 진단 이력 테이블. 주요 컬럼은 `id`, `user_id`, `crop_name`, `disease_name`, `confidence_score`, `image_path`, `identification_time`.

## 5. 리팩토링 우선순위

1. 보안 설정 정리
   - API 키, DB 계정, 카카오 client id를 환경변수 또는 profile별 설정으로 분리
   - 비밀번호 평문 저장을 BCrypt 등 해시 기반으로 교체
   - 서비스 키를 뷰로 직접 넘기는 구조 점검

2. 실행 환경 정리
   - `predict.script.path`, `python.interpreter.path`, `upload.path`를 OS 독립적으로 정리
   - README에 로컬 실행 절차, 필요한 Python 패키지, 모델 파일 위치 명시
   - `JAVA_HOME`과 Maven 실행 환경 문서화

3. API 호출 계층 정리
   - `RestTemplate` 직접 생성 대신 Bean 또는 WebClient로 통일
   - URL 문자열 조립을 `UriComponentsBuilder`로 변경
   - 외부 API 실패/타임아웃/빈 응답 처리 추가

4. 프론트엔드 호출 경로 정리
   - `localhost:8082` 하드코딩 제거
   - 중복된 헤더/회원가입 화면 코드 정리
   - 화면별 JS를 기능 단위로 분리

5. 도메인 구조 정리
   - `auth`, `support`, `ncpms`, `diagnosis`, `recommendation`, `crop`처럼 패키지 기준 재배치
   - Controller는 요청/응답, Service는 비즈니스 로직, Client는 외부 API 호출로 책임 분리
   - Entity와 DTO를 분리해 화면/API 응답에 Entity가 직접 노출되지 않도록 정리

6. 테스트 추가
   - 회원가입/로그인, 관심 등록 중복 방지, 추천 쿼리, 진단 이력 저장/삭제 단위 테스트
   - 외부 API는 MockWebServer 또는 mock client로 테스트

## 6. 공모전 대응 메모

`서류/공모전` 폴더에는 농업·농촌 공공데이터 활용 창업경진대회 관련 자료가 있다.

- `00_경진대회_공고문 (1).pdf`: 대회 공고문
- `02_경진대회_기획서.pdf`: 아이디어 기획/제품·서비스 개발 기획서 양식
- `03_경진대회_평가표.pdf`: 평가표

PDF 텍스트 일부가 깨져서 세부 문구는 원본 확인이 필요하지만, 확인 가능한 평가 방향은 다음과 같다.

- 공공데이터 활용: 농림축산식품 공공데이터를 얼마나 적절하고 구체적으로 쓰는지
- 구체성/기술성: 아이디어와 서비스 구현 방식이 체계적인지
- 독창성: 기존 서비스와의 차별점이 분명한지
- 발전 가능성/사업화 가능성: 향후 서비스 확장, 시장성, 매출 또는 운영 가능성이 있는지
- 주제 시의성: 농식품/농업 현안 해결에 도움이 되는지

들마루는 이미 공공데이터 활용 요소가 많기 때문에, 이번 공모전 리팩토링은 단순 코드 정리보다 `공모전 평가 항목에 맞는 제품 메시지 강화`가 같이 필요하다.

공모전 관점에서 강화하면 좋은 방향은 다음과 같다.

1. 공공데이터 활용도를 화면과 기획서에서 명확히 드러내기
   - 청년농 지원사업 API, 농사로 작물 일정 API, NCPMS 병해충 API를 기능별로 표시
   - 각 데이터가 사용자의 어떤 의사결정을 돕는지 설명

2. 기존 농업 정보 포털과의 차별점 만들기
   - 단순 조회 서비스가 아니라 `내 작물`, `내 지역`, `내 관심 지원사업`, `내 진단 이력`을 묶은 개인화 대시보드로 포지셔닝
   - 병해충 진단 결과에서 관련 병해충 사전/상담/방제 정보로 이어지는 흐름 강화

3. 기술 적용의 설득력 높이기
   - AI 판별 모델은 데모용이라도 입력, 예측, 결과 저장, 이력 조회가 하나의 플로우로 안정적으로 동작해야 함
   - 외부 API 실패 시 빈 화면 대신 안내 메시지와 재시도 흐름 제공

4. 사업화 가능성 보강
   - 청년농/귀농 초기 사용자를 핵심 타깃으로 좁혀 문제를 선명하게 제시
   - 지역별 지원사업 추천, 재배작물 기반 일정 알림, 병해충 진단 이력 관리 같은 반복 사용 이유를 강조

5. 발표/시연 안정성 우선
   - 실제 공모전에서는 기능 수보다 시연이 끊기지 않는 것이 중요하다.
   - API 키/DB/모델 경로를 환경변수화하고, 네트워크 실패 대비 샘플 데이터 모드를 준비하는 것이 좋다.

## 7. Python v2 전환 방향

공모전 제출용 새 구현은 `deulmaru_v2` 폴더에서 Python/FastAPI 기반으로 시작했다. 기존 Spring 프로젝트는 보존하고, 새 팀이 새 UI와 새 구조로 다시 만드는 방향이다.

- 앱 위치: `deulmaru_v2`
- 실행 문서: `deulmaru_v2/README.md`
- 첫 화면: 개인화 농업 의사결정 대시보드
- 현재 데이터: 공모전 시연 안정성을 위한 샘플 데이터
- 향후 연결: 청년농 지원사업 API, 농사로 작물 일정 API, NCPMS API, PyTorch 병해충 모델

v2의 설계 원칙은 다음과 같다.

1. 기존 팀 코드와 화면을 그대로 재사용하지 않는다.
2. 공모전 평가 항목인 공공데이터 활용성, 독창성, 발전 가능성이 첫 화면에서 보이게 한다.
3. 실제 외부 API가 실패해도 발표 시연이 가능한 fallback 데이터를 유지한다.
4. AI 진단은 `app/services/diagnosis.py` 어댑터를 통해 연결해 화면과 모델 코드를 분리한다.

## 8. 새 멤버에게 먼저 설명할 흐름

1. 사용자는 일반/카카오 방식으로 로그인한다.
2. 메인에서 지원사업 추천, 지원사업 목록, 병해충 사전, 상담, AI 판별로 이동한다.
3. 지원사업 상세에서 관심 등록을 하면 `tb_user_interest`에 저장되고 마이페이지/알림/추천에 활용된다.
4. 마이페이지에서 재배 작물을 설정하면 농사로 API에서 해당 작물의 재배 일정을 가져온다.
5. 병해충 사전/상담은 NCPMS API를 프록시처럼 호출해 화면에 표시한다.
6. AI 판별은 이미지를 서버에 저장하고 Python 스크립트를 실행한 뒤, 사용자가 결과를 저장하면 `tb_identi`에 진단 이력이 남는다.

## 9. 확인한 제약

- HWP/PDF 산출물 전체 본문 변환은 외부 패키지 실행 보안 제한으로 완료하지 못했다.
- `테이블명세서.xlsx`는 로컬 표준 라이브러리로 확인했다.
- `서류/공모전`의 PDF 3개는 로컬 방식으로 텍스트를 일부 추출했지만 한글 인코딩이 완전하지 않아 세부 문구는 원본 확인이 필요하다.
- Maven 테스트는 Maven wrapper가 실행됐지만 현재 환경에 `JAVA_HOME`이 없어 완료하지 못했다.
- Python v2는 FastAPI 의존성을 설치했고 `TestClient`로 주요 라우트와 첫 화면 렌더링을 확인했다. 이 셸에서는 백그라운드 서버가 유지되지 않아 브라우저 확인은 직접 실행 명령으로 진행해야 한다.
