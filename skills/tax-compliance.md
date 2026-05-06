---
name: tax-compliance
version: 1.0.0
description: >
  Skill kiểm tra tuân thủ nghĩa vụ thuế — checklist các nghĩa vụ kê khai, nộp thuế,
  hồ sơ lưu trữ, hóa đơn chứng từ theo quy định. Dùng cho JA-Compliance Bot.
category: compliance
tags: [compliance, tax-filing, invoice, record-keeping, audit-risk, vietnam]
applicable_bots: [ja, sa]
---

# Skill: Tax Compliance — Kiểm tra Tuân thủ Thuế

## Framework Kiểm tra Tuân thủ

Khi thực hiện compliance review, đi qua 6 nhóm kiểm tra sau:

### Nhóm 1: Đăng ký và Thông báo

| Nghĩa vụ | Hạn chót | Kiểm tra |
|----------|----------|---------|
| Đăng ký mã số thuế | Ngay khi thành lập DN | Có MST không? Đúng thông tin? |
| Thông báo thay đổi thông tin | 10 ngày kể từ thay đổi | Địa chỉ, ngành nghề, vốn |
| Đăng ký phương pháp kế toán | Kỳ kế toán đầu tiên | Khấu trừ hay trực tiếp (GTGT) |
| Đăng ký nộp VAT tháng/quý | Khi doanh thu đạt ngưỡng | Đã chuyển từ quý sang tháng chưa? |

### Nhóm 2: Kê khai và Nộp thuế

| Loại thuế | Kỳ kê khai | Hạn nộp tờ khai | Hạn nộp tiền |
|-----------|-----------|-----------------|--------------|
| GTGT tháng | Hàng tháng | Ngày 20 tháng sau | Cùng kỳ |
| GTGT quý | Hàng quý | Ngày 30 tháng đầu quý sau | Cùng kỳ |
| TNDN tạm nộp | Hàng quý | Không phải nộp tờ khai | Ngày 30 tháng đầu quý sau |
| TNDN quyết toán | Năm | Ngày 31/3 năm sau | Cùng ngày |
| TNCN khấu trừ tháng | Hàng tháng (nếu ≥50 triệu) | Ngày 20 tháng sau | Cùng kỳ |
| TNCN khấu trừ quý | Hàng quý (nếu <50 triệu) | Ngày 30 tháng đầu quý sau | Cùng kỳ |
| TNCN quyết toán | Năm | Ngày 30/4 năm sau | Cùng ngày |
| Thuế nhà thầu | Theo từng hợp đồng | 10 ngày kể từ ngày khấu trừ | Cùng ngày |
| LPTB, Môn bài | Năm | 30/1 (đầu năm) | Cùng ngày |

### Nhóm 3: Hóa đơn và Chứng từ

**Hóa đơn điện tử (bắt buộc từ 1/7/2022 theo NĐ 123/2020):**
- [ ] Đã đăng ký hóa đơn điện tử với CQT?
- [ ] Hóa đơn có đủ 7 thông tin bắt buộc? (người bán, người mua, HHDV, số lượng, đơn giá, thành tiền, thuế GTGT)
- [ ] Ký số hợp lệ (chữ ký số còn hiệu lực)?
- [ ] Gửi cho CQT đúng thời hạn (cùng ngày hoặc ngày tiếp theo)?

**Hóa đơn đầu vào:**
- [ ] Tên, địa chỉ, MST người bán đúng?
- [ ] Tên HHDV, số lượng, đơn giá, thành tiền khớp với thực tế?
- [ ] Ngày lập hóa đơn phù hợp với thời điểm giao dịch?
- [ ] Thanh toán qua ngân hàng nếu ≥20 triệu?

### Nhóm 4: Giá chuyển nhượng (nếu có bên liên kết)

- [ ] Xác định có giao dịch với bên liên kết theo NĐ 132/2020?
- [ ] Điền Mẫu số 01/TKQ-TNDN (Phụ lục I NĐ 132)?
- [ ] Tổng giao dịch liên kết >200 tỷ → lập hồ sơ Local File?
- [ ] Tổng doanh thu hợp nhất ≥18.000 tỷ → lập Master File?
- [ ] Tổng chi phí lãi vay (liên kết) ≤30% EBITDA?

### Nhóm 5: Lưu trữ hồ sơ

| Loại hồ sơ | Thời hạn lưu trữ |
|-----------|-----------------|
| Hóa đơn, chứng từ | 10 năm |
| Hồ sơ kế toán | 10 năm |
| Hợp đồng kinh tế | 10 năm |
| Hồ sơ lao động | 10 năm |
| Hồ sơ quyết toán thuế | 10 năm |
| Hồ sơ khiếu nại, tranh chấp | Cho đến khi giải quyết xong |

### Nhóm 6: Chỉ số rủi ro kiểm tra thuế

Các yếu tố tăng nguy cơ bị kiểm tra:
- Doanh thu/lợi nhuận giảm mạnh so với năm trước
- Tỷ lệ thuế TNDN/doanh thu thấp so với ngành
- Nhiều năm liên tục kê khai lỗ
- Giao dịch lớn với bên liên kết nước ngoài
- Hoàn thuế GTGT số tiền lớn
- Chênh lệch lớn giữa doanh thu bán hàng và doanh thu kê khai TNCN

## Mức phạt vi phạm hành chính thuế

| Vi phạm | Mức phạt |
|---------|---------|
| Nộp tờ khai chậm 1–10 ngày | 2 triệu đồng |
| Nộp tờ khai chậm 11–20 ngày | 3 triệu đồng |
| Nộp tờ khai chậm 21–30 ngày | 5 triệu đồng |
| Nộp tờ khai chậm 31–40 ngày | 7 triệu đồng |
| Nộp tờ khai chậm >40 ngày hoặc không nộp | 15 triệu đồng |
| Khai sai dẫn đến thiếu thuế | 20% số thuế khai thiếu |
| Trốn thuế | 1–3 lần số thuế trốn |
| Nộp thuế chậm | 0,03%/ngày × số tiền × số ngày |

## Lưu ý đặc biệt 2024–2025

- **Kiểm tra TMĐT**: TCT tăng cường kiểm tra DN bán hàng qua sàn TMĐT (Shopee, TikTok Shop...) — xác nhận khai đúng doanh thu
- **Hóa đơn điện tử có mã**: cơ sở kinh doanh nhỏ bắt buộc dùng HĐ có mã CQT cấp
- **Hệ thống eTax Mobile**: cá nhân kinh doanh có thể bị cơ quan thuế xác định thu nhập qua dữ liệu ngân hàng
- **Thông tư 80/2021/TT-BTC**: quy định mới về khai thuế tập trung cho DN có nhiều chi nhánh, đơn vị phụ thuộc

## Template Báo cáo Compliance Review

Khi hoàn thành compliance check, tổng hợp theo format:

```
BÁO CÁO KIỂM TRA TUÂN THỦ THUẾ
Đơn vị: [Tên DN]
Kỳ kiểm tra: [năm/giai đoạn]
Ngày: [DD/MM/YYYY]

I. TÓM TẮT KẾT QUẢ
   - Tổng số mục kiểm tra: X
   - Tuân thủ: Y / Cần cải thiện: Z / Rủi ro cao: W

II. CÁC VẤN ĐỀ PHÁT HIỆN (ưu tiên theo mức độ nghiêm trọng)
   1. [VẤN ĐỀ] — [MỨC ĐỘ: CAO/TRUNG BÌNH/THẤP]
      - Mô tả: ...
      - Căn cứ pháp lý: ...
      - Rủi ro: ... (số tiền, loại vi phạm)
      - Khuyến nghị: ...

III. HÀNH ĐỘNG ƯU TIÊN
   Ngay lập tức (trong 7 ngày): ...
   Ngắn hạn (trong 30 ngày): ...
   Dài hạn: ...
```
