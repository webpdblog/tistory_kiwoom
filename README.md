# 키움증권 REST API 토큰 관리 시스템

키움증권 REST API의 OAuth 토큰 발급 및 관리를 위한 Windows용 GUI 애플리케이션입니다.

## 주요 기능

### 토큰 관리
- **OAuth 토큰 발급**: 키움증권 API 접근 토큰 자동 발급 (au10001)
- **토큰 폐기**: 사이드바 버튼을 통한 간편한 토큰 폐기 기능
- **토큰 유효성 검증**: 토큰 만료 시간 자동 체크 및 상태 표시
- **환경 전환**: 운영(Production) / 모의투자(Mock) 환경 간 간편 전환

### 사용자 인터페이스
- **웹 스타일 레이아웃**: 사이드바 + 메인 영역 구조
- **크기 조절 가능**: 최소 900x600, 기본 1200x800 창 크기
- **4개 페이지 구성**:
  - 🔑 토큰 발급: 환경 선택 및 토큰 발급
  - 📋 토큰 정보: 발급된 토큰 상세 정보 확인
  - ⚙ 설정: API 및 로깅 설정 확인
  - 📝 실행 로그: 실시간 로그 모니터링
- **카드 기반 UI**: 깔끔하고 직관적인 컴포넌트 구조
- **실시간 업데이트**: 시간 표시, 로그 자동 갱신

## 시스템 요구사항

- **운영체제**: Windows 10/11
- **Python**: 3.8 이상
- **인터넷 연결**: API 호출을 위해 필요

## 설치 방법

### 1. Python 설치 확인

```bash
python --version
```

Python이 설치되어 있지 않다면 [python.org](https://www.python.org/downloads/)에서 다운로드하세요.

### 2. 프로젝트 다운로드

```bash
git clone <repository-url>
cd tistory_kiwoom
```

### 3. 가상 환경 생성 (권장)

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

## 설정 방법

### 방법 1: config.ini 파일 수정

`config.ini` 파일을 열어 API 인증 정보를 입력하세요:

```ini
[KIWOOM]
environment = mock
appkey = YOUR_APP_KEY
secretkey = YOUR_SECRET_KEY
```

### 방법 2: .env 파일 사용 (권장)

1. `.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
copy .env.example .env
```

2. `.env` 파일을 열어 실제 인증 정보 입력:

```env
KIWOOM_APPKEY=실제_발급받은_APP_KEY
KIWOOM_SECRETKEY=실제_발급받은_SECRET_KEY
KIWOOM_ENVIRONMENT=mock
```

> **중요**: `.env` 파일은 보안상 Git에 커밋하지 마세요!

## 실행 방법

### GUI 모드 실행

```bash
python main.py
```

### 프로그램 사용법

#### 1. 토큰 발급 (🔑 토큰 발급 페이지)
- API 환경 선택 (mock/production)
- "토큰 발급하기" 버튼 클릭
- 발급 완료 시 상태가 "연결됨"으로 변경

#### 2. 토큰 정보 확인 (📋 토큰 정보 페이지)
- 토큰 유효 상태 확인
- 토큰 타입, 만료 일시 확인
- 액세스 토큰 전체 값 확인

#### 3. 토큰 폐기
- 사이드바 상단의 "🗑 토큰 폐기" 버튼 클릭
- 확인 다이얼로그에서 "예" 선택
- 자동으로 토큰 발급 페이지로 이동

#### 4. 설정 확인 (⚙ 설정 페이지)
- API 인증 정보 확인
- 로깅 설정 확인

#### 5. 로그 확인 (📝 실행 로그 페이지)
- 실시간 API 호출 내역
- 색상으로 구분된 로그 레벨 (INFO, SUCCESS, ERROR, WARNING)
- 페이지 전환 시에도 로그 히스토리 유지

## 프로젝트 구조

```
tistory_kiwoom/
│
├── main.py                 # 메인 진입점
├── config.ini              # 설정 파일
├── .env                    # 환경 변수 (생성 필요)
├── .env.example            # 환경 변수 예시
├── requirements.txt        # Python 패키지 의존성
├── README.md              # 프로젝트 문서
│
├── src/                   # 소스 코드
│   ├── __init__.py
│   ├── kiwoom_client.py   # API 클라이언트
│   ├── config_manager.py  # 설정 관리자
│   ├── logger.py          # 로깅 시스템
│   └── gui.py             # GUI 인터페이스
│
├── restapi/               # API 문서
│   └── au10001_접근토큰발급.txt
│
└── logs/                  # 로그 파일 (자동 생성)
    └── kiwoom_api.log
```

## API 문서

### 접근 토큰 발급 (au10001)

**엔드포인트**: `POST /oauth2/token`

**요청**:
```json
{
  "grant_type": "client_credentials",
  "appkey": "YOUR_APP_KEY",
  "secretkey": "YOUR_SECRET_KEY"
}
```

**응답**:
```json
{
  "expires_dt": "20240101123000",
  "token_type": "Bearer",
  "token": "ACCESS_TOKEN_VALUE"
}
```

자세한 내용은 `restapi/au10001_접근토큰발급.txt` 참조

## 로깅

- **로그 파일**: `logs/kiwoom_api.log`
- **로그 레벨**: INFO (config.ini에서 변경 가능)
- **로그 로테이션**: 10MB 단위로 자동 백업 (최대 5개)

## 문제 해결

### 토큰 발급 실패

1. **인증 정보 확인**: config.ini 또는 .env 파일의 appkey, secretkey가 정확한지 확인
2. **환경 설정 확인**: mock/production 환경이 올바른지 확인
3. **네트워크 확인**: 인터넷 연결 및 방화벽 설정 확인
4. **로그 확인**: `logs/kiwoom_api.log` 파일에서 상세 오류 내용 확인

### GUI 실행 오류

```bash
# tkinter가 설치되어 있는지 확인
python -m tkinter
```

작은 창이 뜨면 정상입니다. 오류가 발생하면 Python 재설치 시 "tcl/tk and IDLE" 옵션을 선택하세요.

### 패키지 설치 오류

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

## 보안 주의사항

- **인증 정보 보호**: appkey, secretkey는 절대 공개하지 마세요
- **.env 파일**: Git에 커밋하지 마세요 (.gitignore에 추가됨)
- **토큰 관리**: 발급된 토큰은 안전하게 보관하세요
- **로그 파일**: 민감한 정보가 포함될 수 있으니 공유 시 주의하세요

## 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

## 문의

문제가 발생하거나 질문이 있으시면 Issue를 등록해주세요.

---

**키움증권 REST API v1.0** | © 2025
