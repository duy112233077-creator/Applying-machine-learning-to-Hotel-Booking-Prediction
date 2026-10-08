# 🏨 Hotel Booking Cancellation Prediction

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-v1.2%2B-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Bài tập lớn Học máy nâng cao: **Dự đoán khả năng hủy đặt phòng khách sạn bằng các thuật toán Machine Learning (Hotel Booking Cancellation Prediction)**.

Dự án cung cấp quy trình phân tích dữ liệu toàn diện (EDA), làm sạch dữ liệu, xử lý mất cân bằng nhãn bằng **SMOTE**, huấn luyện & đánh giá 5 thuật toán Machine Learning, đồng thời triển khai **Ứng dụng Web tương tác bằng Streamlit**.

---

## 📌 1. Giới Thiệu Đề Tài

Trong ngành dịch vụ khách sạn & lưu trú, việc khách hàng hủy phòng đột ngột không thông báo trước gây tổn thất lớn về doanh thu và lãng phí chi phí vận hành. 

**Mục tiêu của dự án:**
- Phân tích 119,390 đơn đặt phòng để tìm ra các thuộc tính có nguy cơ rủi ro cao (Lead time, Deposit type, Market segment...).
- Huấn luyện các mô hình dự báo với độ chính xác cao (**Accuracy > 87%**, **ROC-AUC > 0.947**).
- Triển khai ứng dụng Web trợ lý thông minh hỗ trợ Ban quản lý khách sạn ra quyết định **Overbooking** và yêu cầu đặt cọc linh hoạt.

---

## 📊 2. Kết Quả Huấn Luyện Các Mô Hình (Model Comparison)

Thực nghiệm so sánh trên 5 thuật toán Machine Learning:

| Thuật Toán Mô Hình | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🥇 **Gradient Boosting** | **0.8712** | 0.8572 | **0.7826** | **0.8182** | **0.9473** |
| 🥈 **Random Forest** | 0.8682 | **0.8875** | 0.7378 | 0.8058 | 0.9465 |
| 🥉 **XGBoost** | 0.8666 | 0.8585 | 0.7661 | 0.8097 | 0.9437 |
| 🔹 **Decision Tree** | 0.8520 | 0.8278 | 0.7581 | 0.7914 | 0.9285 |
| 🔹 **Logistic Regression** | 0.8190 | 0.8100 | 0.6681 | 0.7322 | 0.8979 |

---

## 🛠️ 3. Cấu Trúc Thư Mục Dự Án

```text
├── app.py                                  # Ứng dụng Web tương tác Streamlit (Main Web Dashboard)
├── run_pipeline.py                         # Quy trình xử lý dữ liệu, huấn luyện & xuất mô hình ML
├── Hotel_Booking_Cancellation_Prediction.ipynb # Jupyter Notebook phân tích chi tiết từng bước
├── Bao_Cao_BTL_Hoc_May_Hotel_Booking.docx  # Báo cáo Word hoàn chỉnh theo chuẩn mẫu BTL
├── hotel_bookings.csv/                     # Bộ dữ liệu gốc Hotel Booking Demand (119,390 dòng)
├── requirements.txt                        # Danh sách thư viện Python phụ thuộc
├── outputs/                                # Thư mục chứa mô hình & đồ thị kết quả
│   ├── models/                             # File pickle mô hình đã nén (Random Forest, Gradient Boosting...)
│   └── plots/                              # 15 đồ thị EDA & so sánh mô hình (Confusion Matrix, ROC Curve...)
└── README.md
```

---

## 🚀 4. Hướng Dẫn Cài Đặt Và Chạy Ứng Dụng Web

### 1️⃣ Cài đặt môi trường
Yêu cầu Python version 3.10 trở lên:
```bash
pip install -r requirements.txt
```

### 2️⃣ Chạy lại Pipeline Huấn luyện Mô hình (Tùy chọn)
```bash
python run_pipeline.py
```

### 3️⃣ Khởi chạy ứng dụng Web Streamlit
```bash
streamlit run app.py
```
Sau khi chạy command trên, truy cập đường dẫn local: `http://localhost:8501` trên trình duyệt.

---

## 📷 5. Giao Diện Ứng Dụng Streamlit

- **Preset Profiles**: Nạp sẵn 5 mẫu khách hàng thực tế (Khách gia đình, Doanh nhân, Khách săn sale Online TA...).
- **Risk Progress Gauge**: Hiển thị tỷ lệ xác suất % hủy phòng & cảnh báo rủi ro màu trực quan.
- **Dynamic Breakdown**: Tự động giải thích nguyên nhân tăng/giảm rủi ro và đưa ra khuyến nghị vận hành.

---

## 👤 Tác Giả

- **Sinh viên thực hiện**: Lê Đức Tuyển - Tạ Quang Đại
- **Lớp**: 12422TN - Trường Đại học Sư phạm Kỹ thuật Hưng Yên
- **Giảng viên hướng dẫn**: TS. Hoàng Quốc Việt
>>>>>>> de24b50 (Initial commit: Hotel Booking Cancellation Prediction Machine Learning project and Streamlit Web App)
