---
name: advisory-memo
version: 1.0.0
description: >
  Skill viết advisory memo tư vấn thuế chuyên nghiệp — cấu trúc, ngôn ngữ, định dạng và tiêu chuẩn
  chất lượng cho một văn bản tư vấn thuế theo tiêu chuẩn hãng tư vấn hàng đầu.
  Dùng cho JA Bot (Advisory variant) và Partner Bot.
category: advisory
tags: [memo, advisory, writing, quality, structure]
applicable_bots: [ja, partner]
---

# Skill: Viết Advisory Memo Tư vấn Thuế

## Cấu trúc chuẩn của Advisory Memo thuế

Một advisory memo thuế chuyên nghiệp gồm các phần theo thứ tự:

### 1. TIÊU ĐỀ VÀ THÔNG TIN CƠ BẢN
```
ĐỀ: TƯ VẤN THUẾ — [Chủ đề chính]
KÍNH GỬI: [Tên khách hàng/Công ty]
NGÀY: [DD/MM/YYYY]
THAM CHIẾU: [Mã hồ sơ]
BÍ MẬT: Tư liệu này chỉ dành cho khách hàng được đề cập
```

### 2. TÓM TẮT ĐIỀU HÀNH (Executive Summary)
- Tối đa 200–300 từ
- Nêu rõ: (1) Vấn đề cần tư vấn, (2) Kết luận chính, (3) Khuyến nghị hành động ngay
- Dành cho người ra quyết định đọc nhanh — không cần đọc toàn bộ memo

### 3. SỰ KIỆN (Facts)
- Liệt kê sự kiện quan trọng đã được xác nhận
- Phân biệt: Sự kiện khách hàng cung cấp (CLIENT-STATED) vs. Đã xác minh (VERIFIED)
- Không phân tích ở phần này — chỉ trình bày sự kiện

### 4. VẤN ĐỀ CẦN TƯ VẤN (Issues)
- Liệt kê từng câu hỏi pháp lý cụ thể (đánh số)
- Ví dụ:
  - "1. Khoản thanh toán X có phải chịu thuế GTGT không?"
  - "2. Chi phí Y có được trừ khi tính thuế TNDN không?"

### 5. PHÂN TÍCH PHÁP LÝ (Analysis)
Với mỗi vấn đề:
- **Căn cứ pháp lý**: trích dẫn cụ thể (Điều X, Khoản Y, văn bản số Z)
- **Phân tích**: áp dụng quy định vào sự kiện cụ thể
- **Thực tiễn**: kinh nghiệm xử lý, thông lệ, án lệ (nếu có)
- **Rủi ro**: xác định và định lượng rủi ro thuế

### 6. KẾT LUẬN VÀ KHUYẾN NGHỊ (Conclusions & Recommendations)
- Kết luận rõ ràng cho từng vấn đề (đánh số theo Issues)
- Khuyến nghị hành động cụ thể với timeline
- Phân biệt: hành động cần làm ngay vs. trung hạn vs. dài hạn

### 7. CÁC LƯU Ý VÀ ĐIỀU KIỆN (Caveats)
- Giới hạn của tư vấn (chỉ dựa trên thông tin đã cung cấp)
- Disclaimer bắt buộc về thuế
- Yêu cầu xác nhận với cơ quan thuế/chuyên gia khác nếu cần

## Tiêu chuẩn ngôn ngữ và văn phong

### Ngôn ngữ
- **Tiếng Việt chuyên nghiệp** — không dùng từ thông tục
- Thuật ngữ pháp lý chính xác (theo Luật, không dịch tự do)
- Câu văn rõ ràng, tránh câu quá dài (>50 từ/câu)

### Văn phong tư vấn
- Tư vấn phải **kết luận rõ ràng** — tránh "có thể", "có thể là" khi đã có đủ căn cứ
- Khi bất định: nêu rõ mức độ bất định và lý do
- Không sử dụng "chúng tôi nghĩ rằng" khi có văn bản pháp luật cụ thể → dùng "Theo Điều X, văn bản Y..."

### Trích dẫn pháp lý
- Luôn trích dẫn đầy đủ: số văn bản, điều, khoản, điểm
- Ví dụ đúng: "Theo Điều 9, Khoản 2, Điểm b, Thông tư 78/2014/TT-BTC (sửa đổi bởi Thông tư 96/2015/TT-BTC)..."
- Kiểm tra hiệu lực: văn bản đã bị thay thế hay chưa?

## Độ sâu phân tích

### Markers bắt buộc cho Advisory Memo chất lượng cao
- `[PRACTICAL]` — Ít nhất 2 ví dụ thực tế hoặc case study
- `[PITFALL]` — Ít nhất 1 bẫy phổ biến liên quan
- `[COUNTER]` — Phân tích lập trường đối nghịch (cơ quan thuế có thể lập luận gì?)
- `[ANTICIPATE]` — Dự đoán câu hỏi tiếp theo của khách hàng

### Word count tối thiểu
- Vấn đề STANDARD: ≥800 từ/vấn đề
- Vấn đề DEEP: ≥1.500 từ/vấn đề
- Tổng memo ≥ word_count_floor được xác định bởi Intake Enhancer

## Anti-patterns — Tránh tuyệt đối

| Anti-pattern | Vấn đề | Thay bằng |
|--------------|--------|-----------|
| "Theo quy định hiện hành..." | Không trích dẫn cụ thể | Luôn nêu tên văn bản + điều khoản |
| "Khách hàng nên tham khảo thêm" | Né tránh kết luận | Đưa ra quan điểm rõ ràng |
| Tóm tắt quá ngắn | Thiếu căn cứ | Phân tích đầy đủ từng vấn đề |
| Chỉ nêu quy định, không áp dụng | Không đủ giá trị tư vấn | Áp dụng vào sự kiện cụ thể |
| Không đề cập rủi ro | Thiếu tư duy phòng thủ | Luôn có phần "Rủi ro và biện pháp" |
| Dùng thuật ngữ nước ngoài không giải thích | Khó hiểu | Giải thích lần đầu dùng |

## Template Disclaimer bắt buộc

> Tư vấn này được cung cấp dựa trên thông tin và tài liệu do Khách hàng cung cấp, cũng như các văn bản pháp luật hiện hành tại thời điểm phát hành. Tư vấn có thể thay đổi khi có quy định pháp luật mới hoặc khi có thêm thông tin từ phía Khách hàng. Tư vấn này không thay thế cho ý kiến pháp lý chính thức và Khách hàng nên xác nhận với cơ quan thuế có thẩm quyền trước khi thực hiện.
