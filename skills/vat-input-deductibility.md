---
name: vat-input-deductibility
version: 1.0.0
description: >
  Skill chuyên về khấu trừ thuế GTGT đầu vào tại Việt Nam: điều kiện khấu trừ, hóa đơn
  điện tử bắt buộc, các khoản không được khấu trừ, phân bổ khi có doanh thu miễn thuế,
  và FCT trên dịch vụ quốc tế. Dựa trên vietnam-vat.md + openaccountants-tax nguồn.
category: tax
tags: [vat, gtgt, input-vat, khau-tru, hoa-don-dien-tu, vietnam, deductibility]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Khấu Trừ Thuế GTGT Đầu Vào

> **Căn cứ:** Luật Thuế GTGT 13/2008/QH12 (sửa đổi 2013–2016), TT 219/2013/TT-BTC, TT 103/2014/TT-BTC (FCT), NĐ 123/2020/NĐ-CP (hóa đơn điện tử)

---

## Phần 1 — Điều Kiện Cơ Bản Để Khấu Trừ

Thuế GTGT đầu vào được khấu trừ khi **đồng thời** thỏa mãn **4 điều kiện:**

| # | Điều kiện | Bằng chứng cần có |
|---|-----------|-------------------|
| 1 | **Hóa đơn điện tử hợp lệ** (hóa đơn GTGT) | Số hóa đơn, ngày, MST bên bán, MST bên mua, mô tả HH/DV, số lượng, đơn giá, thuế suất, tiền thuế |
| 2 | **Chứng từ thanh toán qua ngân hàng** (nếu > 20 triệu) | Sao kê ngân hàng, ủy nhiệm chi, UNT |
| 3 | **Hàng hóa/dịch vụ phục vụ sản xuất kinh doanh chịu thuế** | Có thể chứng minh mục đích kinh doanh |
| 4 | **Đã phát sinh giao dịch thực tế** | Không phải hóa đơn ảo, không phải trên giấy |

---

## Phần 2 — Hóa Đơn Điện Tử (Bắt Buộc Từ 2022)

### Yêu cầu bắt buộc

Từ **01/07/2022**, tất cả doanh nghiệp đăng ký kinh doanh phải phát hành **hóa đơn điện tử (HĐĐT)** đã đăng ký với **Tổng cục Thuế (GDT)**.

**Các trường bắt buộc trên HĐĐT:**
- MST bên bán (10 chữ số)
- MST bên mua (10 chữ số)
- Ngày phát hành
- Mô tả hàng hóa/dịch vụ
- Số lượng, đơn giá, thành tiền
- Thuế suất GTGT, tiền thuế GTGT
- Mã xác thực của GDT (mã QR)

> **Conservative default:** Nếu không xác nhận được HĐĐT hợp lệ → **KHÔNG được khấu trừ** đầu vào.
> Mọi input credit đều là **tạm thời** cho đến khi xác nhận hóa đơn điện tử.

### Tra cứu hóa đơn

Kiểm tra tính hợp lệ: **hoadondientu.gdt.gov.vn** → nhập mã hóa đơn, ngày, MST bên bán.

---

## Phần 3 — Các Khoản KHÔNG Được Khấu Trừ

### 3.1 Bảng phân loại khoản không khấu trừ

| Loại khoản | Lý do không khấu trừ | Xử lý |
|-----------|---------------------|-------|
| Mua hàng/dịch vụ **không phục vụ kinh doanh** | Không đáp ứng điều kiện cơ bản | Hạch toán vào chi phí (không phải VAT input) |
| **Xe ô tô dưới 24 chỗ** mua vào (không phải dịch vụ vận tải, du lịch, khách sạn) | Không được khấu trừ (trừ xe chuyên dụng) | Đưa vào giá xe (nguyên giá TSCĐ) |
| Hàng hóa **bị mất mát, thiên tai** không có bồi thường | Mất mục đích kinh doanh | Phải điều chỉnh giảm đầu vào |
| Hàng hóa **tặng, biếu** không có hóa đơn | Không đủ điều kiện hóa đơn | Không được khấu trừ |
| Thuế GTGT **đã hoàn tiền** | Đã được xử lý rồi | Không khấu trừ tiếp |
| Giao dịch giá trị > 20 triệu **thanh toán bằng tiền mặt** | Vi phạm điều kiện thanh toán | Không được khấu trừ dù có đủ hóa đơn |

### 3.2 Ngưỡng thanh toán ngân hàng

| Giá trị giao dịch | Yêu cầu |
|------------------|---------|
| **≤ 20.000.000 đ** | Có thể thanh toán tiền mặt + vẫn khấu trừ |
| **> 20.000.000 đ** | **Bắt buộc** thanh toán qua ngân hàng để được khấu trừ |

> **Lưu ý:** Tính theo từng hóa đơn, không phân kỳ để lách ngưỡng.

---

## Phần 4 — Phân Bổ Đầu Vào (Doanh nghiệp Vừa Chịu Thuế Vừa Miễn Thuế)

### Khi nào phải phân bổ?

Doanh nghiệp có **cả doanh thu chịu thuế lẫn doanh thu không chịu thuế** (ví dụ: vừa IT consulting [10%] vừa cho vay tài chính [miễn]) → phải phân bổ đầu vào theo tỷ lệ.

### Công thức phân bổ

```
Tỷ lệ khấu trừ (%) = Doanh thu chịu thuế GTGT ÷ Tổng doanh thu × 100%

Đầu vào được khấu trừ = Tổng đầu vào dùng chung × Tỷ lệ khấu trừ
Đầu vào không được khấu trừ = Tổng đầu vào dùng chung × (1 − Tỷ lệ)
```

> **Conservative default (R-VN-3):** Nếu không có đủ số liệu → **0% đầu vào** dùng chung được khấu trừ cho đến khi tỷ lệ được xác nhận. **Out of scope** nếu không có dữ liệu doanh thu cả năm → escalate.

### Ví dụ phân bổ

**Doanh nghiệp IT + đầu tư tài chính:**
- Doanh thu IT (10% GTGT): 2 tỷ
- Doanh thu lãi vay (miễn): 500 triệu
- Tổng doanh thu: 2.5 tỷ
- Tỷ lệ khấu trừ = 2.000/2.500 = **80%**
- Đầu vào dùng chung: 100 triệu → Được khấu trừ: 80 triệu; Không khấu trừ: 20 triệu

---

## Phần 5 — FCT trên Dịch Vụ Quốc Tế (R-VN-5)

### Nguyên tắc cơ bản

Khi công ty VN thanh toán cho **nhà cung cấp dịch vụ nước ngoài không có pháp nhân tại VN** → phát sinh **Thuế Nhà Thầu Nước Ngoài (FCT = Foreign Contractor Tax)**.

```
FCT = CIT component (5%) + VAT component (10%)
```

> **Quan trọng:** Phần VAT component của FCT **KHÔNG được khấu trừ** như đầu vào GTGT thông thường.

### Các nhà cung cấp thường gặp

| Nhà cung cấp | Tình trạng FCT |
|-------------|---------------|
| Google Ads, Google Workspace | FCT áp dụng (trừ khi đã đăng ký tại VN) |
| Meta/Facebook Ads | FCT áp dụng |
| Microsoft 365, Azure | Kiểm tra: nếu công ty VN Microsoft xuất hóa đơn → thông thường; nếu từ Ireland → FCT |
| AWS, Zoom, Slack, Notion, OpenAI | FCT áp dụng — flag cho chuyên gia |
| Nhà cung cấp đã đăng ký tại VN | Khấu trừ bình thường nếu có HĐĐT |

### Câu hỏi phải hỏi trước khi xử lý

1. Nhà cung cấp nước ngoài có đăng ký thuế tại VN không? (có MST VN không?)
2. Họ có phát hành HĐĐT theo quy định VN không?
3. Nếu không → công ty VN có bắt buộc kê khai và nộp FCT thay không?

> **R-VN-5:** Đây là vùng phức tạp. **Không khấu trừ đầu vào** cho đến khi xác nhận tình trạng đăng ký của nhà cung cấp. **Escalate** nếu giá trị lớn.

---

## Phần 6 — Red Flag & Conservative Defaults

### Red flag thresholds

| Ngưỡng | Loại | Hành động |
|--------|------|-----------|
| Giao dịch đơn lẻ > 50.000.000 đ | HIGH | Xem xét kỹ hóa đơn, thanh toán qua ngân hàng |
| Delta thuế từ default ≥ 5.000.000 đ | HIGH | Phải flag và xác nhận |
| >40% đầu vào từ 1 nhà cung cấp | MEDIUM | Kiểm tra rủi ro tập trung |
| > 4 conservative defaults trong 1 kỳ | MEDIUM | Review lại toàn bộ |
| Net VAT position < 20.000.000 đ | LOW | Xem xét tính nhất quán |

### Conservative defaults

| Tình huống không rõ | Default bảo thủ |
|-------------------|----------------|
| Không biết thuế suất áp dụng | **10% standard** |
| Không xác nhận được export qualification | **Domestic 10%** |
| Không có HĐĐT | **Không khấu trừ** |
| Hàng hóa/DV mục đích chưa rõ | **0% khấu trừ** |
| Nhà cung cấp nước ngoài chưa xác nhận | **FCT flag — không khấu trừ** |

---

## Phần 7 — Refusal Catalogue

| Mã | Tình huống | Phản hồi chuẩn |
|----|-----------|----------------|
| R-VN-1 | Doanh nghiệp thuế trực tiếp | "Phương pháp trực tiếp không khấu trừ đầu vào theo cách thông thường. Xác nhận phương pháp trước khi tiếp tục." |
| R-VN-2 | Doanh thu < 1 tỷ (dưới ngưỡng đăng ký) | "Xác nhận tình trạng đăng ký GTGT trước khi kê khai khấu trừ." |
| R-VN-3 | Phân bổ đầu vào (doanh thu hỗn hợp) | "Yêu cầu toàn bộ dữ liệu doanh thu cả năm để tính tỷ lệ phân bổ — out of scope nếu thiếu." |
| R-VN-4 | Bất động sản và xây dựng | "VAT bất động sản và xây dựng có quy định đặc thù — escalate chuyên gia." |
| R-VN-5 | FCT nhà thầu nước ngoài | "FCT phức tạp — không khấu trừ đầu vào cho đến khi xác nhận tình trạng đăng ký nhà cung cấp." |
