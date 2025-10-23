# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# 페이지 설정
st.set_page_config(page_title="모임 회계 관리", page_icon="💰", layout="wide")

# 데이터 파일 경로
DATA_FILE = "meeting_data.json"

# 기본 카테고리
DEFAULT_CATEGORIES = {
    "수입": ["회비", "기타수입"],
    "지출": ["식사비", "간식비", "교통비", "주유비", "숙박비", "기타지출"]
}

def load_data():
    """데이터 로드 함수"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 기존 데이터 구조 업데이트
                for meeting_id in data:
                    if "categories" not in data[meeting_id]:
                        data[meeting_id]["categories"] = DEFAULT_CATEGORIES.copy()
                    if "transactions" not in data[meeting_id]:
                        data[meeting_id]["transactions"] = []
                return data
        except:
            return get_default_data()
    else:
        return get_default_data()

def get_default_data():
    """기본 데이터 구조 반환"""
    return {
        "모임1": {
            "name": "모임1",
            "transactions": [],
            "categories": DEFAULT_CATEGORIES.copy()
        },
        "모임2": {
            "name": "모임2",
            "transactions": [],
            "categories": DEFAULT_CATEGORIES.copy()
        }
    }

def save_data(data):
    """데이터 저장 함수"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 세션 상태 초기화
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# 타이틀
st.title("💰 모임 회계 관리 시스템")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("설정")
    
    # 모임 이름 관리
    st.subheader("모임 이름 관리")
    for meeting_id in ["모임1", "모임2"]:
        new_name = st.text_input(
            f"{meeting_id} 이름",
            value=st.session_state.data[meeting_id]["name"],
            key=f"name_{meeting_id}"
        )
        if new_name != st.session_state.data[meeting_id]["name"]:
            st.session_state.data[meeting_id]["name"] = new_name
            save_data(st.session_state.data)
    
    st.markdown("---")
    
    # 모임 선택
    selected_meeting = st.radio(
        "관리할 모임 선택",
        ["모임1", "모임2"],
        format_func=lambda x: st.session_state.data[x]["name"]
    )
    
    st.markdown("---")
    
    # 항목 관리
    st.subheader("항목 관리")
    
    # 수입 항목 관리
    with st.expander("수입 항목 관리"):
        income_cats = st.session_state.data[selected_meeting]["categories"]["수입"]
        st.write("현재 수입 항목:")
        
        for idx, cat in enumerate(income_cats):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(cat)
            with col2:
                if st.button("X", key=f"del_in_{selected_meeting}_{idx}"):
                    st.session_state.data[selected_meeting]["categories"]["수입"].remove(cat)
                    save_data(st.session_state.data)
                    st.rerun()
        
        new_cat = st.text_input("새 수입 항목", key=f"new_in_{selected_meeting}")
        if st.button("추가", key=f"add_in_{selected_meeting}"):
            if new_cat and new_cat not in income_cats:
                st.session_state.data[selected_meeting]["categories"]["수입"].append(new_cat)
                save_data(st.session_state.data)
                st.rerun()
    
    # 지출 항목 관리
    with st.expander("지출 항목 관리"):
        expense_cats = st.session_state.data[selected_meeting]["categories"]["지출"]
        st.write("현재 지출 항목:")
        
        for idx, cat in enumerate(expense_cats):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(cat)
            with col2:
                if st.button("X", key=f"del_ex_{selected_meeting}_{idx}"):
                    st.session_state.data[selected_meeting]["categories"]["지출"].remove(cat)
                    save_data(st.session_state.data)
                    st.rerun()
        
        new_cat = st.text_input("새 지출 항목", key=f"new_ex_{selected_meeting}")
        if st.button("추가", key=f"add_ex_{selected_meeting}"):
            if new_cat and new_cat not in expense_cats:
                st.session_state.data[selected_meeting]["categories"]["지출"].append(new_cat)
                save_data(st.session_state.data)
                st.rerun()
    
    st.markdown("---")
    
    # 데이터 초기화
    if st.button("모든 데이터 초기화"):
        confirm = st.checkbox("정말 초기화하시겠습니까?")
        if confirm:
            st.session_state.data = get_default_data()
            save_data(st.session_state.data)
            st.success("초기화 완료")
            st.rerun()

# 현재 모임 정보
current_meeting = st.session_state.data[selected_meeting]
meeting_name = current_meeting["name"]

# 탭 생성
tab1, tab2, tab3 = st.tabs(["거래 입력", "내역 조회", "이미지 입력(준비중)"])

# 탭1: 거래 입력
with tab1:
    st.header(f"{meeting_name} - 거래 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trans_type = st.selectbox("구분", ["수입", "지출"])
        trans_date = st.date_input("날짜", datetime.now())
    
    with col2:
        available_cats = current_meeting["categories"][trans_type]
        
        input_method = st.radio(
            "항목 입력 방법",
            ["목록에서 선택", "직접 입력"],
            horizontal=True
        )
        
        if input_method == "목록에서 선택":
            if available_cats:
                category = st.selectbox("항목", available_cats)
            else:
                st.warning("등록된 항목이 없습니다")
                category = ""
        else:
            category = st.text_input("항목", placeholder="항목 입력")
    
    amount = st.number_input("금액 (원)", min_value=0, step=1000)
    description = st.text_area("상세 내용", placeholder="추가 설명")
    
    if st.button("저장", type="primary", use_container_width=True):
        if amount > 0 and category:
            new_transaction = {
                "date": trans_date.strftime("%Y-%m-%d"),
                "type": trans_type,
                "category": category,
                "amount": amount,
                "description": description,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            current_meeting["transactions"].append(new_transaction)
            save_data(st.session_state.data)
            st.success("저장 완료!")
            st.rerun()
        else:
            st.error("금액과 항목을 입력해주세요")

# 탭2: 내역 조회
with tab2:
    st.header(f"{meeting_name} - 거래 내역")
    
    transactions = current_meeting["transactions"]
    
    if transactions:
        df = pd.DataFrame(transactions)
        
        # 요약 통계
        col1, col2, col3, col4 = st.columns(4)
        
        total_income = df[df['type'] == '수입']['amount'].sum()
        total_expense = df[df['type'] == '지출']['amount'].sum()
        balance = total_income - total_expense
        
        with col1:
            st.metric("총 수입", f"{total_income:,}원")
        with col2:
            st.metric("총 지출", f"{total_expense:,}원")
        with col3:
            st.metric("잔액", f"{balance:,}원")
        with col4:
            st.metric("총 거래", f"{len(transactions)}건")
        
        st.markdown("---")
        
        # 필터
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.multiselect(
                "구분 필터",
                ["수입", "지출"],
                default=["수입", "지출"]
            )
        with col2:
            all_cats = df['category'].unique().tolist()
            filter_cats = st.multiselect(
                "항목 필터",
                all_cats,
                default=all_cats
            )
        
        filtered_df = df[df['type'].isin(filter_type) & df['category'].isin(filter_cats)]
        
        # 정렬
        sort_order = st.radio("정렬", ["최신순", "오래된순"], horizontal=True)
        display_df = filtered_df.sort_values(
            'date',
            ascending=(sort_order == "오래된순")
        ).reset_index(drop=True)
        
        # 거래 내역 표시
        st.subheader("거래 목록")
        
        for idx, row in display_df.iterrows():
            # 원본 인덱스 찾기
            orig_idx = None
            for i, trans in enumerate(transactions):
                if trans['timestamp'] == row['timestamp']:
                    orig_idx = i
                    break
            
            with st.expander(
                f"{row['date']} | {row['type']} | {row['category']} | {row['amount']:,}원"
            ):
                st.write(f"금액: {row['amount']:,}원")
                st.write(f"구분: {row['type']}")
                st.write(f"항목: {row['category']}")
                if row['description']:
                    st.write(f"상세: {row['description']}")
                st.write(f"등록: {row['timestamp']}")
                
                if orig_idx is not None:
                    if st.button("삭제", key=f"del_{idx}_{row['timestamp']}"):
                        del current_meeting["transactions"][orig_idx]
                        save_data(st.session_state.data)
                        st.rerun()
        
        # CSV 다운로드
        st.markdown("---")
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            "CSV 다운로드",
            data=csv,
            file_name=f"{meeting_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("아직 거래 내역이 없습니다")

# 탭3: 이미지 입력
with tab3:
    st.header("영수증 이미지 인식 (준비중)")
    st.info("""
    향후 추가될 기능:
    - 영수증 이미지 업로드
    - OCR 자동 인식
    - 금액/날짜/항목 추출
    - 자동 저장
    """)
    
    st.file_uploader(
        "영수증 업로드 (준비중)",
        type=['png', 'jpg', 'jpeg'],
        disabled=True
    )

# 푸터
st.markdown("---")
st.caption("Tip: 사이드바에서 모임 이름과 항목을 관리할 수 있습니다")
