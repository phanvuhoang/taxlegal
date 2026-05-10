---
name: vietnam-sst-advanced
version: 1.1.0
description: "Thuế Tiêu thụ đặc biệt (TTĐB/SST) — phân loại hàng hóa, biểu thuế suất, tính thuế, khấu trừ TTĐB, xuất khẩu miễn thuế"
category: tax
tags: [sst, ttdb, special-consumption-tax, viet-nam, excise]
applicable_bots: [ja-sst, partner-sst, sa-advisory, sa-compliance, ja-advisory, ja-compliance]
editable: true
---

# Vietnam Thuế Tiêu Thụ Đặc Biệt (TTĐB / SST)

## Căn Cứ Pháp Lý

| Văn bản | Nội dung |
|---------|----------|
| Luật TTĐB số 27/2008/QH12 (sđbs bởi Luật 70/2014, 106/2016) | Luật gốc — đối tượng chịu thuế, biểu thuế, khấu trừ |
| Luật 106/2016/QH13 | Sửa đổi bổ sung: thuế suất bia, rượu, thuốc lá |
| NĐ 108/2015/NĐ-CP (sđbs bởi NĐ 14/2019) | Hướng dẫn chi tiết thi hành Luật TTĐB |
| TT 195/2015/TT-BTC (sđbs bởi TT 20/2017) | Hướng dẫn thi hành NĐ 108/2015 |
| TT 05/2012/TT-BTC | Hướng dẫn một số điều Luật TTĐB |

> **Lưu ý 2024-2025**: Dự thảo sửa đổi Luật TTĐB đang được lấy ý kiến — có thể tăng thuế suất thuốc lá và bổ sung nước ngọt, thực phẩm có hại sức khỏe.

---

## Đối Tượng Chịu Thuế TTĐB

### Hàng Hóa Chịu Thuế

| Nhóm | Hàng hóa | Thuế suất hiện hành |
|------|----------|---------------------|
| **Thuốc lá** | Thuốc điếu, xì gà, thuốc lá sợi, thuốc lào | **75%** |
| **Rượu** | Rượu từ 20° trở lên | **65%** |
| | Rượu dưới 20° | **35%** |
| **Bia** | Bia các loại | **65%** |
| **Xe ô tô dưới 24 chỗ** | Xe con dưới 9 chỗ ≤ 1.500 cc | **35%** |
| | Xe con dưới 9 chỗ 1.500 cc < cc ≤ 2.000 cc | **40%** |
| | Xe con dưới 9 chỗ 2.000 cc < cc ≤ 2.500 cc | **50%** |
| | Xe con dưới 9 chỗ > 2.500 cc đến 3.000 cc | **60%** |
| | Xe con dưới 9 chỗ > 3.000 cc | **150%** |
| | Xe từ 10 đến dưới 16 chỗ | **15%** |
| | Xe từ 16 đến dưới 24 chỗ | **10%** |
| | Xe pick-up | **15%** |
| | Xe thuần điện (EV) | **3%** |
| **Xe máy** | Xe gắn máy > 125 cc | **20%** |
| **Xăng các loại** | Xăng | **10%** |
| **Điều hoà** | Điều hòa không khí ≤ 90.000 BTU | **10%** |
| **Bài lá, vàng mã** | Bài lá, pháo, vàng mã | **70%** (bài lá) |
| **Kinh doanh dịch vụ** | Casino, trò chơi điện tử có thưởng | **35%** |
| | Kinh doanh golf | **20%** |
| | Kinh doanh xổ số | **15%** |

---

## Căn Cứ Tính Thuế

### Công Thức Chung

```
Thuế TTĐB phải nộp = Giá tính thuế TTĐB × Thuế suất TTĐB
```

### Giá Tính Thuế TTĐB

**Hàng hóa sản xuất trong nước:**
```
Giá tính thuế TTĐB = Giá bán của cơ sở sản xuất / (1 + Thuế suất TTĐB)
```
- Giá bán = giá bán ra của cơ sở sản xuất (chưa có VAT)
- Không bao gồm giá bán lẻ của đại lý thương mại

**Hàng hóa nhập khẩu:**
```
Giá tính thuế TTĐB = (Giá tính thuế nhập khẩu + Thuế nhập khẩu) / (1 + Thuế suất TTĐB)
```
Hoặc:
```
Giá tính thuế TTĐB = Giá tính thuế nhập khẩu + Thuế nhập khẩu
```
*(TTĐB tính trên giá đã có thuế nhập khẩu)*

**Chú ý quan trọng về giá tính thuế:**
- Cơ sở SX bán qua cơ sở thương mại liên kết: giá tính thuế = giá bán ra của cơ sở thương mại, không thấp hơn 7% so với giá bán bình quân của cơ sở thương mại cùng loại
- Nếu không có cơ sở thương mại độc lập tương đương → dùng giá bán ra của cơ sở SX

---

## Khấu Trừ Thuế TTĐB (Tax Credit)

**Nguyên tắc**: Cơ sở sản xuất hàng hóa chịu TTĐB bằng nguyên liệu đã nộp TTĐB được khấu trừ số TTĐB đã nộp đối với nguyên liệu.

**Điều kiện khấu trừ:**
1. Nguyên liệu đã thực nộp TTĐB khi nhập khẩu hoặc mua trong nước
2. Có chứng từ hợp lệ (tờ khai hải quan, chứng từ nộp thuế hoặc hóa đơn mua nguyên liệu)
3. Nguyên liệu dùng để SX ra hàng hóa chịu TTĐB (cùng dòng sản phẩm)

**Công thức khấu trừ:**
```
TTĐB khấu trừ = TTĐB thực nộp của nguyên liệu tương ứng với số lượng sản phẩm đã bán ra
```
- Khấu trừ theo tỷ lệ sử dụng thực tế
- Không khấu trừ phần nguyên liệu SX hàng hóa không chịu TTĐB

**Ví dụ — Rượu vang sản xuất từ rượu nhập khẩu:**
- Mua 10.000 lít cồn ethanol nhập khẩu, thuế suất 65%, đã nộp TTĐB = X
- SX ra 20.000 chai rượu 20°, bán được 15.000 chai
- Khấu trừ = X × (10.000/20.000) × (15.000/20.000) → điều chỉnh theo thực tế

---

## Không Chịu Thuế TTĐB (Exemptions)

| Trường hợp | Điều kiện |
|-----------|-----------|
| Hàng hóa xuất khẩu | Có hợp đồng XK, chứng từ thanh toán qua ngân hàng, tờ khai hải quan |
| Hàng hóa NK vào khu phi thuế quan | Doanh nghiệp chế xuất, khu KTX |
| Hàng hóa SX trong KCX, DNCX không tiêu thụ nội địa | Xuất khẩu 100% |
| Tàu bay, du thuyền dùng cho mục đích kinh doanh vận chuyển hành khách/hàng hóa | Có chứng nhận của cơ quan nhà nước có thẩm quyền |
| Xe ô tô cứu thương, xe dành cho người tàn tật | Theo quy định đặc biệt |
| Máy điều hòa dưới 90.000 BTU dùng cho tàu thuyền | Đăng ký sử dụng trên phương tiện đường thủy |

---

## Kê Khai & Nộp Thuế TTĐB

### Thời Hạn Kê Khai
- **Hàng tháng**: tờ khai TTĐB nộp chậm nhất ngày 20 tháng sau
- **Khi phát sinh**: nhập khẩu từng lần nộp theo tờ khai hải quan

### Mẫu Tờ Khai
- **01/TTĐB** — Tờ khai TTĐB (hàng hóa SX trong nước)
- **02/TTĐB** — Tờ khai TTĐB (nhập khẩu, theo tờ khai hải quan)

### Cơ Quan Quản Lý Thuế
- **Doanh nghiệp SX nội địa**: Chi cục Thuế / Cục Thuế nơi có cơ sở SX
- **NK hàng hóa**: Cơ quan Hải quan cửa khẩu

---

## Red Flags & Lưu Ý Thực Tiễn

### Rủi ro phổ biến
1. **Phân loại sai**: xe gắn máy 125 cc vs >125 cc — tranh chấp với CQT về dung tích xi lanh theo chứng nhận kỹ thuật
2. **Xe nhập khẩu nguyên chiếc (CBU) vs SKD/CKD**: áp thuế suất TTĐB khác nhau, phải xác định đúng trạng thái lắp ráp
3. **Rượu định nghĩa nồng độ cồn**: đo lường tại nhiệt độ nào (20°C), tranh chấp 20° vs < 20°
4. **Cơ sở bán qua đại lý liên kết**: CQT thường kiểm tra xem giá tính thuế có đủ 7% chênh lệch không
5. **Khấu trừ không đủ chứng từ**: chứng từ nộp TTĐB nguyên liệu bị thất lạc → không được khấu trừ

### Checklist Kiểm Toán TTĐB
- [ ] Xác nhận đối tượng chịu thuế đúng nhóm hàng hóa
- [ ] Kiểm tra giá tính thuế: có áp dụng quy tắc 7% với đại lý liên kết không?
- [ ] Khớp số liệu TTĐB trên tờ khai 01/TTĐB với sổ kế toán (TK 3332)
- [ ] Kiểm tra khấu trừ TTĐB: chứng từ đầy đủ, tỷ lệ phân bổ đúng
- [ ] Xác nhận hàng XK được miễn TTĐB: chứng từ thanh toán qua ngân hàng + tờ khai HQ
- [ ] So sánh doanh thu chịu TTĐB với doanh thu VAT — phát hiện rủi ro bỏ sót
