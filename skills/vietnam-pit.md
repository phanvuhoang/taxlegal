---
name: vietnam-pit
version: 1.0.0
description: >
  Skill chuyên sâu về Thuế Thu nhập cá nhân (TNCN/PIT) Việt Nam.
  Bao gồm thu nhập chịu thuế, biểu thuế, các khoản miễn, giảm trừ gia cảnh, quyết toán.
  Dùng cho JA Bot và Partner Bot khi phân tích vấn đề PIT.
category: tax
tags: [pit, tncn, personal-income-tax, salary, freelance, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế Thu nhập Cá nhân (PIT) — Việt Nam

## Khung pháp lý

| Văn bản | Số hiệu |
|---------|---------|
| Luật TNCN | 04/2007/QH12 (sửa 26/2012, 71/2014) |
| Nghị định | 65/2013/NĐ-CP (sửa 91/2014, 12/2015) |
| Thông tư | 111/2013/TT-BTC (sửa 92/2015, 25/2018) |
| Giảm trừ gia cảnh | NQ 954/2020/UBTVQH14: bản thân 11 triệu/tháng, phụ thuộc 4,4 triệu/tháng |

## Đối tượng nộp thuế

- **Cá nhân cư trú**: thu nhập trong và ngoài VN → chịu thuế toàn cầu
- **Cá nhân không cư trú**: chỉ thu nhập phát sinh tại VN → thuế suất 20% flat

**Cá nhân cư trú**: hiện diện ≥183 ngày/năm dương lịch HOẶC ≥183 ngày trong 12 tháng liên tục kể từ ngày đến VN, HOẶC có nơi ở thường xuyên tại VN.

## 10 Loại thu nhập chịu thuế

1. Thu nhập từ kinh doanh
2. **Thu nhập từ tiền lương, tiền công** ← phổ biến nhất
3. Thu nhập từ đầu tư vốn (cổ tức, lãi)
4. Thu nhập từ chuyển nhượng vốn
5. Thu nhập từ chuyển nhượng BĐS
6. Thu nhập từ trúng thưởng
7. Thu nhập từ bản quyền
8. Thu nhập từ nhượng quyền thương mại
9. Thu nhập từ thừa kế
10. Thu nhập từ quà tặng

## Biểu thuế lũy tiến (Thu nhập từ lương)

| Bậc | Thu nhập tính thuế/tháng | Thuế suất |
|-----|--------------------------|-----------|
| 1 | Đến 5 triệu | 5% |
| 2 | Trên 5 – 10 triệu | 10% |
| 3 | Trên 10 – 18 triệu | 15% |
| 4 | Trên 18 – 32 triệu | 20% |
| 5 | Trên 32 – 52 triệu | 25% |
| 6 | Trên 52 – 80 triệu | 30% |
| 7 | Trên 80 triệu | 35% |

**Thu nhập tính thuế = Thu nhập chịu thuế - Giảm trừ gia cảnh - Bảo hiểm bắt buộc - Từ thiện**

## Các khoản giảm trừ

| Khoản | Mức |
|-------|-----|
| Bản thân | 11 triệu/tháng (132 triệu/năm) |
| Người phụ thuộc | 4,4 triệu/người/tháng |
| BHXH bắt buộc | 8% lương; BHYT 1,5%; BHTN 1% |
| Đóng góp quỹ hưu trí tự nguyện | ≤1 triệu/tháng |
| Đóng góp từ thiện (quỹ nhân đạo Nhà nước) | Toàn bộ số tiền đóng |

## Các khoản KHÔNG chịu thuế (tiêu biểu)

- Phụ cấp độc hại, nguy hiểm (đúng quy định)
- Phụ cấp điện thoại, trang phục (đúng định mức)
- Tiền ăn giữa ca ≤ 730.000đ/tháng
- Vé máy bay về phép (1 lần/năm với người nước ngoài, người VN làm việc nước ngoài)
- Thu nhập từ làm thêm ngoài giờ phần vượt lương giờ thường (≤300%)
- Tiền phụ cấp nhà ở do người sử dụng lao động trả ≤ 15% thu nhập chịu thuế (mới 2020)
- Thưởng nhân ngày lễ tết theo quy chế (giới hạn)

## Thuế TNCN từ cổ tức, chuyển nhượng vốn

| Loại thu nhập | Thuế suất |
|--------------|-----------|
| Cổ tức nhận bằng tiền | 5% flat |
| Lãi tiền gửi, lãi cho vay | 5% flat |
| Chuyển nhượng vốn (cty) | 20% thu nhập ròng HOẶC 0,1% doanh thu (nếu không xác định được giá vốn) |
| Chuyển nhượng chứng khoán | 0,1% giá bán (mỗi lần giao dịch) |
| Chuyển nhượng BĐS | 2% giá bán |

## Quyết toán TNCN

**Ai phải quyết toán:** Cá nhân có thu nhập từ tiền lương, tiền công phải QT nếu:
- Có số thuế phải nộp thêm sau khi tổng hợp
- Muốn hoàn thuế
- Có thu nhập từ 2 nơi trở lên trong năm (trừ trường hợp chỉ 1 nơi trả và đã khấu trừ đúng)

**Hạn quyết toán:** Ngày cuối tháng 4 năm sau (30/4)

**Ủy quyền QT:** Cá nhân có thu nhập từ 1 nơi, không có thu nhập khác hoặc thu nhập khác ≤10 triệu/năm có thể ủy quyền cho tổ chức chi trả QT thay.

## Người nước ngoài làm việc tại VN

- **Cư trú (≥183 ngày)**: chịu thuế lũy tiến như người VN, giảm trừ gia cảnh đủ điều kiện
- **Không cư trú (<183 ngày)**: 20% flat trên tổng thu nhập phát sinh tại VN
- **Expatriate package**: phụ cấp nhà ở, tiền học phí con (hợp đồng ghi rõ), 1 vé máy bay/năm — không tính vào thu nhập chịu thuế

## Checklist PIT

- [ ] Xác định tình trạng cư trú (≥183 ngày?)
- [ ] Liệt kê tất cả loại thu nhập
- [ ] Xác định người phụ thuộc đủ điều kiện
- [ ] Kiểm tra các khoản không chịu thuế (phụ cấp, trợ cấp)
- [ ] Tính thuế từng loại thu nhập riêng (lương, vốn, BĐS)
- [ ] Quyết toán: cá nhân có ủy quyền không hay tự QT?
