import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_streamlit_ui_mockup():
    os.makedirs("outputs/plots", exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Background
    ax.add_patch(patches.Rectangle((0, 0), 100, 100, facecolor='#F8F9FA'))
    
    # Header bar
    ax.add_patch(patches.Rectangle((0, 90), 100, 10, facecolor='#0D6EFD'))
    ax.text(3, 94, "🏨 HỆ THỐNG DỰ ĐOÁN KHẢ NĂNG HỦY ĐẶT PHÒNG KHÁCH SẠN", 
            fontsize=14, color='white', fontweight='bold', va='center')
    
    # Sidebar
    ax.add_patch(patches.Rectangle((0, 0), 25, 90, facecolor='#E9ECEF'))
    ax.text(2, 85, "⚙️ Tùy chọn Hồ sơ", fontsize=11, fontweight='bold', color='#212529')
    
    profiles = [
        "✍️ Tự nhập thủ công",
        "👨‍👩‍👧‍👦 1. Khách Gia Đình Nghỉ Mát",
        "💼 2. Khách Doanh Nhân",
        "⚠️ 3. Khách Săn Sale Mạng",
        "🛡️ 4. Khách Cọc Non-Refund"
    ]
    for i, p in enumerate(profiles):
        y = 78 - i * 6
        bg_col = '#0D6EFD' if i == 3 else '#FFFFFF'
        txt_col = '#FFFFFF' if i == 3 else '#212529'
        ax.add_patch(patches.Rectangle((2, y-2), 21, 5, facecolor=bg_col, edgecolor='#CED4DA'))
        ax.text(3, y, p, fontsize=8.5, color=txt_col, va='center')

    # Main content panel
    ax.add_patch(patches.Rectangle((28, 50), 69, 37, facecolor='#FFFFFF', edgecolor='#DEE2E6'))
    ax.text(30, 83, "📋 Thông tin Chi Tiết Đơn Đặt Phòng", fontsize=12, fontweight='bold', color='#0D6EFD')
    
    # Inputs simulation
    inputs = [
        ("Khách sạn:", "City Hotel"), ("Thời gian đặt trước (lead_time):", "260 ngày"),
        ("Loại cọc (deposit_type):", "No Deposit"), ("Phân khúc (market_segment):", "Online TA"),
        ("Giá phòng (adr):", "85.0 EUR/đêm"), ("Lịch sử hủy trước (prev_canc):", "2 lần")
    ]
    for i, (label, val) in enumerate(inputs):
        x = 30 if i % 2 == 0 else 65
        y = 75 - (i // 2) * 8
        ax.text(x, y, label, fontsize=9, color='#495057')
        ax.add_patch(patches.Rectangle((x, y-4), 30, 3.5, facecolor='#F1F3F5', edgecolor='#CED4DA'))
        ax.text(x+1, y-2.2, val, fontsize=8.5, color='#212529', fontweight='bold')

    # Prediction Result Panel
    ax.add_patch(patches.Rectangle((28, 8), 69, 38, facecolor='#FFF5F5', edgecolor='#FA5252'))
    ax.text(30, 42, "🎯 KẾT QUẢ DỰ ĐOÁN TỪ MÔ HÌNH HỌC MÁY", fontsize=12, fontweight='bold', color='#C92A2A')
    
    # Metrics
    ax.add_patch(patches.Rectangle((30, 24), 31, 14, facecolor='#FFE3E3', edgecolor='#FFA8A8'))
    ax.text(32, 34, "XÁC SUẤT HỦY PHÒNG", fontsize=9, color='#C92A2A')
    ax.text(32, 28, "86.4%", fontsize=18, fontweight='bold', color='#E03131')
    
    ax.add_patch(patches.Rectangle((64, 24), 31, 14, facecolor='#FFE3E3', edgecolor='#FFA8A8'))
    ax.text(66, 34, "MỨC ĐỘ RỦI RO", fontsize=9, color='#C92A2A')
    ax.text(66, 28, "⚠️ RỦI RO CAO", fontsize=14, fontweight='bold', color='#E03131')
    
    # Action Recommendation
    ax.text(30, 18, "💡 KHUYẾN NGHỊ HÀNH ĐỘNG DÀNH CHO QUẢN LÝ KHÁCH SẠN:", fontsize=9.5, fontweight='bold', color='#C92A2A')
    ax.text(30, 13, "• Đơn có thời gian chờ xa (260 ngày) & lịch sử hủy 2 lần. Cần liên hệ gửi email/tin nhắn xác nhận.", fontsize=8.5, color='#212529')
    ax.text(30, 9.5, "• Khuyến nghị yêu cầu thanh toán cọc trước 30% hoặc áp dụng chính sách overbooking linh hoạt.", fontsize=8.5, color='#212529')
    
    plt.tight_layout()
    output_path = "outputs/plots/streamlit_app_ui.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"UI mockup plot generated: {output_path}")

if __name__ == '__main__':
    generate_streamlit_ui_mockup()
