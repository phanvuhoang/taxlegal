---
name: vat-exempt-classification
version: 1.0.0
description: >
  Skill phân loại hàng hóa/dịch vụ không chịu thuế GTGT và chịu thuế suất 5% tại Việt Nam.
  Danh mục miễn thuế theo Điều 5 Luật GTGT, điều kiện áp dụng 5%, rủi ro phân loại sai,
  và escalation path cho các trường hợp biên (edge cases).
category: tax
tags: [vat, gtgt, exempt, mien-thue, reduced-rate, 5-percent, classification, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Phân Loại Hàng Hóa/Dịch Vụ Không Chịu Thuế & 5% GTGT

> **Căn cứ:** Luật Thuế GTGT Điều 5 (miễn), Điều 9 (5%), TT 219/2013/TT-BTC Điều 4 và 10

---

## Phần 1 — Danh Mục Không Chịu Thuế GTGT (Điều 5)

### Nhóm 1: Dịch vụ tài chính & bảo hiểm

| Hàng hóa/Dịch vụ | Ghi chú |
|-----------------|---------|
| Dịch vụ cấp tín dụng, cho vay | Lãi suất nhận về |
| Kinh doanh ngoại tệ | Chênh lệch tỷ giá |
| Dịch vụ thanh toán, chuyển tiền | Phí giao dịch ngân hàng |
| Dịch vụ bảo hiểm | Nhân thọ, phi nhân thọ, bảo hiểm nông nghiệp |
| Chứng khoán: môi giới, tư vấn đầu tư | Cổ phiếu, trái phiếu |

### Nhóm 2: Y tế & Giáo dục

| Hàng hóa/Dịch vụ | Ghi chú |
|-----------------|---------|
| Dịch vụ khám, chữa bệnh | Bệnh viện, phòng khám |
| Dịch vụ thú y | Khám chữa gia súc, gia cầm |
| Dạy học, dạy nghề | Mọi cấp học chính thức |
| Dịch vụ đào tạo nghề | Có chứng chỉ theo quy định |

### Nhóm 3: Bất động sản & Xây dựng

| Hàng hóa/Dịch vụ | Ghi chú |
|-----------------|---------|
| Chuyển quyền sử dụng đất | KHÔNG bao gồm BĐS gắn trên đất |
| Nhà ở bán/cho thuê của cá nhân không đăng ký KD | Chú ý: tổ chức KD bán nhà ở thương mại = 10% |

### Nhóm 4: Nông nghiệp & Chế biến thô

| Hàng hóa/Dịch vụ | Ghi chú |
|-----------------|---------|
| Sản phẩm trồng trọt, chăn nuôi **chưa qua chế biến** bán bởi tổ chức/cá nhân sản xuất | Lúa, ngô, khoai, sắn, rau quả... khi bán thẳng từ hộ nông dân |
| Muối (NaCl từ muối biển, muối mỏ) | |
| Tưới tiêu, cày bừa, thu hoạch nông nghiệp | DV phục vụ nông nghiệp |

### Nhóm 5: Văn hóa, xã hội, khoa học

| Hàng hóa/Dịch vụ | Ghi chú |
|-----------------|---------|
| Xuất bản báo, tạp chí, bản tin | Báo in/điện tử |
| Phát thanh, truyền hình (theo lịch phát sóng nhà nước) | Không bao gồm dịch vụ truyền hình trả tiền |
| Dịch vụ bưu chính phổ cập | Tem thư, chuyển thư cơ bản |
| Nhập khẩu một số máy móc, thiết bị CNTT | Theo danh mục Chính phủ phê duyệt |

### Nhóm 6: Hàng nhập khẩu đặc thù

| Hàng hóa | Ghi chú |
|---------|---------|
| Vũ khí, đạn dược cho quốc phòng/an ninh | Nhập theo kế hoạch nhà nước |
| Hàng hóa nhập khẩu để viện trợ nhân đạo | Theo quyết định cơ quan nhà nước |
| Hàng hóa là quà tặng trong ngưỡng miễn thuế | Tùy ngưỡng hải quan |

---

## Phần 2 — Thuế Suất 5% (Điều 9)

| Hàng hóa/Dịch vụ | Điều kiện áp dụng 5% |
|-----------------|---------------------|
| **Nước sạch** (sinh hoạt, sản xuất) | Nước cấp bởi đơn vị cấp nước (SAWACO, HAWACO...); KHÔNG bao gồm nước đóng chai |
| **Phân bón** | Tất cả loại phân bón dùng trong nông nghiệp |
| **Thức ăn chăn nuôi, thức ăn thủy sản** | Thức ăn gia súc, gia cầm, tôm, cá... |
| **Thuốc trừ sâu, thuốc bảo vệ thực vật** | Theo danh mục Bộ NN&PTNT |
| **Thiết bị y tế** | Danh mục Bộ Y tế phê duyệt; máy chẩn đoán, dụng cụ phẫu thuật... |
| **Dụng cụ giảng dạy** | Bàn ghế học sinh, bảng, máy chiếu cho giáo dục |
| **Sách** | Sách các loại (KHÔNG bao gồm báo, tạp chí) |
| **Đường mía, đường củ cải** | Sản phẩm đường thô và tinh luyện |
| **Dịch vụ kỹ thuật trực tiếp phục vụ sản xuất nông nghiệp** | Gieo cấy, thu hoạch, sấy, bảo quản nông sản |
| **Sản phẩm trồng trọt, chăn nuôi, thủy sản** bán bởi doanh nghiệp/HTX (đã qua chế biến thông thường) | KHÔNG phải hộ nông dân bán thẳng (hộ nông dân = không chịu) |

> **Conservative default (R-VN Q6.3):** Nếu không chắc hàng hóa có trong danh sách 5% → **áp 10%** cho đến khi xác nhận cụ thể.

---

## Phần 3 — Phân Biệt Dễ Nhầm

### 3.1 Nông sản: Ai bán thì mới áp dụng?

| Người bán | Xử lý GTGT |
|----------|-----------|
| Hộ nông dân tự sản xuất → bán trực tiếp | **Không chịu thuế** (Điều 5) |
| Doanh nghiệp/HTX thu gom, bán chưa qua chế biến | **Không chịu thuế** (Điều 5) |
| Doanh nghiệp đã qua chế biến thông thường (sơ chế) | **5%** (Điều 9) |
| Doanh nghiệp đã chế biến sâu (thực phẩm đóng gói) | **10%** (Điều 11) |

### 3.2 Sách vs Báo

| Loại | Xử lý |
|------|-------|
| Sách (mọi thể loại) | **5%** |
| Báo, tạp chí, bản tin | **Không chịu thuế** |
| Sách điện tử (e-book) | Tier 2 — kiểm tra; thường **5%** nếu là bản số hóa từ sách in |

### 3.3 Thiết bị y tế vs Sản phẩm tiêu dùng

| Loại | Xử lý |
|------|-------|
| Thiết bị y tế trong danh mục Bộ Y tế | **5%** |
| Mỹ phẩm, TPCN, thực phẩm chức năng | **10%** |
| Dụng cụ y tế không trong danh mục | **10%** (conservative default) |

### 3.4 Nhà ở và BĐS

| Loại | Xử lý |
|------|-------|
| Chuyển nhượng quyền sử dụng đất | **Không chịu thuế** |
| Bán nhà ở thương mại (doanh nghiệp đăng ký KD BĐS) | **10%** (BĐS gắn liền đất) |
| Cho thuê nhà ở dài hạn (cá nhân không đăng ký KD) | **Không chịu thuế** |
| Cho thuê văn phòng, mặt bằng kinh doanh | **10%** |
| Dịch vụ xây dựng, lắp đặt BĐS | Tier 2 — phức tạp (R-VN-4) — escalate |

---

## Phần 4 — Rủi Ro Phân Loại Sai

### Hậu quả phân loại sai

| Lỗi phân loại | Hậu quả |
|--------------|---------|
| Áp 0% cho DV không đủ điều kiện | Truy thu thuế + lãi chậm nộp 0.03%/ngày |
| Áp 5% cho hàng không trong danh mục | Truy thu 5% chênh lệch + lãi |
| Không chịu thuế → thực ra chịu | Phạt khai sai 20% + truy thu |
| Khấu trừ đầu vào cho dịch vụ miễn thuế | Hoàn lại đầu vào đã khấu trừ sai |

### Nguyên tắc escalation

- **Cụ thể, đơn giản, trong danh mục rõ ràng** → Áp dụng ngay
- **Biên (edge case) hoặc hàng hóa mới, phức tạp** → Tier 2 — xin ruling từ CQT
- **BĐS, xây dựng, FCT, phân bổ đầu vào phức tạp** → Escalate chuyên gia
