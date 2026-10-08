import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout_box(doc, text_list, bg_hex="F8F9FA", border_hex="0D6EFD"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Border
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.25
    
    for i, line in enumerate(text_list):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.25
        run = p.add_run(line)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x21, 0x25, 0x29)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F1F3F5")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="12" w:space="0" w:color="CED4DA"/>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="E9ECEF"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="E9ECEF"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="E9ECEF"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    lines = code_text.strip().split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)

def main():
    doc = docx.Document()

    # Page Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.79)

    # Style defaults
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Helper function for headings
    def add_title(text, level=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 0 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.bold = True
        
        if level == 0: # Header info
            run.font.size = Pt(14)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
        elif level == 1: # Chapter Title
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
        elif level == 2: # Section Title
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(0x00, 0x22, 0x44)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
        elif level == 3: # Sub-section Title
            run.font.size = Pt(13)
            run.font.italic = True
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
        return p

    def add_body_p(text, bold_prefix="", space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(0)
        
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.bold = True
            r_bold.font.name = 'Times New Roman'
            r_bold.font.size = Pt(13)
            
        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(13)
        return p

    def add_img(img_path, caption, width_in=5.8):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_in))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(11)
            r_cap.font.italic = True
            r_cap.font.bold = True
            r_cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # -------------------------------------------------------------
    # TRANG BÌA (COVER PAGE)
    # -------------------------------------------------------------
    p_header1 = add_title("BỘ GIÁO DỤC VÀ ĐÀO TẠO", level=0)
    p_header2 = add_title("TRƯỜNG ĐẠI HỌC SƯ PHẠM KỸ THUẬT HƯNG YÊN", level=0)
    
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(36)
    
    p_btl = doc.add_paragraph()
    p_btl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_btl = p_btl.add_run("BÀI TẬP LỚN\nHỌC MÁY CƠ BẢN")
    r_btl.font.size = Pt(22)
    r_btl.font.bold = True
    r_btl.font.name = 'Times New Roman'
    p_btl.paragraph_format.space_after = Pt(24)

    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_topic = p_topic.add_run("ĐỀ TÀI: DỰ ĐOÁN KHẢ NĂNG HỦY ĐẶT PHÒNG KHÁCH SẠN BẰNG CÁC THUẬT TOÁN HỌC MÁY\n(HOTEL BOOKING CANCELLATION PREDICTION)")
    r_topic.font.size = Pt(16)
    r_topic.font.bold = True
    r_topic.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    p_topic.paragraph_format.space_after = Pt(40)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.line_spacing = 1.4
    r_info = p_info.add_run(
        "NGÀNH: CÔNG NGHỆ PHẦN MỀM\n\n"
        "SINH VIÊN THỰC HIỆN: LÊ ĐỨC TUYỂN - TẠ QUANG ĐẠI\n"
        "LỚP: 12422TN\n"
        "NGƯỜI HƯỚNG DẪN: TS. HOÀNG QUỐC VIỆT"
    )
    r_info.font.size = Pt(13)
    r_info.font.bold = True
    r_info.font.name = 'Times New Roman'

    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(60)

    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_footer = p_footer.add_run("HƯNG YÊN – 2026")
    r_footer.font.size = Pt(13)
    r_footer.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # TRANG NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN
    # -------------------------------------------------------------
    add_title("NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN", level=1)
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    add_body_p(".........................................................................................................................................................")
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(30)
    r_sign = p_sign.add_run("GIÁO VIÊN HƯỚNG DẪN\n\n\n\nTS. Hoàng Quốc Việt")
    r_sign.font.bold = True
    r_sign.font.size = Pt(13)

    doc.add_page_break()

    # -------------------------------------------------------------
    # MỤC LỤC VÀ DANH MỤC HÌNH VẼ
    # -------------------------------------------------------------
    add_title("MỤC LỤC", level=1)
    
    toc_items = [
        ("CHƯƠNG 1: GIỚI THIỆU BÀI TOÁN", "4"),
        ("  1.1 Bài toán và Ý nghĩa thực tiễn", "4"),
        ("  1.2 Trình bày dữ liệu bài toán", "4"),
        ("  1.3 Tiền xử lý dữ liệu", "6"),
        ("  1.4 Làm sạch dữ liệu", "6"),
        ("  1.5 Trực quan hoá dữ liệu (EDA)", "7"),
        ("CHƯƠNG 2: CƠ SỞ LÝ THUYẾT", "9"),
        ("  2.1 Thuật toán Hồi quy Logistic (Logistic Regression)", "9"),
        ("  2.2 Thuật toán Cây quyết định (Decision Tree Classifier)", "9"),
        ("  2.3 Thuật toán Rừng ngẫu nhiên (RandomForestClassifier)", "10"),
        ("  2.4 Thuật toán Gradient Boosting Classifier", "11"),
        ("  2.5 Thuật toán XGBoost Classifier", "12"),
        ("  2.6 Các độ đo đánh giá hiệu suất mô hình", "12"),
        ("CHƯƠNG 3: GIẢI PHÁP, CÀI ĐẶT THỰC HIỆN", "14"),
        ("  3.1 Mã nguồn tiền xử lý dữ liệu", "14"),
        ("  3.2 Mã nguồn chức năng làm sạch dữ liệu", "14"),
        ("  3.3 Mã nguồn chức năng Trực quan hóa dữ liệu", "17"),
        ("  3.4 Mã nguồn Chuyển đổi dữ liệu & SMOTE", "20"),
        ("  3.5 Huấn luyện và Đánh giá các mô hình SKLEARN", "22"),
        ("CHƯƠNG 4: XÂY DỰNG ỨNG DỤNG", "26"),
        ("  4.1 Giới thiệu ứng dụng Web Streamlit", "26"),
        ("  4.2 Mã nguồn và giao diện dự đoán trực quan", "26"),
        ("KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO", "28"),
    ]
    
    for item, page in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.line_spacing = 1.25
        p_toc.paragraph_format.space_after = Pt(3)
        r_item = p_toc.add_run(item.ljust(90, '.'))
        if item.startswith("CHƯƠNG") or item.startswith("KẾT LUẬN"):
            r_item.font.bold = True
        r_page = p_toc.add_run(f" {page}")
        r_page.font.bold = True

    add_title("DANH MỤC CÁC HÌNH VẼ, ĐỒ THỊ", level=1)
    fig_items = [
        ("Hình 3.1: Kiểm tra tỷ lệ phần trăm giá trị thiếu của từng thuộc tính", "15"),
        ("Hình 3.2: Boxplot kiểm tra dữ liệu ngoại lai trước và sau khi xử lý bằng IQR", "16"),
        ("Hình 3.3: Heatmap ma trận tương quan giữa các đặc trưng", "17"),
        ("Hình 3.4: Biểu đồ kết hợp Bar và Pie chart thể hiện phân phối nhãn target", "17"),
        ("Hình 3.5: Biểu đồ Pie chart phân phối các thuộc tính phân loại", "18"),
        ("Hình 3.6: Mối tương quan giữa hình thức đặt cọc (Deposit Type) và tỷ lệ hủy phòng", "18"),
        ("Hình 3.7: So sánh tỷ lệ hủy phòng giữa Khách sạn Thành phố và Khách sạn Nghỉ dưỡng", "19"),
        ("Hình 3.8: Biểu đồ Scatter minh họa mối quan hệ giữa Lead Time và ADR", "19"),
        ("Hình 3.9: Biểu đồ so sánh phân bố dữ liệu trước và sau khi áp dụng thuật toán SMOTE", "21"),
        ("Hình 3.10: Ma trận nhầm lẫn (Confusion Matrix) của 5 mô hình huấn luyện", "23"),
        ("Hình 3.11: Đồ thị đường cong ROC AUC so sánh hiệu suất giữa các mô hình", "24"),
        ("Hình 3.12: Biểu đồ cột so sánh chi tiết các chỉ số Accuracy, Precision, Recall, F1-Score", "24"),
        ("Hình 3.13: Đồ thị thể hiện 15 đặc trưng quan trọng nhất (Feature Importances)", "25"),
        ("Hình 4.1: Giao diện Web dự đoán hủy phòng khách sạn xây dựng bằng Streamlit", "27")
    ]
    for fig_title, page in fig_items:
        p_fig = doc.add_paragraph()
        p_fig.paragraph_format.line_spacing = 1.2
        p_fig.paragraph_format.space_after = Pt(3)
        r_f1 = p_fig.add_run(fig_title.ljust(90, '.'))
        r_f2 = p_fig.add_run(f" {page}")
        r_f2.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHƯƠNG 1: GIỚI THIỆU BÀI TOÁN
    # -------------------------------------------------------------
    add_title("CHƯƠNG 1: GIỚI THIỆU BÀI TOÁN", level=1)
    
    add_title("1.1 Bài toán và Ý nghĩa thực tiễn", level=2)
    add_body_p(
        "Trong ngành công nghiệp dịch vụ lưu trú và khách sạn, hiện tượng khách hàng hủy đặt phòng (Booking Cancellation) "
        "là một trong những thách thức lớn nhất ảnh hưởng trực tiếp đến doanh thu, chi phí vận hành và hiệu quả quản lý phòng. "
        "Khi khách hàng hủy phòng đột ngột mà không thông báo sớm, khách sạn rơi vào thế bị động: phòng bị bỏ trống, "
        "chi phí chuẩn bị dịch vụ bị lãng phí và mất đi cơ hội phục vụ các khách hàng tiềm năng khác."
    )
    add_body_p(
        "Nhằm giải quyết bài toán kinh doanh thực tế này, đề tài \"Áp dụng các thuật toán Học máy vào dự đoán khả năng hủy đặt phòng khách sạn\" "
        "được triển khai với các mục tiêu chính sau:"
    )
    add_body_p("• Phân tích chuyên sâu dữ liệu lịch sử đặt phòng để xác định các yếu tố rủi ro hàng đầu dẫn đến hành vi hủy phòng.", bold_prefix="")
    add_body_p("• Xây dựng và thực nghiệm các mô hình học máy phân loại (Classification Models) có độ chính xác cao.", bold_prefix="")
    add_body_p("• Cung cấp giải pháp dự báo sớm giúp nhà quản lý đưa ra chính sách cọc phòng hợp lý, linh hoạt hoặc áp dụng chiến lược đặt phòng vượt (Overbooking) một cách an toàn và tối ưu doanh thu.", bold_prefix="")

    add_callout_box(doc, [
        "Mục tiêu cốt lõi: Dự đoán chính xác nhãn 'is_canceled' (0: Không hủy, 1: Hủy phòng) dựa trên các thuộc tính về thời gian đặt trước (lead_time), loại tiền cọc (deposit_type), giá phòng trung bình (adr), quốc gia xuất xứ và lịch sử hủy phòng của khách hàng."
    ])

    add_title("1.2 Trình bày dữ liệu bài toán", level=2)
    add_body_p(
        "Bộ dữ liệu được sử dụng trong bài toán lấy từ Kaggle (Hotel Booking Demand Dataset), bao gồm 119,390 bản ghi "
        "với 32 thuộc tính chứa thông tin nhân khẩu học của khách hàng, thông tin đặt phòng, kênh phân phối và lịch sử lưu trú."
    )
    
    # Dataset dictionary table
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_titles = ["Tên Thuộc Tính", "Kiểu Dữ Liệu", "Mô Tả Chi Tiết"]
    for i, t in enumerate(hdr_titles):
        hdr_cells[i].text = t
        set_cell_background(hdr_cells[i], "003366")
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            
    attr_data = [
        ("hotel", "object", "Loại khách sạn (City Hotel hoặc Resort Hotel)"),
        ("is_canceled", "int64", "Nhãn mục tiêu (0: Không hủy phòng, 1: Đã hủy phòng)"),
        ("lead_time", "int64", "Số ngày giữa thời điểm đặt phòng và ngày nhận phòng"),
        ("arrival_date_year/month/day", "int/str", "Thời gian khách nhận phòng (Năm, Tháng, Tuần, Ngày)"),
        ("stays_in_weekend/week_nights", "int64", "Số đêm lưu trú vào cuối tuần / ngày trong tuần"),
        ("adults / children / babies", "int/float", "Số lượng người lớn, trẻ em và trẻ sơ sinh"),
        ("meal", "object", "Gói bữa ăn (BB: Sáng, HB: Sáng+Tối, FB: Trọn gói, SC: Tự túc)"),
        ("country", "object", "Quốc gia xuất xứ của khách hàng (Mã ISO 3-letter)"),
        ("market_segment", "object", "Phân khúc thị trường (Online TA, Offline TA, Direct, Corporate...)"),
        ("deposit_type", "object", "Hình thức cọc (No Deposit, Non Refund, Refundable)"),
        ("previous_cancellations", "int64", "Số lần khách hàng đã từng hủy phòng trong quá khứ"),
        ("booking_changes", "int64", "Số lần thay đổi/điều chỉnh chi tiết đặt phòng"),
        ("adr", "float64", "Giá phòng trung bình mỗi đêm (Average Daily Rate)"),
        ("required_car_parking_spaces", "int64", "Số chỗ đỗ xe khách yêu cầu"),
        ("total_of_special_requests", "int64", "Tổng số yêu cầu đặc biệt (tầng cao, giường đôi...)")
    ]
    
    for row_idx, (col, dtype, desc) in enumerate(attr_data):
        row_cells = table.add_row().cells
        row_cells[0].text = col
        row_cells[1].text = dtype
        row_cells[2].text = desc
        bg = "F8F9FA" if row_idx % 2 == 0 else "FFFFFF"
        for c_idx, cell in enumerate(row_cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    add_body_p("", space_after=6)
    add_body_p("Kết quả thống kê mô tả (Descriptive Statistics) cơ bản trên các đặc trưng số học chính:")
    add_body_p("• Tỷ lệ hủy phòng trung bình (is_canceled): 37.04% (44,224 đơn hủy / 119,390 tổng số đơn).", bold_prefix="")
    add_body_p("• Thời gian đặt trước (lead_time): Trung bình 104 ngày, lớn nhất lên tới 737 ngày.", bold_prefix="")
    add_body_p("• Giá phòng trung bình mỗi đêm (adr): Trung bình 101.83 EUR, dao động từ 0 đến 5,400 EUR (chứa giá trị ngoại lai).", bold_prefix="")

    add_title("1.3 Tiền xử lý dữ liệu", level=2)
    add_body_p(
        "Bước đầu tiên trong quy trình xử lý là kiểm tra cấu trúc dữ liệu (`df.info()`), loại bỏ các trường dữ liệu "
        "rác hoặc gây rò rỉ thông tin tương lai (Data Leakage) như `reservation_status` và `reservation_status_date`. "
        "Ngoài ra, các cột chứa mã định danh như `agent` và `company` có tỷ lệ khuyết thiếu quá cao cũng được xem xét xử lý."
    )

    add_title("1.4 Làm sạch dữ liệu", level=2)
    add_body_p(
        "• Xử lý giá trị thiếu (Missing Values): Cột `children` khuyết 4 giá trị được điền bằng 0; cột `country` khuyết 488 giá trị được điền nhãn 'Unknown'; cột `agent` khuyết 16,340 giá trị được thay bằng 0 (không qua đại lý).", bold_prefix=""
    )
    add_body_p(
        "• Xử lý giá trị ngoại lai (Outliers): Sử dụng phương pháp khoảng tứ phân vị IQR (Interquartile Range) để xác định và loại bỏ các bản ghi adr bất thường (như adr = 5,400 EUR hoặc adr < 0).", bold_prefix=""
    )
    add_body_p(
        "• Ma trận tương quan (Correlation Matrix): Tính toán hệ số tương quan Pearson giữa các thuộc tính số học với biến mục tiêu `is_canceled` để phát hiện các yếu tố có tác động mạnh nhất.", bold_prefix=""
    )

    add_title("1.5 Trực quan hoá dữ liệu (EDA)", level=2)
    add_body_p(
        "Khám phá dữ liệu bằng biểu đồ trực quan (EDA) mang lại các phát hiện quan trọng:"
    )
    add_body_p("1. Tỷ lệ hủy phòng giữa hai loại khách sạn: City Hotel có tỷ lệ hủy (41.7%) cao hơn đáng kể so với Resort Hotel (27.7%).")
    add_body_p("2. Tác động của hình thức cọc (Deposit Type): Đáng chú ý, nhóm đặt cọc không hoàn tiền (Non Refund) lại có tỷ lệ ghi nhận hủy cao do chính sách gom đơn của các đại lý tour du lịch.")
    add_body_p("3. Mối quan hệ giữa Lead Time và Cancellation: Thời gian đặt trước càng xa (lead_time lớn), xác suất khách hủy phòng càng gia tăng mạnh mẽ.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHƯƠNG 2: CƠ SỞ LÝ THUYẾT
    # -------------------------------------------------------------
    add_title("CHƯƠNG 2: CƠ SỞ LÝ THUYẾT", level=1)
    
    add_title("2.1 Thuật toán Hồi quy Logistic (Logistic Regression)", level=2)
    add_body_p(
        "Logistic Regression là mô hình phân loại tuyến tính cơ sở, dự đoán xác suất thuộc về một lớp bằng cách sử dụng hàm Sigmoid: "
        "P(y=1|X) = 1 / (1 + e^(-z)) với z = w^T X + b. "
        "Mô hình dễ cài đặt, tốc độ tính toán nhanh và cung cấp khả năng giải thích trọng số của từng đặc trưng rõ ràng."
    )

    add_title("2.2 Thuật toán Cây quyết định (Decision Tree Classifier)", level=2)
    add_body_p(
        "Decision Tree phân chia không gian đặc trưng thành các vùng hình chữ nhật bằng các câu hỏi điều kiện dạng Yes/No. "
        "Tại mỗi nút phân chia, thuật toán chọn thuộc tính giúp tối ưu độ tinh khiết (Purity) dựa trên chỉ số Gini Impurity hoặc Entropy. "
        "Cây quyết định phản ánh tự nhiên logic quy trình ra quyết định nhưng dễ bị quá khớp (Overfitting) nếu không giới hạn độ sâu."
    )

    add_title("2.3 Thuật toán Rừng ngẫu nhiên (RandomForestClassifier)", level=2)
    add_body_p(
        "Random Forest là phương pháp Học kết hợp (Ensemble Learning) dựa trên kỹ thuật Bagging. Thuật toán xây dựng hàng trăm cây quyết định "
        "độc lập trên các tập con dữ liệu ngẫu nhiên (Bootstrap Samples) và tập con thuộc tính ngẫu nhiên (Feature Subsets). "
        "Kết quả dự đoán cuối cùng là sự bỏ phiếu theo đa số (Majority Voting). Random Forest giảm thiểu đáng kể rủi ro quá khớp và có độ bền vững rất cao."
    )

    add_title("2.4 Thuật toán Gradient Boosting Classifier", level=2)
    add_body_p(
        "Gradient Boosting hoạt động theo cơ chế Boosting: xây dựng các cây quyết định nối tiếp nhau, trong đó cây sau tập trung học "
        "và sửa chữa sai số (Residual Errors) của cây phía trước bằng cách tối ưu hàm mất mát thông qua thuật toán Gradient Descent. "
        "Gradient Boosting thường đạt độ chính xác hàng đầu trên dữ liệu dạng bảng."
    )

    add_title("2.5 Thuật toán XGBoost Classifier", level=2)
    add_body_p(
        "XGBoost (Extreme Gradient Boosting) là phiên bản tối ưu hóa cao cấp của Gradient Boosting, tích hợp thành phần điều hòa L1/L2 (Regularization) "
        "để chống quá khớp, hỗ trợ tính toán song song đa nhân và xử lý giá trị thiếu tự động. Đây là thuật toán hiện đại được ưa chuộng nhất trong các cuộc thi Data Science."
    )

    add_title("2.6 Các độ đo đánh giá hiệu suất mô hình", level=2)
    add_body_p("• Accuracy (Độ chính xác tổng quan): Tỷ lệ các mẫu được dự đoán đúng trên tổng số mẫu.", bold_prefix="")
    add_body_p("• Precision (Độ chính xác lớp Hủy): Tỷ lệ đơn thực sự hủy trong số các đơn mô hình dự báo hủy.", bold_prefix="")
    add_body_p("• Recall (Độ nhạy / Tỷ lệ phát hiện): Tỷ lệ đơn hủy mà mô hình bắt được trên tổng số đơn hủy thực tế.", bold_prefix="")
    add_body_p("• F1-Score: Trung bình hài hòa giữa Precision và Recall, đánh giá sự cân bằng của mô hình.", bold_prefix="")
    add_body_p("• ROC-AUC Score: Diện tích dưới đường cong ROC, đánh giá khả năng phân biệt giữa lớp Hủy và Không Hủy ở các ngưỡng quyết định khác nhau.", bold_prefix="")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHƯƠNG 3: GIẢI PHÁP, CÀI ĐẶT THỰC HIỆN
    # -------------------------------------------------------------
    add_title("CHƯƠNG 3: GIẢI PHÁP, CÀI ĐẶT THỰC HIỆN", level=1)
    
    add_title("3.1 Mã nguồn tiền xử lý dữ liệu", level=2)
    add_body_p("Mã nguồn tải dữ liệu và kiểm tra cấu trúc ban đầu trong pipeline thực thi:")
    add_code_block(doc, """import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("hotel_bookings.csv")
print(f"Dataset Shape: {df.shape[0]} rows x {df.shape[1]} columns")

# Drop data leakage columns
df.drop(columns=['reservation_status', 'reservation_status_date'], inplace=True, errors='ignore')
""")

    add_title("3.2 Mã nguồn chức năng làm sạch dữ liệu", level=2)
    add_body_p("Đoạn mã xử lý giá trị thiếu và loại bỏ các dòng chứa thông tin ngoại lai bất thường:")
    add_code_block(doc, """# Fill Missing Values
df['children'].fillna(0, inplace=True)
df['country'].fillna('Unknown', inplace=True)
df['agent'].fillna(0, inplace=True)

# Outlier Filter using IQR for Average Daily Rate (ADR)
Q1 = df['adr'].quantile(0.25)
Q3 = df['adr'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['adr'] >= 0) & (df['adr'] <= Q3 + 3.0 * IQR)]
""")

    add_img("outputs/plots/eda_missing_values.png", "Hình 3.1: Kiểm tra tỷ lệ phần trăm giá trị thiếu của từng thuộc tính")
    add_img("outputs/plots/eda_lead_time_boxplot.png", "Hình 3.2: Boxplot kiểm tra dữ liệu ngoại lai của thuộc tính Lead Time")
    add_img("outputs/plots/eda_correlation_matrix.png", "Hình 3.3: Heatmap ma trận tương quan giữa các đặc trưng số học")

    add_title("3.3 Mã nguồn chức năng Trực quan hóa dữ liệu", level=2)
    add_body_p("Trực quan hóa phân phối nhãn target và mối tương quan giữa các đặc trưng quan trọng:")
    add_img("outputs/plots/eda_target_distribution_pie_bar.png", "Hình 3.4: Biểu đồ kết hợp Bar và Pie chart thể hiện phân phối nhãn target")
    add_img("outputs/plots/eda_categorical_pies.png", "Hình 3.5: Biểu đồ Pie chart phân phối các thuộc tính phân loại (Hotel, Customer Type...)")
    add_img("outputs/plots/eda_deposit_cancellation.png", "Hình 3.6: Mối tương quan giữa hình thức đặt cọc (Deposit Type) và tỷ lệ hủy phòng")
    add_img("outputs/plots/eda_hotel_cancellation.png", "Hình 3.7: So sánh tỷ lệ hủy phòng giữa Khách sạn Thành phố và Khách sạn Nghỉ dưỡng")
    add_img("outputs/plots/eda_leadtime_vs_adr_scatter.png", "Hình 3.8: Biểu đồ Scatter minh họa mối quan hệ giữa Lead Time và ADR")

    add_title("3.4 Mã nguồn Chuyển đổi dữ liệu & SMOTE", level=2)
    add_body_p(
        "Mã nguồn chuẩn hóa thuộc tính số bằng StandardScaler, mã hóa One-Hot cho thuộc tính phân loại "
        "và cân bằng nhãn bằng phương pháp SMOTE:"
    )
    add_code_block(doc, """from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# One-Hot Encoding
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Train Test Split
X = df_encoded.drop(columns=['is_canceled'])
y = df_encoded['is_canceled']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE Resampling
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
""")
    add_img("outputs/plots/smote_comparison_chart.png", "Hình 3.9: Biểu đồ so sánh phân bố dữ liệu trước và sau khi áp dụng thuật toán SMOTE")

    add_title("3.5 Huấn luyện và Đánh giá các mô hình SKLEARN", level=2)
    add_body_p("Kết quả thực nghiệm chi tiết của 5 thuật toán trên tập kiểm thử (Test Set):")

    # Table of results
    table_res = doc.add_table(rows=1, cols=6)
    table_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_hdr = table_res.rows[0].cells
    r_titles = ["Thuật Toán Mô Hình", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
    for i, t in enumerate(r_titles):
        r_hdr[i].text = t
        set_cell_background(r_hdr[i], "003366")
        p = r_hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.size = Pt(10.5)

    m_results = [
        ("Logistic Regression", "0.8190", "0.8100", "0.6681", "0.7322", "0.8979"),
        ("Decision Tree", "0.8520", "0.8278", "0.7581", "0.7914", "0.9285"),
        ("Random Forest", "0.8682", "0.8875", "0.7378", "0.8058", "0.9465"),
        ("Gradient Boosting", "0.8712", "0.8572", "0.7826", "0.8182", "0.9473"),
        ("XGBoost", "0.8666", "0.8585", "0.7661", "0.8097", "0.9437")
    ]

    for idx, (m_name, acc, prec, rec, f1, auc) in enumerate(m_results):
        row_cells = table_res.add_row().cells
        row_cells[0].text = m_name
        row_cells[1].text = acc
        row_cells[2].text = prec
        row_cells[3].text = rec
        row_cells[4].text = f1
        row_cells[5].text = auc
        bg = "EBF3FB" if idx in [2, 3] else ("F8F9FA" if idx % 2 == 0 else "FFFFFF")
        for c_idx, cell in enumerate(row_cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)
                if idx in [2, 3]:
                    r.font.bold = True

    add_body_p("", space_after=6)
    add_body_p(
        "Nhận xét kết quả: Mô hình Gradient Boosting đạt hiệu suất tổng thể cao nhất với Accuracy = 87.12%, F1-Score = 81.82% và ROC-AUC = 0.9473. "
        "Random Forest đạt Precision vượt trội (88.75%), cực kỳ thích hợp cho các kịch bản cần hạn chế tối đa báo động giả."
    )

    add_img("outputs/plots/confusion_matrices.png", "Hình 3.10: Ma trận nhầm lẫn (Confusion Matrix) của 5 mô hình huấn luyện")
    add_img("outputs/plots/roc_curves_comparison.png", "Hình 3.11: Đồ thị đường cong ROC AUC so sánh hiệu suất giữa các mô hình")
    add_img("outputs/plots/model_metrics_comparison.png", "Hình 3.12: Biểu đồ cột so sánh chi tiết các chỉ số Accuracy, Precision, Recall, F1-Score")
    add_img("outputs/plots/feature_importance_rf.png", "Hình 3.13: Đồ thị thể hiện 15 đặc trưng quan trọng nhất (Feature Importances) từ Random Forest")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHƯƠNG 4: XÂY DỰNG ỨNG DỤNG
    # -------------------------------------------------------------
    add_title("CHƯƠNG 4: XÂY DỰNG ỨNG DỤNG", level=1)
    
    add_title("4.1 Giới thiệu ứng dụng Web Streamlit", level=2)
    add_body_p(
        "Nhằm đưa các mô hình học máy vào thực tế kinh doanh vận hành khách sạn, ứng dụng Web dự đoán trực quan "
        "đã được phát triển dựa trên thư viện Streamlit (file `app.py`)."
    )
    add_body_p("Các tính năng nổi bật của ứng dụng:")
    add_body_p("1. Nạp tự động bộ mô hình đã đóng gói (Random Forest, Gradient Boosting, Scaler) qua `joblib`.")
    add_body_p("2. Tích hợp sẵn 4 Hồ sơ mẫu (Preset Profiles) đại diện cho các đối tượng khách phổ biến (Khách gia đình nghỉ mát, Khách doanh nhân, Khách săn sale mạng có rủi ro hủy cao, Khách cọc không hoàn lại).")
    add_body_p("3. Cho phép người dùng tùy chỉnh thủ công đầy đủ các thông tin đơn đặt phòng.")
    add_body_p("4. Tính toán xác suất hủy phòng (Cancel Probability %), đưa ra cảnh báo mức độ rủi ro (An toàn, Trung bình, Rủi ro cao) cùng khuyến nghị hành động cụ thể cho lễ tân / quản lý khách sạn.")

    add_title("4.2 Mã nguồn và giao diện ứng dụng", level=2)
    add_code_block(doc, """import streamlit as st
import joblib

# Load artifacts
rf_model = joblib.load("outputs/models/random_forest.pkl")
gb_model = joblib.load("outputs/models/gradient_boosting.pkl")

# Predict logic
prob = gb_model.predict_proba(input_scaled)[0][1]
st.metric("Xác suất Hủy phòng", f"{prob*100:.1f}%")
if prob > 0.6:
    st.error("⚠️ CẢNH BÁO RỦI RO HỦY PHÒNG CAO! Khuyến nghị yêu cầu xác nhận cọc.")
""")

    # Try to insert streamlit_app_ui.png if created or existing plot
    if os.path.exists("outputs/plots/streamlit_app_ui.png"):
        add_img("outputs/plots/streamlit_app_ui.png", "Hình 4.1: Giao diện Web dự đoán hủy phòng khách sạn xây dựng bằng Streamlit")

    doc.add_page_break()

    # -------------------------------------------------------------
    # KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO
    # -------------------------------------------------------------
    add_title("KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO", level=1)
    
    add_title("1. Kết quả đạt được", level=2)
    add_body_p("• Xây dựng thành công quy trình xử lý dữ liệu chuẩn chỉnh, làm sạch giá trị thiếu và giải quyết vấn đề mất cân bằng nhãn bằng SMOTE.", bold_prefix="")
    add_body_p("• Huấn luyện và đánh giá toàn diện 5 mô hình học máy, xác định Gradient Boosting và Random Forest là các mô hình tối ưu nhất với ROC-AUC > 0.947.", bold_prefix="")
    add_body_p("• Đóng gói thành công ứng dụng Web tương tác Streamlit thân thiện, sẵn sàng đưa vào hỗ trợ thực tế tại khách sạn.", bold_prefix="")

    add_title("2. Hạn chế của đề tài", level=2)
    add_body_p("• Bộ dữ liệu tập trung chủ yếu tại khu vực châu Âu (Bồ Đào Nha), cần thu thập thêm dữ liệu nội địa Việt Nam để nâng cao tính tổng quát hóa.", bold_prefix="")
    add_body_p("• Mô hình Gradient Boosting có chi phí tính toán huấn luyện khá lớn khi kích thước dữ liệu tăng mạnh.", bold_prefix="")

    add_title("3. Hướng phát triển", level=2)
    add_body_p("• Tích hợp ứng dụng qua API với hệ thống quản lý khách sạn (PMS - Property Management System) như Opera, Smile.", bold_prefix="")
    add_body_p("• Áp dụng các kỹ thuật giải thích mô hình tiên tiến như SHAP / LIME để phân tích nguyên nhân hủy phòng chi tiết cho từng khách hàng cụ thể.", bold_prefix="")

    add_title("4. Tài liệu tham khảo", level=2)
    refs = [
        "[1] Antonio, N., de Almeida, A., & Nunes, L. (2019). Hotel booking demand datasets. Data in Brief, 22, 41-49.",
        "[2] Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
        "[3] Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. In Proceedings of KDD '16.",
        "[4] Chawla, N. V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. Journal of Artificial Intelligence Research, 16, 321-357.",
        "[5] Streamlit Documentation - https://docs.streamlit.io/"
    ]
    for r in refs:
        add_body_p(r, space_after=4)

    output_filename = "Bao_Cao_BTL_Hoc_May_Hotel_Booking.docx"
    doc.save(output_filename)
    print(f"Successfully generated report document: {output_filename}")

if __name__ == "__main__":
    main()
