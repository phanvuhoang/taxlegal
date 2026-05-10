---
name: vietnam-customs-valuation
version: 1.0.0
description: >
  Skill về trị giá hải quan Việt Nam theo Hiệp định WTO-CVA: 6 phương pháp tính trị giá,
  các khoản cộng vào/trừ ra, trị giá giao dịch giữa các bên liên kết, và xử lý royalties,
  license fees trong trị giá hải quan.
category: customs
tags: [customs, valuation, tri-gia-hai-quan, cif, transaction-value, related-parties, royalty, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Trị Giá Hải Quan

> **Căn cứ:** Hiệp định WTO về Trị giá Hải quan (CVA), TT 39/2015/TT-BTC (sửa đổi TT 60/2019/TT-BTC)

---

## Phần 1 — Phương Pháp 1: Trị Giá Giao Dịch (Ưu Tiên Hàng Đầu)

### Công thức cơ bản

```
Trị giá hải quan = Giá FOB (đã thanh toán/phải trả) + Cộng thêm các khoản bắt buộc
```

**CIF tại cửa khẩu VN:**
```
= Giá mua thực tế (FOB)
+ Phí bảo hiểm (Insurance)
+ Cước phí vận chuyển đến cửa khẩu nhập đầu tiên tại VN (Freight)
+ Các khoản cộng thêm bắt buộc khác
```

### Các khoản PHẢI cộng thêm vào trị giá (dù chưa có trong giá hóa đơn)

| Khoản cộng thêm | Ví dụ |
|----------------|-------|
| **Hoa hồng và phí môi giới** (không phải hoa hồng mua) | Phí commission trả cho đại lý mua hàng |
| **Chi phí container, đóng gói** đặc biệt | Chi phí bao bì đặc biệt theo yêu cầu người mua |
| **Nguyên liệu, dụng cụ** cung cấp miễn phí cho người bán để SX hàng | Khuôn mẫu gửi cho nhà máy để sản xuất |
| **Tiền bản quyền và phí nhượng quyền** liên quan đến hàng NK | Royalty trả cho việc dùng thương hiệu trên hàng NK |
| **Lợi nhuận từ việc bán lại** thuộc về người bán | Ít phổ biến, chỉ áp dụng trong một số trường hợp |

### Các khoản KHÔNG cộng vào (được trừ ra nếu tách biệt)

| Khoản trừ |
|-----------|
| Cước phí vận chuyển SAU khi cập cảng VN |
| Phí bốc dỡ tại cảng VN |
| Thuế NK, GTGT tại VN |
| Lãi vay nếu tách biệt trong hóa đơn |
| Chi phí bảo hành sau khi mua (nếu tách biệt) |

---

## Phần 2 — 5 Phương Pháp Thay Thế (Theo Thứ Tự Ưu Tiên)

Chỉ áp dụng khi **không thể dùng Phương pháp 1** (trị giá giao dịch bị bác bỏ):

| Phương pháp | Căn cứ tính |
|------------|-----------|
| **PM2: Trị giá hàng giống hệt** | Giá của hàng giống hệt (identical goods) nhập vào VN cùng thời điểm |
| **PM3: Trị giá hàng tương tự** | Giá của hàng tương tự (similar goods) nhập vào VN cùng thời điểm |
| **PM4: Trị giá khấu trừ** | Giá bán tại VN × (1 − % lợi nhuận − chi phí nội địa) |
| **PM5: Trị giá tính toán** | Chi phí SX + Chi phí vận chuyển + Lợi nhuận định mức |
| **PM6: Phương pháp suy luận** | Áp dụng linh hoạt từ PM1–5 |

> **Thực tiễn VN:** Hải quan VN thường áp dụng **cơ sở dữ liệu trị giá** (GTT02) khi bác bỏ PM1 — DN cần chuẩn bị phản bác bằng chứng từ giá giao dịch thực tế.

---

## Phần 3 — Giao Dịch Giữa Các Bên Liên Kết

### Khi nào bị coi là bên liên kết?

| Tiêu chí | Ví dụ |
|---------|-------|
| Công ty mẹ-con (≥ 50% vốn) | Mua từ công ty mẹ ở nước ngoài |
| Có đại diện tham gia HĐQT | Director cross |
| Nhân sự quản lý chéo | CEO/CFO làm việc cho cả hai |
| Đối tác kinh doanh chia sẻ lợi nhuận | JV, partnership |
| Kiểm soát gián tiếp | Thông qua công ty thứ 3 |

### Hải quan VN xử lý giao dịch liên kết

1. Hải quan có quyền **đặt vấn đề** về tính đại diện của giá khi giao dịch giữa bên liên kết
2. DN phải **chứng minh** giá giao dịch liên kết **không bị ảnh hưởng** bởi mối quan hệ liên kết
3. Phương pháp chứng minh: **Test giá** (so sánh với giá bán cho bên độc lập; kiểm tra lợi nhuận gộp)

### Chứng từ cần chuẩn bị cho giao dịch liên kết

- [ ] Transfer pricing documentation (nếu có — liên kết với thuế TNDN)
- [ ] So sánh giá với giá bán cho bên độc lập cùng điều kiện
- [ ] Phân tích lợi nhuận gộp của DN bán
- [ ] Xác nhận giá phản ánh điều kiện thị trường (arm's length)

---

## Phần 4 — Royalties và License Fees

### Khi nào Royalty phải cộng vào trị giá?

Royalty (tiền bản quyền, phí nhượng quyền) **phải cộng vào trị giá hải quan** nếu:
1. Khoản royalty **liên quan đến hàng hóa** đang nhập
2. Việc trả royalty là **điều kiện để mua được hàng** (condition of sale)

**Ví dụ phải cộng:** Nhập sản phẩm mang thương hiệu nước ngoài → phải trả royalty theo license → Royalty phải cộng vào trị giá HQ.

**Ví dụ không cộng:** Royalty trả cho phần mềm post-importation (không liên quan đến giá hàng nhập) → Không cộng.

### Xử lý royalty trong thực tiễn

```
1. Xác định royalty rate (thường % doanh thu hoặc % giá bán)
2. Phân tích: royalty có "liên quan đến hàng nhập" và "điều kiện bán" không?
3. Nếu phải cộng: Tính royalty tương ứng cho lô hàng → Cộng vào CIF
4. Lưu ý: Thường phức tạp; đề nghị xin advance ruling từ TCHQ
```

---

## Phần 5 — Biên Bản Tham Vấn Trị Giá

Khi hải quan bác trị giá khai báo, họ sẽ:
1. Gửi **Thông báo kết quả phân loại** (yêu cầu giải thích)
2. DN có **3 ngày làm việc** để phản hồi
3. Nếu không đồng ý → **Tham vấn chính thức** (5 ngày)
4. Sau tham vấn → Hải quan ra **Quyết định ấn định trị giá**
5. DN có thể **nộp thuế theo trị giá ấn định + khiếu nại** (không được giữ hàng chờ giải quyết khiếu nại)

### Chiến lược kháng nghị trị giá thành công

- **Nhanh:** Chuẩn bị hồ sơ ngay khi nhận thông báo
- **Đầy đủ:** Cung cấp tất cả chứng từ giá (hợp đồng, LC, invoice gốc, catalog)
- **Chuyên nghiệp:** Tham chiếu TT 39/2015 và WTO CVA trong văn bản phản hồi
- **Có tiền lệ:** Nếu có tờ khai trước đây với cùng hàng + giá tương tự đã được chấp nhận → đính kèm làm bằng chứng
