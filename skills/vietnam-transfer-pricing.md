---
name: vietnam-transfer-pricing
version: 1.0.0
description: >
  Vietnam Transfer Pricing — Decree 132/2020, arm's length principle, TP methods,
  documentation requirements (local file/master file/CbCR), APA, and conservative defaults.
category: tax
tags: [transfer-pricing, gia-chuyen-nhuong, decree-132, arm-length, apa, giao-dich-lien-ket, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Giá chuyển nhượng (Transfer Pricing) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Nghị định TP hiện hành | 132/2020/NĐ-CP | Quy định chính (thay NĐ20/2017) |
| Thông tư hướng dẫn | 45/2021/TT-BTC | Hướng dẫn NĐ132 |
| NĐ cũ (tham chiếu) | 20/2017/NĐ-CP (sửa 68/2020) | Đã thay thế bởi NĐ132 |
| Thông tư cũ (tham chiếu) | 41/2017/TT-BTC | Đã thay thế bởi TT45/2021 |
| BEPS Action 13 | OECD 2015 | Tiêu chuẩn quốc tế — VN áp dụng |

## Định nghĩa Giao dịch Liên kết

**Theo Điều 5, NĐ 132/2020** — Hai bên có quan hệ liên kết khi:

| Tiêu chí | Ngưỡng |
|---------|-------|
| Sở hữu vốn trực tiếp/gián tiếp | **≥ 25%** |
| Cho vay / bảo lãnh vốn | ≥ 25% vốn góp |
| Kiểm soát Hội đồng quản trị | ≥ 1/3 thành viên HĐQT |
| Tổng giám đốc/Giám đốc chung | Cùng người điều hành |
| Tham gia chương trình hợp tác kinh doanh | Được xem là liên kết theo thỏa thuận |
| Giao dịch với bên tại thiên đường thuế | Tự động coi là liên kết nếu giao dịch qua jurisdictions không minh bạch |

## Nguyên tắc Giá thị trường (Arm's Length Principle)

**Định nghĩa**: Giao dịch giữa các bên liên kết phải được thực hiện theo điều kiện và giá cả như giữa các bên độc lập trong điều kiện tương đương.

**Quy trình phân tích arm's length:**
1. **Phân tích chức năng, tài sản, rủi ro (FAR)**: Xác định vai trò của từng bên
2. **Phân tích có thể so sánh (Comparables)**: Tìm giao dịch/doanh nghiệp có thể so sánh
3. **Chọn phương pháp TP phù hợp**
4. **Tính khoảng arm's length (IQR)**
5. **So sánh và điều chỉnh nếu cần**

## 5 Phương pháp Giá chuyển nhượng

| Phương pháp | Tên tiếng Anh | Ưu tiên áp dụng |
|------------|--------------|----------------|
| **CUP** | Comparable Uncontrolled Price | Ưu tiên 1 — khi có giao dịch so sánh được trực tiếp |
| **RPM** | Resale Price Method | Cho nhà phân phối/bán lại không gia tăng giá trị đáng kể |
| **CPM** | Cost Plus Method | Cho nhà sản xuất/cung cấp dịch vụ đơn giản |
| **TNMM** | Transactional Net Margin Method | Phổ biến nhất trong thực tế VN |
| **PSM** | Profit Split Method | Giao dịch phức tạp, tài sản vô hình độc đáo |

**Thực tế**: TNMM chiếm đa số trong hồ sơ TP Việt Nam vì dễ tìm comparables nhất.

## Khoảng Giá thị trường — IQR (Interquartile Range)

**Theo Điều 17, NĐ 132/2020:**

- Tính **khoảng tứ phân vị (IQR)** từ tập dữ liệu so sánh độc lập
- **P25 (Q1)** → Giới hạn dưới của khoảng arm's length
- **P75 (Q3)** → Giới hạn trên của khoảng arm's length
- Nếu chỉ tiêu tài chính của giao dịch liên kết nằm trong khoảng [P25; P75] → được chấp nhận
- Nếu nằm ngoài khoảng → CQT điều chỉnh về trung vị (**P50**)

**Nguồn dữ liệu so sánh được chấp nhận**: Bureau van Dijk (Orbis), Bloomberg, Compustat, dữ liệu nội bộ đã công bố.

## Yêu cầu Tài liệu Giá chuyển nhượng

### Cấu trúc 3 cấp (theo BEPS Action 13)

| Cấp | Tên | Nội dung | Đối tượng bắt buộc |
|-----|-----|---------|-------------------|
| **1** | Local File (Hồ sơ địa phương) | Thông tin DN tại VN, giao dịch liên kết, phân tích TP | Tất cả DN có giao dịch liên kết |
| **2** | Master File (Hồ sơ tập đoàn) | Cấu trúc tập đoàn, chính sách TP toàn cầu, tài sản vô hình | DN có công ty mẹ nước ngoài, doanh thu tập đoàn ≥ VND 18,000 tỷ |
| **3** | CbCR (Country-by-Country Report) | Phân bổ lợi nhuận, thuế theo từng quốc gia | Tập đoàn toàn cầu doanh thu ≥ EUR 750 triệu (VND 18,000 tỷ) |

### Mẫu kê khai giao dịch liên kết

| Mẫu | Nội dung | Nộp cùng |
|-----|---------|---------|
| **Phụ lục I/TNDN** (Mẫu 01) | Danh sách giao dịch liên kết | Tờ khai CIT năm |
| **Phụ lục II/TNDN** (Mẫu 02) | Thông tin CbCR (nếu áp dụng) | Tờ khai CIT năm |

## Thời hạn lập tài liệu

**Nguyên tắc đồng thời (Contemporaneous)**:
- Tài liệu TP phải được hoàn thành **trước ngày nộp tờ khai CIT** (tức là trước 31/03 năm sau)
- Không được lập tài liệu hồi tố sau khi CQT thanh tra
- CQT có quyền yêu cầu xuất trình tài liệu trong vòng **15 ngày làm việc** kể từ khi yêu cầu

## Safe Harbor (Trường hợp được miễn lập hồ sơ)

**Theo Điều 19, NĐ 132/2020** — DN được miễn lập Local File/Master File nếu:

| Điều kiện | Ngưỡng |
|----------|-------|
| Doanh thu < | VND 50 tỷ AND tổng giá trị giao dịch liên kết < VND 30 tỷ |
| Đã ký APA | Và đang thực hiện đúng APA |
| Chỉ giao dịch nội địa | Các bên đều chịu cùng mức thuế CIT tại VN, không được ưu đãi khác nhau |

**Chú ý**: Miễn lập hồ sơ ≠ miễn khai Mẫu 01/TNDN — vẫn phải khai phụ lục giao dịch liên kết.

## Thỏa thuận Định giá trước (APA — Advance Pricing Agreement)

**Theo Điều 41–48, NĐ 132/2020:**

| Loại APA | Nội dung |
|---------|---------|
| **Unilateral APA** | Thỏa thuận giữa DN và TCT VN |
| **Bilateral APA** | Thỏa thuận giữa TCT VN và CQT nước đối tác (qua MAP) |
| **Multilateral APA** | Nhiều nước tham gia (hiếm) |

**Lợi ích APA**: Xác định phương pháp và khoảng giá chấp nhận trước → an toàn pháp lý trong thời hạn APA (3–5 năm, có thể gia hạn).

**Hạn chế APA**: Chi phí cao, thời gian đàm phán dài (thường 1–3 năm), không phù hợp DN nhỏ.

## Quy tắc Thin Capitalisation (Giới hạn lãi vay liên kết)

**Theo Điều 16, NĐ 132/2020:**
- Chi phí lãi vay ròng (sau khi trừ lãi tiền gửi, cho vay) **không được vượt 30% EBITDA**
- Phần vượt được chuyển sang tối đa **5 năm** tiếp theo
- Không áp dụng cho: ngân hàng, tổ chức tín dụng, bảo hiểm, các khoản vay ODA nhà nước

## Nguyên tắc mặc định thận trọng (Conservative Defaults)

| Tình huống | Mặc định |
|-----------|---------|
| Không chắc có đáp ứng safe harbor | Lập đầy đủ Local File để an toàn |
| Chưa tìm được comparables đủ mạnh | Ghi nhận rủi ro, không đưa ra vị trí TP mà không có cơ sở |
| Lãi vay liên kết gần 30% EBITDA | Lập tính toán chính xác, không dựa vào ước tính |
| Nghi ngờ giao dịch vi phạm arm's length | Đề xuất điều chỉnh chủ động trước khi CQT phát hiện |
| Tài liệu lập sau ngày nộp tờ khai | Không sử dụng — tài liệu hồi tố không có giá trị |

## Checklist Transfer Pricing

- [ ] Xác định tất cả bên liên kết theo tiêu chí NĐ132 (≥25% ownership)
- [ ] Liệt kê toàn bộ giao dịch liên kết và giá trị trong năm
- [ ] Kiểm tra có đáp ứng safe harbor không
- [ ] Chọn phương pháp TP phù hợp (ưu tiên CUP, thực tế thường TNMM)
- [ ] Tìm và lọc comparables từ cơ sở dữ liệu tin cậy
- [ ] Tính IQR và xác định khoảng arm's length
- [ ] Hoàn thành Local File trước ngày 31/03
- [ ] Điền Phụ lục 01/TNDN khi nộp CIT quyết toán
- [ ] Kiểm tra chi phí lãi vay liên kết ≤ 30% EBITDA
- [ ] Xem xét nộp APA nếu giao dịch liên kết lớn và thường xuyên
