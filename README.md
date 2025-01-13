# 보도자료 HTML 자동 생성기

Streamlit과 Jinja2를 활용한 보도자료 HTML 자동 생성 웹 애플리케이션입니다.

## 주요 기능

- 보도자료 제목과 본문 입력
- HTML 자동 생성
- 미리보기 기능
- HTML 및 텍스트 파일 다운로드
- n8n Webhook 연동 지원

## 설치 방법

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run streamlit_app.py
```

웹 브라우저에서 자동으로 http://localhost:8501 이 열립니다. 