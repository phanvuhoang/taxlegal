---
name: vietnam-vat
version: 1.0.0
description: >
  Skill chuyên sâu về Thuế Giá trị gia tăng (GTGT/VAT) Việt Nam.
  Bao gồm đối tượng chịu thuế, không chịu thuế, khấu trừ, hoàn thuế, VAT nhà thầu.
  Dùng cho Partner Bot và JA Bot khi phân tích vấn đề VAT.
category: tax
tags: [vat, gtgt, invoice, input-tax, zero-rate, vietnam]
applicable_bots: [partner, ja, sa]
---

# Skill: Thuế Giá trị gia tăng (VAT) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Ghi chú |
|---------|---------|---------|
| Luật GTGT (mới nhất) | **48/2024/QH15** | Hiệu lực **01/07/2025** — thay thế Luật 13/2008 |
| NĐ hướng dẫn | 209/2013/NĐ-CP (sửa 12/2015, 49/2022) | Đang hiệu lực đến 30/6/2025 |
| TT hướng dẫn | 219/2013/TT-BTC (sửa nhiều lần) | Hướng dẫn chính |
| Giảm thuế GTGT | NĐ 70/2025/NĐ-CP | Giảm 2% → 8% đến 30/6/2026 |

**⚠️ Lưu ý quan trọng:** Luật GTGT 48/2024/QH15 có hiệu lực từ 01/07/2025. Cần xác nhận văn bản áp dụng dựa trên thời điểm giao dịch.

## Thuế suất GTGT

| Mức thuế suất | Áp dụng cho |
|--------------|-------------|
| **0%** | Hàng hóa/DV xuất khẩu; vận tải quốc tế; dịch vụ cung cấp cho tổ chức/cá nhân nước ngoài (điều kiện cụ thể); một số DV tại khu phi thuế quan |
| **5%** | Sản phẩm trồng trọt, chăn nuôi chưa chế biến; nước sạch; phân bón; sách giáo khoa; thuốc chữa bệnh; trang thiết bị y tế; dịch vụ khoa học công nghệ; nhà ở xã hội |
| **8%** | Hàng hóa/DV trong danh mục giảm thuế theo NĐ 70/2025 (đến 30/6/2026) |
| **10%** | Tất cả hàng hóa/DV còn lại không thuộc diện không chịu thuế hoặc thuế suất 0%/5% |

## Đối tượng KHÔNG chịu thuế GTGT (26 nhóm)

Các nhóm thường gặp trong tư vấn doanh nghiệp:
- Dịch vụ tín dụng, cho vay, bảo lãnh (trừ DV tư vấn tài chính)
- Kinh doanh chứng khoán, quỹ đầu tư
- Chuyển nhượng vốn, chuyển nhượng dự án đầu tư
- Bảo hiểm nhân thọ, sức khỏe, nông nghiệp
- Dịch vụ y tế, thú y (khám chữa bệnh)
- Dạy học, dạy nghề
- In ấn, xuất bản báo, tạp chí, sách thuộc Nhà nước
- Vũ khí, khí tài quốc phòng

## Điều kiện khấu trừ thuế đầu vào

**4 điều kiện đồng thời (Điều 15 TT219/2013 + Điều 12 Luật 48/2024):**

1. **Hóa đơn GTGT hợp pháp** — có đầy đủ thông tin bắt buộc
2. **Có chứng từ thanh toán không dùng tiền mặt** (≥ 20 triệu đồng/lần) — trừ hàng hóa nhập khẩu
3. **Hàng hóa/DV phục vụ SXKD hàng chịu thuế GTGT** — bao gồm SXKD chịu 0%, 5%, 10%
4. **Kê khai đúng kỳ** — kê khai trong kỳ phát sinh hoặc chậm nhất kỳ khai thuế liền kề tiếp theo

**Lưu ý đặc biệt:**
- Hàng hóa/DV phục vụ đồng thời chịu thuế và không chịu thuế: phân bổ theo doanh thu hoặc hướng dẫn riêng
- Tài sản đặc biệt (xe ô tô ≤9 chỗ không dùng kinh doanh vận tải): chỉ khấu trừ phần tương ứng doanh thu chịu thuế

## VAT 0% — Điều kiện

Để được áp dụng thuế suất 0%:
1. **Có hợp đồng xuất khẩu** (hoặc uỷ thác xuất khẩu)
2. **Có chứng từ thanh toán qua ngân hàng** bằng ngoại tệ (hoặc hình thức được chấp nhận)
3. **Có tờ khai hải quan** (đối với xuất khẩu hàng hóa)
4. **Hóa đơn GTGT** (0%) hoặc hóa đơn thương mại

**Dịch vụ xuất khẩu 0%:**
- Cung cấp cho tổ chức, cá nhân nước ngoài
- Sử dụng ngoài VN
- Thanh toán qua ngân hàng bằng ngoại tệ
- **Không bao gồm**: DV sửa chữa phương tiện, máy móc trong VN; DV xây dựng lắp đặt công trình ở nước ngoài (lại là 0%); nhà hàng, khách sạn, vui chơi giải trí tại VN

## Hoàn thuế GTGT

| Trường hợp | Điều kiện | Thời hạn giải quyết |
|-----------|-----------|---------------------|
| Xuất khẩu hàng hóa/DV | Số thuế đầu vào chưa khấu trừ hết ≥300 triệu | 6 ngày làm việc (kiểm tra trước, hoàn sau) hoặc 40 ngày (kiểm tra trước) |
| Dự án đầu tư | Giai đoạn đầu tư, chưa đi vào SXKD, số thuế chưa khấu trừ ≥300 triệu | 40 ngày |
| Chuyển đổi sở hữu, giải thể | Số thuế đầu vào chưa khấu trừ hết | 40 ngày |
| DN 3 năm liên tục SXKD xuất khẩu | Được hoàn hàng tháng/quý | Ưu tiên hoàn trước kiểm sau |

## VAT nhà thầu nước ngoài (FCT-VAT)

Khi DN VN trả tiền cho nhà thầu nước ngoài cung cấp DV tại VN:
- DN VN (bên thuê) **khấu trừ và nộp thay** VAT nhà thầu theo TT103/2014/TT-BTC
- Thuế suất thường là **5% hoặc 10%** tùy loại DV
- DN VN được khấu trừ số VAT đã nộp thay nếu đủ điều kiện

## Kê khai VAT

| Hình thức | Điều kiện | Kỳ kê khai |
|-----------|-----------|------------|
| Kê khai tháng | Doanh thu năm trước >50 tỷ | Hạn ngày 20 tháng sau |
| Kê khai quý | Doanh thu năm trước ≤50 tỷ | Hạn ngày 30 tháng đầu quý sau |
| SXKD mới | Tất cả | Quý cho đến khi đủ điều kiện tháng |

## Checklist VAT thực hành

- [ ] Xác định đúng thuế suất (0/5/8/10% hoặc không chịu thuế)
- [ ] Kiểm tra điều kiện khấu trừ: hóa đơn, chứng từ TT không tiền mặt, mục đích kinh doanh
- [ ] Hàng bán 0%: đủ 3 điều kiện (HĐ, thanh toán qua NH, tờ khai HQ)?
- [ ] Có hoạt động vừa chịu thuế vừa không chịu? → phân bổ đúng
- [ ] Kỳ kê khai: tháng hay quý?
- [ ] Có phát sinh VAT nhà thầu nước ngoài không?
