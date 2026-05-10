---
name: vat-export-zero-rate
version: 1.0.0
description: >
  Skill về thuế GTGT suất 0% cho xuất khẩu hàng hóa và dịch vụ tại Việt Nam. Điều kiện
  áp dụng 0%, bằng chứng xuất khẩu cần có, xử lý hoàn thuế GTGT đầu vào, và các trường
  hợp dễ nhầm (dịch vụ tiêu dùng trong nước nhưng cho khách nước ngoài trả tiền).
category: tax
tags: [vat, gtgt, export, xuat-khau, zero-rate, suat-0, refund, hoan-thue, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: GTGT Suất 0% — Xuất Khẩu

> **Căn cứ:** Luật Thuế GTGT Điều 8, TT 219/2013/TT-BTC Điều 9

---

## Phần 1 — Hàng Hóa Xuất Khẩu (0%)

### Điều kiện áp dụng 0% cho hàng hóa

| Điều kiện | Bằng chứng cần có |
|-----------|------------------|
| Hàng thực tế xuất khẩu qua cửa khẩu | **Tờ khai hải quan** (tờ khai xuất khẩu đã thông quan) |
| Thanh toán bằng ngoại tệ hoặc thanh toán qua ngân hàng | Xác nhận thanh toán ngân hàng (SWIFT, bank statement) |
| Hợp đồng mua bán quốc tế | Hợp đồng ký với đối tác nước ngoài |
| Hóa đơn thương mại (commercial invoice) | Invoice ghi rõ buyer nước ngoài |

> **Conservative default:** Nếu không có tờ khai hải quan đã thông quan → **10% domestic rate**.

### Bằng chứng tối thiểu cho 0% hàng hóa

```
PHẢI CÓ:
✅ Tờ khai hải quan xuất khẩu đã được hải quan xác nhận thông quan
✅ Xác nhận thanh toán qua ngân hàng (FX receipt)
✅ Hợp đồng với bên mua nước ngoài

KHUYẾN NGHỊ CÓ THÊM:
→ Bill of lading / Airway bill (vận đơn)
→ Packing list
→ Certificate of origin (C/O) nếu cần ưu đãi FTA
```

---

## Phần 2 — Dịch Vụ Xuất Khẩu (0%)

Dịch vụ được hưởng 0% nếu **đồng thời** đáp ứng **4 điều kiện:**

| # | Điều kiện |
|---|-----------|
| 1 | Cung cấp cho đối tác là **tổ chức/cá nhân nước ngoài** |
| 2 | Dịch vụ được **tiêu thụ ngoài lãnh thổ Việt Nam** |
| 3 | Thanh toán bằng **ngoại tệ** qua ngân hàng |
| 4 | Dịch vụ **không thực hiện tại Việt Nam** (cho một số loại DV) |

> **Conservative default (R-VN Q6.2):** Nếu không xác nhận được 4 điều kiện → **10% domestic rate**.

### Bảng phân loại dịch vụ phổ biến

| Dịch vụ | 0% hay 10%? | Điều kiện then chốt |
|---------|------------|---------------------|
| IT consulting/phần mềm cho khách nước ngoài | 0% nếu đủ 4 ĐK | Thanh toán USD; công ty nước ngoài; tiêu thụ ngoài VN |
| Thiết kế đồ họa cho khách nước ngoài | 0% nếu đủ 4 ĐK | Như trên |
| Dịch thuật văn bản gửi cho công ty nước ngoài | 0% nếu đủ 4 ĐK | Như trên |
| Tư vấn pháp lý cho khách nước ngoài về pháp luật nước ngoài | 0% nếu đủ 4 ĐK | DV tiêu thụ ngoài VN |
| Du lịch, khách sạn cho khách nước ngoài đến VN | **10%** | DV thực hiện TẠI VN = không đủ ĐK 4 |
| Dịch thuật/phiên dịch tại VN cho khách nước ngoài | **10%** | Thực hiện TẠI VN |
| Quảng cáo trực tuyến (DV cung cấp cho công ty nước ngoài nhưng nhắm đến VN) | **Tier 2 — hỏi thêm** | Không rõ ràng |

---

## Phần 3 — Vận Tải Quốc Tế (0%)

| Loại | Xử lý |
|------|-------|
| Vận tải quốc tế (hàng, người) từ VN ra nước ngoài | 0% (cả đoạn VN → biên giới/cảng) |
| Vận tải nội địa (VN → VN, dù đặt qua công ty nước ngoài) | 10% |
| Dịch vụ hỗ trợ vận tải quốc tế (xếp dỡ, lưu kho tại cảng quốc tế) | Tier 2 — kiểm tra chi tiết |

---

## Phần 4 — Hoàn Thuế GTGT Đầu Vào Cho Xuất Khẩu

### Khi nào được hoàn?

Doanh nghiệp xuất khẩu có thể **hoàn thuế GTGT đầu vào** nếu:
- Doanh thu xuất khẩu ≥ 50% tổng doanh thu **trong 12 tháng liên tục**
- Số thuế GTGT đầu vào chưa được khấu trừ hết (số dư âm liên tục ≥ 3 tháng/quý)

### Quy trình hoàn thuế cơ bản

```
1. Kê khai đầy đủ trên Form 01/GTGT: đầu ra 0% + đầu vào liên quan
2. Xác định số thuế đầu vào chưa khấu trừ (Line [41])
3. Lập hồ sơ hoàn thuế nộp cho Cục Thuế:
   - Bảng kê hóa đơn đầu vào liên quan xuất khẩu
   - Bảng kê tờ khai hải quan
   - Xác nhận thanh toán qua ngân hàng
4. Cục Thuế kiểm tra (hoàn trước kiểm sau hoặc kiểm tra trước)
5. Nhận tiền hoàn thuế
```

### Thời hạn xử lý hoàn thuế

| Loại | Thời gian |
|------|---------|
| Hoàn trước kiểm sau (doanh nghiệp tuân thủ tốt) | 6 ngày làm việc |
| Kiểm tra trước hoàn sau | 40 ngày làm việc |

---

## Phần 5 — Kiểm Tra Trước Khi Áp Dụng 0%

### Checklist 0% cho dịch vụ

- [ ] Đối tác là tổ chức/cá nhân nước ngoài? (kiểm tra hợp đồng, hóa đơn thương mại)
- [ ] Dịch vụ tiêu thụ ngoài lãnh thổ VN? (không phải thực hiện tại VN cho người tiêu dùng tại VN)
- [ ] Thanh toán bằng ngoại tệ qua ngân hàng? (có SWIFT/bank statement xác nhận)
- [ ] Hợp đồng bằng văn bản với đối tác nước ngoài?
- [ ] Hóa đơn GTGT phát hành đúng, ghi rõ "thuế suất 0%"?

### Checklist 0% cho hàng hóa

- [ ] Tờ khai hải quan xuất khẩu đã thông quan (có xác nhận của hải quan)?
- [ ] Thanh toán qua ngân hàng nhận bằng ngoại tệ?
- [ ] Hợp đồng xuất khẩu ký với người mua nước ngoài?
- [ ] Hóa đơn thương mại (commercial invoice) phù hợp?

> **Nguyên tắc:** Thiếu bất kỳ yếu tố nào → **10% default**. Chỉ áp dụng 0% khi có đủ bằng chứng hoàn chỉnh.
