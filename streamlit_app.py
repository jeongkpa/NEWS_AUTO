import streamlit as st
from jinja_utils import generate_press_release_html
import requests
import json

# 디버깅 모드 플래그
DEBUG_MODE = False  # 임시로 True로 설정

def get_ai_generated_text(form_data: dict) -> dict:
    """n8n webhook을 통해 AI 생성된 보도자료 텍스트를 받아옵니다."""
    # 입력 데이터에서 마크다운 볼드 표시와 헤더 표시 제거
    for key in form_data:
        if isinstance(form_data[key], str):
            form_data[key] = form_data[key].replace('**', '').replace('#', '')
    
    webhook_url = "http://203.239.132.7:5678/webhook/3ccfd480-71e7-4d1e-b264-69a651180350"
    
    try:
        # webhook으로 데이터 전송
        with st.spinner("AI가 보도자료를 생성하고 있습니다..."):
            response = requests.post(webhook_url, json=form_data, timeout=30)
        
        if response.status_code == 200:
            if DEBUG_MODE:
                st.write("### 디버깅: 서버 응답 정보")
                st.write(f"Status Code: {response.status_code}")
                st.write(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
                st.write("Response Text:")
                st.code(response.text)
            
            # Content-Type 확인
            content_type = response.headers.get('Content-Type', '')
            
            try:
                if 'application/json' in content_type:
                    # JSON 응답 처리
                    result = response.json()
                    if DEBUG_MODE:
                        st.write("### 디버깅: 파싱된 JSON 데이터")
                        st.json(result)
                    
                    # 배열로 온 경우 첫 번째 항목 사용
                    if isinstance(result, list):
                        result = result[0]
                    
                    title = result.get("title", "").strip()
                    news_data = result.get("news_data", "").strip()
                    check_data = result.get("check_data", "").strip()
                    insta_data = result.get("insta_data", "").strip()
                    facebook_data = result.get("facebook_data", "").strip()
                    blog_data = result.get("blog_data", "").strip()  # 블로그 데이터 추가
                else:
                    # 일반 텍스트 응답 처리
                    response_text = response.text.strip()
                    
                    # 응답 텍스트에서 첫 줄을 제목으로 사용
                    lines = response_text.split('\n')
                    title = lines[0].strip()
                    news_data = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                    check_data = ""
                    insta_data = ""
                    facebook_data = ""
                    blog_data = ""  # 블로그 데이터 빈 값으로 초기화
                
                st.success("보도자료가 성공적으로 생성되었습니다!")
                
                # 필수 필드 검증
                if not title or not news_data:
                    if DEBUG_MODE:
                        st.error("### 디버깅: 필수 필드 누락")
                        st.write(f"title 존재: {bool(title)}")
                        st.write(f"news_data 존재: {bool(news_data)}")
                    
                    # 폴백: 기본 템플릿 사용
                    return generate_fallback_template(form_data)
                
                return {
                    "title": title,
                    "news_data": news_data,
                    "check_data": check_data,
                    "insta_data": insta_data,
                    "facebook_data": facebook_data,
                    "blog_data": blog_data  # 블로그 데이터 추가
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                if DEBUG_MODE:
                    st.error(f"### 디버깅: 응답 처리 오류")
                    st.write(f"Error type: {type(e).__name__}")
                    st.write(f"Error message: {str(e)}")
                    st.write("Raw response:")
                    st.code(response.text)
                st.error("서버 응답을 처리하는 중 오류가 발생했습니다.")
                # 폴백: 기본 템플릿 사용
                return generate_fallback_template(form_data)
        else:
            if DEBUG_MODE:
                st.error(f"### 디버깅: HTTP 오류")
                st.write(f"Status code: {response.status_code}")
                st.write(f"Response text: {response.text}")
            st.error(f"서버 오류: {response.status_code}")
            # 폴백: 기본 템플릿 사용
            return generate_fallback_template(form_data)
            
    except requests.exceptions.RequestException as e:
        if DEBUG_MODE:
            st.error("### 디버깅: 요청 오류")
            st.write(f"Error type: {type(e).__name__}")
            st.write(f"Error message: {str(e)}")
        st.error(f"Webhook 호출 중 오류가 발생했습니다: {str(e)}")
        st.error("n8n 서버 연결을 확인해주세요 (http://203.239.132.7:5678)")
        # 폴백: 기본 템플릿 사용
        return generate_fallback_template(form_data)

def generate_fallback_template(form_data: dict) -> dict:
    """폴백: 기본 템플릿을 생성합니다."""
    if form_data["보도자료_유형"] == "제품 출시/리뷰 보도자료":
        generated_text = f"""{form_data['도입부']}은(는) {form_data['출시일']}에 {form_data['제품명']}을(를) 출시한다고 발표했습니다.

{form_data['제품명']}은(는) {form_data['제품 카테고리']} 제품으로, {form_data['주요 타깃']}을 위해 개발되었습니다.

{form_data['주요 특징(세일즈 포인트)']}

디자인 측면에서는 {form_data['주요 특징(디자인)']}

제품의 주요 스펙으로는 {form_data['세부 스펙 및 성능']}

{form_data['가격 및 판매 정보']}

{form_data['맺음말']}"""
    else:
        generated_text = f"""{form_data['도입부']}은(는) {form_data['행사명']}을(를) 진행한다고 발표했습니다.

행사 기간: {form_data['행사기간']}

{form_data['행사내용']}

{form_data['대상 제품']}

유의사항:
{form_data['유의사항']}

{form_data['맺음말']}"""

    generated_text += """

이와 관련한 보도자료를 송부하며, 제품에 대한 추가 자료 요청이나 문의는
아래 연락처로 부탁 드립니다.

감사합니다."""
    
    return {
        "title": form_data["제목"],
        "news_data": generated_text,
        "check_data": "",
        "insta_data": "",
        "facebook_data": "",
        "blog_data": ""
    }

def show_product_release_form():
    """제품 출시/리뷰 보도자료 폼을 표시합니다."""
    # 1. 제목
    title_input = st.text_input(
        "1. **제목** *",
        placeholder="예시) 제이씨현시스템㈜, GIGABYTE M27QA ICE 게이밍 모니터 출시!"
    )
    
    # 2. 도입부
    company_name = st.text_area(
        "2. **도입부** *",
        placeholder="예시) GIGABYTE Technology Co., LTD(이하 기가바이트)의 공식 공급원인 제이씨현시스템㈜ (대표: 차중석, 차정헌)은 2025년 1월, 'GIGABYTE M27QA ICE'를 새롭게 출시했다.",
        height=70
    )
    
    # 3. 제품명/시리즈명
    product_name = st.text_input(
        "3. **제품명/시리즈명** *",
        placeholder="예시) 기가바이트 M27QA ICE 게이밍 모니터",
        
    )
    
    # 4. 출시(예정)일
    release_date = st.text_input(
        "4. 출시(예정)일",
        placeholder="예시) 2024년 1월 9일"
    )
    
    # 5. 제품 카테고리
    category = st.text_input(
        "5. 제품 카테고리",
        placeholder="예시) 게이밍 모니터"
    )
    
    # 6. 주요 타깃
    target = st.text_input(
        "6. 주요 타깃",
        placeholder="예시) 화이트 색상의 모니터를 원하는 게이머",
    )
    
    # 7. 주요 특징(세일즈 포인트)
    innovation = st.text_area(
        "7. **주요 특징(세일즈 포인트)** *",
        placeholder="예시)\n- 27인치에 적합한 해상도인 QHD(2560*1440) 해상도\n- 광시야각 SS IPS\n- 180Hz의 고주사율\n- 응답속도 1ms(MPRT)\n- G-싱크 및 프리싱크 호환\n- DCI-P3 95%의 색재현율\n- 10비트 컬러, VESA HDR 400 지원\n- KVM스위치 내장\n- 3년 무상의 A/S 보증 서비스",
        height=250
    )
    
    # 8. 주요 특징(디자인)
    design = st.text_input(
        "8. **주요 특징(디자인)** *",
        placeholder="예시) ICE로 대표되는 기가바이트의 화이트 디자인",
    )
    
    # 9. 세부 스펙 및 성능
    specs = st.text_area(
        "9. 세부 스펙 및 성능",
        placeholder="예시)\n- 게임 편의 기능인 'Game Assist' 제공\n- 오랜 시간 편안한 게이밍을 위한 로우 블루라이트, 플리커 프리 기술 제공",
        height=100
    )
    
    # 10. 가격 및 판매 정보
    price_info = st.text_input(
        "10. 가격 및 판매 정보",
        placeholder="예시) 자세한 정보는 홈페이지를 통해 확인 가능합니다",
    )
    
    # 11. 맺음말
    press_quote = st.text_input(
        "11. 맺음말",
        placeholder="예시) 앞으로도 더 좋은 제품으로 보답하겠습니다.",
    )

    return {
        "보도자료_유형": "제품 출시/리뷰 보도자료",
        "제목": title_input,
        "도입부": company_name,
        "제품명": product_name,
        "출시일": release_date,
        "제품 카테고리": category,
        "주요 타깃": target,
        "주요 특징(세일즈 포인트)": innovation,
        "주요 특징(디자인)": design,
        "세부 스펙 및 성능": specs,
        "가격 및 판매 정보": price_info,
        "맺음말": press_quote
    }

def show_event_release_form():
    """이벤트/행사 보도자료 폼을 표시합니다."""
    # 1. 제목
    title_input = st.text_input(
        "1. **제목** *",
        placeholder="예시) 제이씨현시스템㈜, PNY GeForce RTX 4070 이상 제품 대상, 게임 증정 프로모션 진행!"
    )
    
    # 2. 도입부
    company_name = st.text_area(
        "2. **도입부** *",
        placeholder="예시) 국내 PNY Technologies, Inc. 공식 공급원 제이씨현시스템㈜ (대표: 차중석, 차정헌)은 PNY GeForce RTX 4070 이상의 제품(RTX 4090, RTX 40 SUPER, RTX 4070) 구매 고객을 대상으로 Indiana Jones and the Great Circle 게임 코드를 증정하는 프로모션을 진행한다.",
        height=100
    )
    
    # 3. 행사명
    event_name = st.text_input(
        "3. **행사명** *",
        placeholder="예시) Indiana Jones and the Great Circle 게임 코드를 증정"
    )
    
    # 4. 행사 기간
    event_period = st.text_input(
        "4. **행사 기간** *",
        placeholder="예시) 한국 시간 기준으로 2024년 11월 12일 밤 10시부터 12월 29일까지"
    )
    
    # 5. 행사 내용
    event_details = st.text_area(
        "5. **행사 내용** *",
        placeholder="""예시)\n게임 타이틀 청구 기간은 2025년 1월 30일까지다. 기한 내에 행사 페이지에 등록된 QR 코드를 통해 응모해야 하며, 반드시 구매 영수증을 첨부해야 최종 접수된다.""",
        height=100
    )
    
    # 6. 대상 제품
    target_products = st.text_area(
        "6. **대상 제품** *",
        placeholder="예시)신작 게임을 증정하는 PNY RTX 40 시리즈 그래픽카드는 지포스 RTX 4090, RTX 4080 SUPER, RTX 4080, RTX 4070 Ti SUPER, RTX 4070 Ti, RTX 4070 SUPER, RTX 4070 모델이다.",
        height=70
    )
    
    # 7. 유의사항
    notes = st.text_area(
        "7. 유의사항",
        placeholder="예시)\n- 재고 소진 시 조기 종료될 수 있음\n- 일부 제품은 행행행사에서 제외될 수 있음\n- 사은품은 추후 배송될 수 있음",
        height=110
    )
    
    # 8. 맺음말
    press_quote = st.text_area(
        "8. 맺음말",
        placeholder="예시) PNY는 소비자 및 비즈니스 등급의 전자 제품 제조에 전념하는 글로벌 기술 리더다. PNY는 전 세계 소비자, B2B 및 OEM에 서비스를 제공하는 30년 이상의 비즈니스 경험을 가지고 있다.",
        height=100
    )

    return {
        "보도자료_유형": "이벤트/행사 보도자료",
        "제목": title_input,
        "도입부": company_name,
        "행사명": event_name,
        "행사기간": event_period,
        "행사내용": event_details,
        "대상 제품": target_products,
        "유의사항": notes,
        "맺음말": press_quote
    }

def get_required_fields(release_type: str) -> list:
    """보도자료 유형별 필수 입력 필드를 반환합니다."""
    if release_type == "제품 출시/리뷰 보도자료":
        return [
            "제목",
            "도입부",
            "제품명",
            "주요 특징(세일즈 포인트)",
            "주요 특징(디자인)"
        ]
    else:  # 이벤트/행사 보도자료
        return [
            "제목",
            "도입부",
            "행사명",
            "행사기간",
            "행사내용",
            "대상 제품"
        ]

def show_result(generated_data, form_data, container):
    """생성된 보도자료 결과를 표시합니다."""
    with container:
        # 스타일 정의
        st.markdown("""
            <style>
                .stTabs [data-baseweb="tab-panel"] {
                    padding: 0.5rem;
                }
                .stMarkdown {
                    padding: 0;
                }
                /* HTML 미리보기 컨테이너가 부모 너비에 맞게 조정되도록 */
                iframe {
                    width: 100% !important;
                }
                /* td 요소의 너비를 늘림 */
                td[width="550"] {
                    width: 800px !important;
                }
                /* 테이블 자체의 너비도 조정 */
                table {
                    width: 100% !important;
                }
                /* 인스타그램 포스팅 스타일 */
                .instagram-post {
                    background: white;
                    border: 1px solid #dbdbdb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }
                .instagram-post pre {
                    white-space: pre-wrap;
                    font-family: inherit;
                    margin: 0;
                    padding: 10px;
                }
                /* 서브헤더 여백 조정 */
                .stTabs + div > .stMarkdown > h3 {
                    margin-top: 0.5rem;
                    margin-bottom: 0.5rem;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # 탭 생성
        tab1, tab2 = st.tabs(["🌐 HTML 미리보기", "📝 텍스트 미리보기"])
        
        with tab1:
            st.markdown("<h3 style='margin: 0.5rem 0;'>HTML 미리보기</h3>", unsafe_allow_html=True)
            rendered_html = generate_press_release_html(
                title=generated_data["title"],
                body_text=generated_data["news_data"]
            )
            # HTML 컨텐츠를 좌측 정렬하고 너비를 늘림
            st.components.v1.html(
                f"""
                <div style="width: 100%; margin: 0; text-align: left;">
                    <div style="margin: 0; min-width: 550px;">
                        {rendered_html}
                    </div>
                </div>
                """,
                height=800,
                scrolling=True
            )
            
            # 다운로드 버튼 섹션
            st.subheader("파일 다운로드")
            col1, col2 = st.columns(2)
            
            with col1:
                # 텍스트 파일에는 제목과 본문을 함께 포함
                full_text = f"{generated_data['title']}\n\n{generated_data['news_data']}"
                st.download_button(
                    label="📄 보도자료 텍스트(.txt)",
                    data=full_text.encode("utf-8"),
                    file_name="press_release.txt",
                    mime="text/plain",
                    key="download_txt"
                )

            with col2:
                st.download_button(
                    label="🌐 보도자료 HTML(.html)",
                    data=generate_press_release_html(
                        title=generated_data["title"],
                        body_text=generated_data["news_data"]
                    ).encode("utf-8"),
                    file_name="press_release.html",
                    mime="text/html",
                    key="download_html"
                )
            
            # 인스타그램 포스팅 미리보기
            if generated_data.get("insta_data"):
                st.subheader("❤️ 인스타 및 틱톡 미리보기")
                with st.expander("인스타 및 틱톡 보기", expanded=False):
                    posts = generated_data["insta_data"].strip().split("\n\n\n")
                    # 처음 2개의 포스팅만 표시
                    for i, post in enumerate(posts[:2], 1):
                        if post.strip():
                            st.markdown(f"""
                                <div class="instagram-post">
                                    <h4>포스팅 {i}</h4>
                                    <pre>{post.strip()}</pre>
                                </div>
                            """, unsafe_allow_html=True)
            
            # Facebook 포스팅 미리보기
            if generated_data.get("facebook_data"):
                st.subheader("💙 페이스북 미리보기")
                with st.expander("페이스북 포스팅 보기", expanded=False):
                    st.markdown(f"""
                        <div class="instagram-post">
                            <pre>{generated_data["facebook_data"].strip()}</pre>
                        </div>
                    """, unsafe_allow_html=True)
            
            # 네이버 블로그 미리보기
            if generated_data.get("blog_data"):
                st.subheader("💚 네이버 블로그 미리보기")
                with st.expander("블로그 포스팅 보기", expanded=False):
                    st.markdown(f"""
                        <div class="instagram-post">
                            <pre><strong>{generated_data["title"]}</strong>
                            <br>
                            <br>
{generated_data["blog_data"].strip()}</pre>
                        </div>
                    """, unsafe_allow_html=True)
            
            # 검증 데이터가 있는 경우 표시
            if generated_data["check_data"]:
                st.subheader("입력 데이터 검증 및 조언")
                with st.expander("검증 결과 보기", expanded=False):
                    st.markdown(generated_data["check_data"])
            
        with tab2:
            st.subheader("생성된 보도자료")
            # 제목 표시
            st.markdown(f"**제목:** {generated_data['title']}")
            # 본문 표시
            st.markdown(
                f"""<div style="padding: 4rem;">
                    {generated_data['news_data'].replace(chr(10), "<br>")}
                </div>""",
                unsafe_allow_html=True
            )
            
            # 인스타그램 포스팅 표시
            if generated_data.get("insta_data"):
                st.subheader("인스타그램 포스팅")
                with st.expander("인스타그램 포스팅 보기", expanded=False):
                    posts = generated_data["insta_data"].strip().split("\n\n\n")
                    # 처음 2개의 포스팅만 표시
                    st.markdown("\n\n".join(posts[:2]))
            
            # 검증 데이터가 있는 경우 표시
            if generated_data["check_data"]:
                st.subheader("입력 데이터 검증 결과")
                with st.expander("검증 결과 보기", expanded=False):
                    st.markdown(generated_data["check_data"])

def main():
    # 페이지 레이아웃을 centered 모드로 변경 (wide -> centered)
    st.set_page_config(
        page_title="보도자료 기사 AI 자동 생성",
        layout="centered",  # wide에서 centered로 변경
        initial_sidebar_state="collapsed"
    )
    
    # CSS로 전체 페이지 스타일 정의
    st.markdown("""
        <style>
            /* 상단 여백 줄이기 */
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
            /* 제목 여백 조정 */
            .stTitle {
                margin-top: -2rem;
            }
            /* 기존 스타일 유지 */
            .main > div {
                padding-left: 8rem;
                padding-right: 8rem;
                margin: 0 auto;
            }
            /* Streamlit 기본 요소 숨기기 */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("보도자료 기사 AI 자동 생성")
    
    # 세션 상태 초기화
    if "generated_data" not in st.session_state:
        st.session_state["generated_data"] = None
    if "form_data" not in st.session_state:
        st.session_state["form_data"] = {}
    
    # 보도자료 유형 선택을 container로 감싸서 여백 추가
    with st.container():        
        st.markdown("""
            <div style="font-size: 0.875rem; color: rgb(49, 51, 63); margin-bottom: 0.1rem;">
            보도자료 유형을 선택하세요
            </div>
        """, unsafe_allow_html=True)
        
        release_type = st.selectbox(
            "보도자료 유형",  # 라벨 추가
            ["제품 출시/리뷰 보도자료", "이벤트/행사 보도자료"],
            label_visibility="collapsed"  # 라벨을 시각적으로 숨김
        )
        
        st.markdown("""
            <div class="info-text" style="font-size: 0.875rem;">
                <strong>필수입력 사항(*)</strong><br>
                여러번 호출하여 마음에 드는 보도자료를 생성해보세요.<br>
                작성한 폼은 새로고침만 하지 않으시면 유지됩니다.
            </div>
            <br>
        """, unsafe_allow_html=True)
    
    # 폼을 container로 감싸서 여백 추가
    form_container = st.container()
    with form_container:
        with st.form("press_release_form", clear_on_submit=False):
            if release_type == "제품 출시/리뷰 보도자료":
                form_data = show_product_release_form()
            else:
                form_data = show_event_release_form()

            submitted = st.form_submit_button("AI 보도자료 생성", use_container_width=True)
    # 여백 추가
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # 폼 제출 처리
    if submitted:
        # 필수 입력값 검증
        required_fields = get_required_fields(release_type)
        empty_required_fields = [k for k in required_fields if not form_data[k].strip()]
        
        if empty_required_fields:
            st.error(f"다음 필수 항목을 입력해주세요: {', '.join(empty_required_fields)}")
            return
        
        # AI 생성 요청
        generated_data = get_ai_generated_text(form_data)
        
        # 세션 상태에 텍스트와 폼 데이터를 저장
        if generated_data:
            st.session_state["generated_data"] = generated_data
            st.session_state["form_data"] = form_data
    
    # 세션 상태에 저장된 텍스트가 있을 경우 결과 표시
    if st.session_state["generated_data"]:
        result_container = st.container()
        show_result(
            st.session_state["generated_data"], 
            st.session_state["form_data"],
            result_container
        )

if __name__ == "__main__":
    main()