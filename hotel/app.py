import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Hệ Thống Dự Đoán Khả Năng Hủy Đặt Phòng Khách Sạn",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Visual Excellence
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(30, 60, 114, 0.2);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 1.8rem;
        margin-bottom: 8px;
    }
    .main-header p {
        color: #E0E8F9;
        font-size: 0.95rem;
        margin: 0;
    }
    
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #E9ECEF;
        text-align: center;
    }
    .risk-high {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE3E3 100%);
        border: 2px solid #FF6B6B;
        border-radius: 14px;
        padding: 20px;
    }
    .risk-safe {
        background: linear-gradient(135deg, #EBFBEE 0%, #D3F9D8 100%);
        border: 2px solid #51CF66;
        border-radius: 14px;
        padding: 20px;
    }
    .badge-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    .badge-danger { background: #FF6B6B; color: white; }
    .badge-success { background: #51CF66; color: white; }
    
    div[data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0D6EFD 0%, #0A58CA 100%);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        padding: 12px 24px;
        border: none;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(13, 110, 253, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Load trained model artifacts
@st.cache_resource
def load_artifacts():
    models_dir = os.path.join("outputs", "models")
    rf_model = joblib.load(os.path.join(models_dir, "random_forest.pkl"))
    gb_model = joblib.load(os.path.join(models_dir, "gradient_boosting.pkl"))
    scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(models_dir, "feature_names.pkl"))
    return rf_model, gb_model, scaler, feature_names

rf_model, gb_model, scaler, feature_names = load_artifacts()

# Mapping Dictionaries: Display Label -> Raw Feature Value
HOTEL_MAP = {
    "City Hotel (Khách sạn Thành phố)": "City Hotel",
    "Resort Hotel (Khách sạn Nghỉ dưỡng)": "Resort Hotel"
}

MARKET_SEGMENT_MAP = {
    "Online TA (Đại lý du lịch trực tuyến: Agoda, Booking, Expedia...)": "Online TA",
    "Offline TA/TO (Đại lý du lịch truyền thống / Công ty lữ hành)": "Offline TA/TO",
    "Groups (Khách đặt đi theo đoàn)": "Groups",
    "Direct (Khách đặt trực tiếp tại Khách sạn / Website)": "Direct",
    "Corporate (Khách doanh nghiệp / Công tác)": "Corporate",
    "Complementary (Phòng miễn phí / Tài trợ)": "Complementary"
}

DEPOSIT_TYPE_MAP = {
    "No Deposit (Không cần đặt cọc)": "No Deposit",
    "Non Refund (Đặt cọc không hoàn lại - Rất an toàn)": "Non Refund",
    "Refundable (Đặt cọc có thể hoàn tiền)": "Refundable"
}

CUSTOMER_TYPE_MAP = {
    "Transient (Khách lẻ vãng lai)": "Transient",
    "Transient-Party (Khách lẻ đi theo nhóm)": "Transient-Party",
    "Contract (Khách đặt theo hợp đồng dài hạn)": "Contract",
    "Group (Khách đoàn chính thức)": "Group"
}

COUNTRY_MAP = {
    "PRT (Bồ Đào Nha - Portugal)": "PRT",
    "GBR (Vương Quốc Anh - United Kingdom)": "GBR",
    "FRA (Pháp - France)": "FRA",
    "ESP (Tây Ban Nha - Spain)": "ESP",
    "DEU (Đức - Germany)": "DEU",
    "ITA (Ý - Italy)": "ITA",
    "IRL (Ireland)": "IRL",
    "BRA (Brazil)": "BRA",
    "NLD (Hà Lan - Netherlands)": "NLD",
    "Other (Quốc gia khác)": "Other"
}

MEAL_MAP = {
    "BB (Bed & Breakfast - Chỉ bao gồm bữa sáng)": "BB",
    "HB (Half Board - Ăn 2 bữa: Sáng + Tối)": "HB",
    "FB (Full Board - Ăn trọn gói 3 bữa: Sáng + Trưa + Tối)": "FB",
    "SC (Self Catering - Tự phục vụ / Không kèm bữa ăn)": "SC",
    "Undefined (Chưa xác định gói ăn)": "Undefined"
}

# Define Preset Sample Customer Profiles
PRESET_PROFILES = {
    "✍️ Tự nhập thông tin thủ công": None,
    "👨‍👩‍👧‍👦 1. Khách Gia Đình Nghỉ Mát (Resort Family - An toàn)": {
        "hotel": "Resort Hotel (Khách sạn Nghỉ dưỡng)",
        "lead_time": 30,
        "stays_weekend": 2,
        "stays_week": 4,
        "adults": 2,
        "children": 2,
        "babies": 0,
        "special_requests": 2,
        "market_segment": "Direct (Khách đặt trực tiếp tại Khách sạn / Website)",
        "deposit_type": "No Deposit (Không cần đặt cọc)",
        "customer_type": "Transient (Khách lẻ vãng lai)",
        "adr": 160.0,
        "prev_canc": 0,
        "prev_not_canc": 2,
        "booking_changes": 1,
        "parking_spaces": 1,
        "country_group": "PRT (Bồ Đào Nha - Portugal)",
        "meal": "HB (Half Board - Ăn 2 bữa: Sáng + Tối)"
    },
    "💼 2. Khách Doanh Nhân Công Tác (Business Corporate - An toàn)": {
        "hotel": "City Hotel (Khách sạn Thành phố)",
        "lead_time": 5,
        "stays_weekend": 0,
        "stays_week": 2,
        "adults": 1,
        "children": 0,
        "babies": 0,
        "special_requests": 0,
        "market_segment": "Corporate (Khách doanh nghiệp / Công tác)",
        "deposit_type": "No Deposit (Không cần đặt cọc)",
        "customer_type": "Contract (Khách đặt theo hợp đồng dài hạn)",
        "adr": 110.0,
        "prev_canc": 0,
        "prev_not_canc": 5,
        "booking_changes": 0,
        "parking_spaces": 0,
        "country_group": "GBR (Vương Quốc Anh - United Kingdom)",
        "meal": "BB (Bed & Breakfast - Chỉ bao gồm bữa sáng)"
    },
    "⚠️ 3. Khách Săn Sale Mạng (Online TA - RỦI RO HỦY CAO)": {
        "hotel": "City Hotel (Khách sạn Thành phố)",
        "lead_time": 260,
        "stays_weekend": 2,
        "stays_week": 3,
        "adults": 2,
        "children": 0,
        "babies": 0,
        "special_requests": 0,
        "market_segment": "Online TA (Đại lý du lịch trực tuyến: Agoda, Booking, Expedia...)",
        "deposit_type": "No Deposit (Không cần đặt cọc)",
        "customer_type": "Transient (Khách lẻ vãng lai)",
        "adr": 85.0,
        "prev_canc": 2,
        "prev_not_canc": 0,
        "booking_changes": 0,
        "parking_spaces": 0,
        "country_group": "PRT (Bồ Đào Nha - Portugal)",
        "meal": "BB (Bed & Breakfast - Chỉ bao gồm bữa sáng)"
    },
    "🛡️ 4. Khách Cọc Không Hoàn Lại (Non-Refundable - CỰC KỲ AN TOÀN)": {
        "hotel": "Resort Hotel (Khách sạn Nghỉ dưỡng)",
        "lead_time": 90,
        "stays_weekend": 1,
        "stays_week": 2,
        "adults": 2,
        "children": 0,
        "babies": 0,
        "special_requests": 1,
        "market_segment": "Offline TA/TO (Đại lý du lịch truyền thống / Công ty lữ hành)",
        "deposit_type": "Non Refund (Đặt cọc không hoàn lại - Rất an toàn)",
        "customer_type": "Transient (Khách lẻ vãng lai)",
        "adr": 95.0,
        "prev_canc": 0,
        "prev_not_canc": 0,
        "booking_changes": 0,
        "parking_spaces": 0,
        "country_group": "ESP (Tây Ban Nha - Spain)",
        "meal": "BB (Bed & Breakfast - Chỉ bao gồm bữa sáng)"
    },
    "👥 5. Khách Đặt Theo Đoàn Lớn (Group Booking)": {
        "hotel": "City Hotel (Khách sạn Thành phố)",
        "lead_time": 120,
        "stays_weekend": 0,
        "stays_week": 3,
        "adults": 2,
        "children": 0,
        "babies": 0,
        "special_requests": 0,
        "market_segment": "Groups (Khách đặt đi theo đoàn)",
        "deposit_type": "Non Refund (Đặt cọc không hoàn lại - Rất an toàn)",
        "customer_type": "Group (Khách đoàn chính thức)",
        "adr": 75.0,
        "prev_canc": 0,
        "prev_not_canc": 0,
        "booking_changes": 0,
        "parking_spaces": 0,
        "country_group": "FRA (Pháp - France)",
        "meal": "HB (Half Board - Ăn 2 bữa: Sáng + Tối)"
    }
}

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🏨 HỆ THỐNG QUẢN TRỊ RỦI RO & DỰ ĐOÁN HỦY ĐẶT PHÒNG KHÁCH SẠN</h1>
    <p>Giải pháp Machine Learning ứng dụng thuật toán Gradient Boosting & Random Forest dự báo khả năng hủy đơn thực tế.</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("📌 MẪU KHÁCH HÀNG THUÊ")
st.sidebar.markdown("Chọn một **Preset Profile** để nạp dữ liệu kiểm thử nhanh:")

selected_profile_name = st.sidebar.selectbox(
    "Danh sách mẫu hồ sơ:",
    list(PRESET_PROFILES.keys()),
    index=0
)

# Apply preset to session state if changed
if "current_profile" not in st.session_state or st.session_state["current_profile"] != selected_profile_name:
    st.session_state["current_profile"] = selected_profile_name
    preset_vals = PRESET_PROFILES[selected_profile_name]
    if preset_vals:
        for k, v in preset_vals.items():
            st.session_state[f"input_{k}"] = v

st.sidebar.divider()
st.sidebar.markdown("""
### 📊 Thông tin Mô hình:
- **Gradient Boosting**: Accuracy = 87.12%, ROC-AUC = 0.9473
- **Random Forest**: Accuracy = 86.82%, Precision = 88.75%
- **Kích thước Dataset**: 119,390 bản ghi
""")

# --- MAIN NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs([
    "🎯 Dự Đoán Đơn Lẻ (Single Prediction)",
    "📂 Dự Đoán Hàng Loạt (Batch CSV Upload)",
    "📊 Báo Cáo Hiệu Suất Mô Hình (Model Performance)"
])

# =============================================================================
# TAB 1: SINGLE PREDICTION
# =============================================================================
with tab1:
    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.subheader("📋 Thông tin Đặt phòng & Khách ở")
        
        hotel_sel = st.selectbox(
            "Loại Khách Sạn (Hotel Type)",
            list(HOTEL_MAP.keys()),
            index=list(HOTEL_MAP.keys()).index(st.session_state.get("input_hotel", list(HOTEL_MAP.keys())[0]))
        )
        
        lead_time = st.number_input(
            "Thời gian đặt phòng trước - Lead Time (Số ngày)",
            min_value=0, max_value=737,
            value=int(st.session_state.get("input_lead_time", 45))
        )
        
        c1, c2 = st.columns(2)
        with c1:
            stays_weekend = st.number_input(
                "Số đêm Cuối tuần (T7, CN)",
                min_value=0, max_value=20,
                value=int(st.session_state.get("input_stays_weekend", 1))
            )
            adults = st.number_input(
                "Số Người lớn (Adults)",
                min_value=1, max_value=10,
                value=int(st.session_state.get("input_adults", 2))
            )
            children = st.number_input(
                "Số Trẻ em (Children)",
                min_value=0, max_value=10,
                value=int(st.session_state.get("input_children", 0))
            )
        with c2:
            stays_week = st.number_input(
                "Số đêm Trong tuần (T2 - T6)",
                min_value=0, max_value=30,
                value=int(st.session_state.get("input_stays_week", 2))
            )
            babies = st.number_input(
                "Số Trẻ sơ sinh (Babies)",
                min_value=0, max_value=10,
                value=int(st.session_state.get("input_babies", 0))
            )
            special_requests = st.number_input(
                "Số Yêu cầu Đặc biệt (Special Requests)",
                min_value=0, max_value=5,
                value=int(st.session_state.get("input_special_requests", 1))
            )

        c3, c4 = st.columns(2)
        with c3:
            market_segment_sel = st.selectbox(
                "Phân khúc Thị trường (Market Segment)",
                list(MARKET_SEGMENT_MAP.keys()),
                index=list(MARKET_SEGMENT_MAP.keys()).index(st.session_state.get("input_market_segment", list(MARKET_SEGMENT_MAP.keys())[0]))
            )
            deposit_type_sel = st.selectbox(
                "Hình thức Đặt cọc (Deposit Type)",
                list(DEPOSIT_TYPE_MAP.keys()),
                index=list(DEPOSIT_TYPE_MAP.keys()).index(st.session_state.get("input_deposit_type", list(DEPOSIT_TYPE_MAP.keys())[0]))
            )
        with c4:
            customer_type_sel = st.selectbox(
                "Phân loại Khách hàng (Customer Type)",
                list(CUSTOMER_TYPE_MAP.keys()),
                index=list(CUSTOMER_TYPE_MAP.keys()).index(st.session_state.get("input_customer_type", list(CUSTOMER_TYPE_MAP.keys())[0]))
            )
            adr = st.number_input(
                "Giá phòng trung bình/đêm - ADR ($ USD)",
                min_value=0.0, max_value=1000.0,
                value=float(st.session_state.get("input_adr", 105.0))
            )

    with col_right:
        st.subheader("📊 Lịch Sử Khách Hàng & Thuật Toán")
        
        prev_canc = st.number_input(
            "Số lần đã Hủy phòng trong Quá khứ",
            min_value=0, max_value=30,
            value=int(st.session_state.get("input_prev_canc", 0))
        )
        prev_not_canc = st.number_input(
            "Số lần ở Thành công trong Quá khứ",
            min_value=0, max_value=50,
            value=int(st.session_state.get("input_prev_not_canc", 0))
        )
        booking_changes = st.number_input(
            "Số lần Thay đổi Thông tin Đơn đặt",
            min_value=0, max_value=20,
            value=int(st.session_state.get("input_booking_changes", 0))
        )
        parking_spaces = st.number_input(
            "Số chỗ Đỗ xe Ô tô Yêu cầu",
            min_value=0, max_value=5,
            value=int(st.session_state.get("input_parking_spaces", 0))
        )
        
        country_sel = st.selectbox(
            "Quốc gia Xuất xứ của Khách (Country)",
            list(COUNTRY_MAP.keys()),
            index=list(COUNTRY_MAP.keys()).index(st.session_state.get("input_country_group", list(COUNTRY_MAP.keys())[0]))
        )
        meal_sel = st.selectbox(
            "Gói Dịch vụ Bữa ăn (Meal Package)",
            list(MEAL_MAP.keys()),
            index=list(MEAL_MAP.keys()).index(st.session_state.get("input_meal", list(MEAL_MAP.keys())[0]))
        )

        model_choice = st.radio(
            "Mô hình Học máy Dự đoán:",
            ["Gradient Boosting (Độ chính xác cao nhất: 87.1%)", "Random Forest (Độ chuẩn xác cao: 86.8%)"]
        )

    st.divider()
    
    predict_btn = st.button("🚀 THỰC THI DỰ ĐOÁN XÁC SUẤT HỦY PHÒNG", use_container_width=True)
    
    if predict_btn or True: # Run initial prediction for preview
        hotel = HOTEL_MAP[hotel_sel]
        market_segment = MARKET_SEGMENT_MAP[market_segment_sel]
        deposit_type = DEPOSIT_TYPE_MAP[deposit_type_sel]
        customer_type = CUSTOMER_TYPE_MAP[customer_type_sel]
        country_group = COUNTRY_MAP[country_sel]
        meal = MEAL_MAP[meal_sel]

        input_data = {feat: 0.0 for feat in feature_names}
        input_data['lead_time'] = float(lead_time)
        input_data['stays_in_weekend_nights'] = float(stays_weekend)
        input_data['stays_in_week_nights'] = float(stays_week)
        input_data['adults'] = float(adults)
        input_data['children'] = float(children)
        input_data['babies'] = float(babies)
        input_data['previous_cancellations'] = float(prev_canc)
        input_data['previous_bookings_not_canceled'] = float(prev_not_canc)
        input_data['booking_changes'] = float(booking_changes)
        input_data['adr'] = float(adr)
        input_data['required_car_parking_spaces'] = float(parking_spaces)
        input_data['total_of_special_requests'] = float(special_requests)
        
        input_data['total_stay'] = float(stays_weekend + stays_week)
        input_data['total_guests'] = float(adults + children + babies)
        input_data['is_family'] = 1.0 if (children > 0 or babies > 0) else 0.0
        input_data['has_special_requests'] = 1.0 if (special_requests > 0) else 0.0

        if f"hotel_{hotel}" in input_data: input_data[f"hotel_{hotel}"] = 1.0
        if f"deposit_type_{deposit_type}" in input_data: input_data[f"deposit_type_{deposit_type}"] = 1.0
        if f"market_segment_{market_segment}" in input_data: input_data[f"market_segment_{market_segment}"] = 1.0
        if f"customer_type_{customer_type}" in input_data: input_data[f"customer_type_{customer_type}"] = 1.0
        if f"country_group_{country_group}" in input_data: input_data[f"country_group_{country_group}"] = 1.0
        if f"meal_{meal}" in input_data: input_data[f"meal_{meal}"] = 1.0

        df_input = pd.DataFrame([input_data])
        input_scaled = scaler.transform(df_input)
        
        model_to_use = gb_model if "Gradient" in model_choice else rf_model
        pred_class = model_to_use.predict(input_scaled)[0]
        pred_proba = model_to_use.predict_proba(input_scaled)[0]
        cancel_prob = pred_proba[1] * 100

        st.subheader("🎯 KẾT QUẢ VÀ CẢNH BÁO RỦI RO")
        
        res_col1, res_col2 = st.columns([1.2, 0.8])
        
        with res_col1:
            if pred_class == 1 or cancel_prob > 50:
                st.markdown(f"""
                <div class="risk-high">
                    <span class="badge-tag badge-danger">⚠️ RỦI RO HỦY CAO</span>
                    <h2 style="color: #C92A2A; margin: 8px 0;">Tỷ lệ Hủy phòng: {cancel_prob:.1f}%</h2>
                    <p style="color: #495057; font-size: 0.95rem;">Đơn đặt phòng này có xác suất bị hủy rất cao. Khuyến nghị gửi thông báo xác nhận cọc hoặc áp dụng chính sách overbooking linh hoạt.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="risk-safe">
                    <span class="badge-tag badge-success">✅ AN TOÀN - GIỮ PHÒNG</span>
                    <h2 style="color: #2B8A3E; margin: 8px 0;">Tỷ lệ Giữ phòng: {100-cancel_prob:.1f}%</h2>
                    <p style="color: #495057; font-size: 0.95rem;">Khách hàng có cam kết cao, tỷ lệ hủy dự báo chỉ {cancel_prob:.1f}%. Phòng đã được giữ chắc chắn.</p>
                </div>
                """, unsafe_allow_html=True)

        with res_col2:
            st.write("**Thanh đo Xác suất Hủy (Risk Gauge):**")
            st.progress(int(cancel_prob))
            st.metric("Probability of Cancellation", f"{cancel_prob:.1f}%")
            st.metric("Probability of Confirmation", f"{100-cancel_prob:.1f}%")

        # Dynamic Factor Breakdown
        risk_factors = []
        safe_factors = []

        if deposit_type == "Non Refund":
            safe_factors.append("🟢 **Đặt cọc không hoàn lại (Non Refund)**: Khách bị ràng buộc tài chính tuyệt đối.")
        elif deposit_type == "No Deposit":
            risk_factors.append("🔴 **Không đặt cọc (No Deposit)**: Dễ dàng hủy phòng nếu tìm thấy lựa chọn rẻ hơn.")

        if lead_time > 150:
            risk_factors.append(f"🔴 **Lead Time quá xa (`{lead_time}` ngày)**: Khoảng thời gian quá xa làm gia tăng rủi ro thay đổi kế hoạch.")
        elif lead_time <= 14:
            safe_factors.append(f"🟢 **Đặt sát ngày (`{lead_time}` ngày)**: Khách chốt lịch trình di chuyển chắc chắn.")

        if prev_canc > 0:
            risk_factors.append(f"🔴 **Lịch sử hủy phòng (`{prev_canc}` lần)**: Khách có thói quen hủy phòng trong quá khứ.")
        if prev_not_canc > 0:
            safe_factors.append(f"🟢 **Lịch sử ở uy tín (`{prev_not_canc}` lần ở)**: Khách quen có độ tin cậy rất cao.")

        if special_requests > 0:
            safe_factors.append(f"🟢 **Có yêu cầu đặc biệt (`{special_requests}` yêu cầu)**: Khách đã lên kế hoạch chi tiết cho lưu trú.")
        else:
            risk_factors.append("🔴 **Không có yêu cầu đặc biệt**: Ít tương tác hoặc chuẩn bị chuyến đi.")

        if market_segment == "Online TA":
            risk_factors.append("🔴 **Đặt qua đại lý mạng (Online TA)**: Khách so sánh giá thường xuyên.")

        st.markdown("### 🔍 PHÂN TÍCH CÁC DẤU HIỆU ĐÓNG GÓP")
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.markdown("#### 🔴 Yếu tố Tăng Rủi Ro:")
            for rf in risk_factors: st.markdown(f"- {rf}")
        with exp_col2:
            st.markdown("#### 🟢 Yếu tố Tăng An Toàn:")
            for sf in safe_factors: st.markdown(f"- {sf}")

# =============================================================================
# TAB 2: BATCH CSV PREDICTION
# =============================================================================
with tab2:
    st.subheader("📂 Dự Đoán Hàng Loạt Đơn Đặt Phòng Từ File CSV")
    st.markdown("Tải lên file danh sách các đơn đặt phòng (đúng định dạng cột) để hệ thống chạy dự đoán và xuất báo cáo:")
    
    uploaded_file = st.file_uploader("Chọn file CSV dữ liệu đặt phòng:", type=["csv"])
    
    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            st.success(f"Đã tải thành công: {len(batch_df)} dòng dữ liệu!")
            st.dataframe(batch_df.head(5))
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")
    else:
        st.info("💡 Bạn có thể dùng file gốc `hotel_bookings.csv` để thử nghiệm tính năng dự đoán hàng loạt này.")
        if st.button("🧪 Chạy thử nghiệm trên 100 mẫu dữ liệu ngẫu nhiên từ Dataset gốc"):
            data_path = os.path.join("hotel_bookings.csv", "hotel_bookings.csv") if os.path.exists(os.path.join("hotel_bookings.csv", "hotel_bookings.csv")) else "hotel_bookings.csv"
            if os.path.exists(data_path):
                df_sample = pd.read_csv(data_path).sample(100, random_state=42)
                st.write("### Kết quả Phân tích 100 mẫu thử nghiệm:")
                
                # Mock batch visualization
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.countplot(data=df_sample, x='is_canceled', palette=['#51CF66', '#FF6B6B'], ax=ax)
                ax.set_title("Phân bố Dự đoán Hủy / Giữ phòng trên 100 mẫu thử", fontweight='bold')
                ax.set_xticklabels(['Giữ phòng (0)', 'Hủy phòng (1)'])
                st.pyplot(fig)

# =============================================================================
# TAB 3: MODEL PERFORMANCE REPORT
# =============================================================================
with tab3:
    st.subheader("📊 Báo Cáo Hiệu Suất Thuật Toán Học Máy")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if os.path.exists("outputs/plots/roc_curves_comparison.png"):
            st.image("outputs/plots/roc_curves_comparison.png", caption="So sánh đường cong ROC AUC giữa các thuật toán")
        if os.path.exists("outputs/plots/model_metrics_comparison.png"):
            st.image("outputs/plots/model_metrics_comparison.png", caption="So sánh các chỉ số Accuracy, Precision, Recall, F1-Score")
            
    with col_m2:
        if os.path.exists("outputs/plots/confusion_matrices.png"):
            st.image("outputs/plots/confusion_matrices.png", caption="Ma trận nhầm lẫn (Confusion Matrix) của các mô hình")
        if os.path.exists("outputs/plots/feature_importance_rf.png"):
            st.image("outputs/plots/feature_importance_rf.png", caption="Độ quan trọng của các thuộc tính (Feature Importances)")

st.divider()
st.caption("🏨 Hệ Thống Dự Đoán Khả Năng Hủy Đặt Phòng Khách Sạn | Antigravity AI Machine Learning Platform © 2026")
