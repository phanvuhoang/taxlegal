---
name: pit-finalization
version: 1.0.0
description: >
  Quy trình quyết toán thuế TNCN năm — cả cá nhân tự quyết toán lẫn doanh nghiệp quyết toán
  cho người lao động. Gồm SOP 9 bước eTax Mobile, điều kiện ủy quyền, mẫu biểu, deadline
  và các tình huống phức tạp. Áp dụng năm quyết toán 2025 (nộp 2026).
category: tax
tags: [pit, tncn, quyet-toan, finalization, etax, mau-02-qtt, vietnam, 2026]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Quyết Toán Thuế TNCN

> **Kỳ áp dụng:** Quyết toán năm 2025 (nộp tháng 4/2026)
> **Căn cứ:** TT 80/2021/TT-BTC, Luật Quản lý thuế 38/2019/QH14, Luật 109/2025/QH15

---

## Phần 1 — Ai Cần Tự Quyết Toán?

### Bắt buộc tự quyết toán

| Trường hợp | Ghi chú |
|-----------|---------|
| Thu nhập từ **2 nguồn trở lên** (không đủ ĐK ủy quyền) | Ngay cả khi từng nguồn đã khấu trừ đúng |
| Số thuế phải **nộp thêm > 50.000 đ** | Dù chỉ 1 nguồn |
| Muốn **hoàn thuế** | Không thể ủy quyền nếu có hoàn |
| Cá nhân nước ngoài **rời Việt Nam** | Phải quyết toán trước ngày rời |

### Được phép ủy quyền (điều kiện đồng thời)

1. Chỉ có 1 nguồn thu nhập từ tiền lương/tiền công
2. Không phát sinh hoàn thuế hoặc nộp thêm ≤ 50.000 đ
3. Đang làm việc tại DN tại thời điểm ủy quyền

> **Lỗi thường gặp:** Làm thêm freelance (dù chỉ 1 lần) + ủy quyền cho DN chính → **SAI**. Phải tự quyết toán.

---

## Phần 2 — Deadline 2026

| Đối tượng | Hạn nộp |
|----------|---------|
| Cá nhân tự quyết toán (thuế năm 2025) | **30/04/2026** (→ 04/05/2026 nếu trùng lễ) |
| DN quyết toán cho người lao động (05/QTT-TNCN) | **31/03/2026** |
| Nộp tiền thuế còn phải nộp thêm | **30/04/2026** |

> **Lưu ý:** Chậm nộp mà **có hoàn thuế** → **KHÔNG bị phạt**. Hoàn tự động xử lý trong 3 ngày làm việc.
> Chậm nộp mà **phải nộp thêm** → phạt hành chính + 0.03%/ngày trên số tiền chậm.

---

## Phần 3 — SOP Quyết Toán Cá Nhân qua eTax Mobile

### Bước 1: Cài đặt & Đăng nhập
- Tải app **eTax Mobile** (App Store / Google Play)
- Đăng nhập bằng MST + mật khẩu hoặc **VNeID mức độ 2**
- Kiểm tra thông tin cá nhân chính xác

### Bước 2: Vào chức năng quyết toán
- Chọn **"Hỗ trợ quyết toán thuế TNCN"**
- Chọn **"Hỗ trợ lập tờ khai quyết toán"**
- Chọn năm quyết toán: **2025**

### Bước 3: Tra cứu dữ liệu
- Nhấn **"Tra cứu"** → hệ thống tự tổng hợp thu nhập + thuế đã khấu trừ
- Nếu dữ liệu sai → liên hệ **đơn vị chi trả** để điều chỉnh (không tự sửa)

### Bước 4: Tạo tờ khai
- Nhấn **"Tạo tờ khai 02/QTT-TNCN gợi ý"**
- Trả lời câu hỏi hệ thống
- Điền thông tin + phụ lục

### Bước 5: Kiểm tra NPT
- Vào **"Bảng kê 02-1/BK-QTT-TNCN"**
- Bổ sung NPT nếu bị thiếu
- Kiểm tra MST của từng NPT

### Bước 6: Cam kết & Nộp
- Kiểm tra lại toàn bộ
- Tích ô cam kết
- Nếu hoàn thuế: điền thông tin tài khoản ngân hàng
- Nhấn **"Nộp tờ khai"**

### Bước 7: Đính kèm hồ sơ
- Upload chứng từ khấu trừ thuế (từng đơn vị chi trả)
- Upload CCCD/CMND (bản sao)
- Upload hợp đồng lao động (nếu có nhiều nơi)

### Bước 8: Xác thực OTP
- Nhập mã OTP gửi về số điện thoại đã đăng ký

### Bước 9: Nộp tiền (nếu phải nộp thêm)
- Tại trang chủ eTax Mobile: chọn **"Nộp thuế"** → "Tra cứu" → "Nộp tất cả"
- Tạo giấy nộp tiền → Thanh toán qua ngân hàng liên kết

---

## Phần 4 — SOP Quyết Toán qua Cổng Thuế Điện Tử

**URL:** `canhan.gdt.gov.vn`

1. Đăng nhập → Chọn **"Quyết toán thuế"** → "Kê khai trực tuyến"
2. Chọn tờ khai **02/QTT-TNCN**
3. Điền thông tin cá nhân, chọn cơ quan thuế quản lý
4. Khai chi tiết + bảng kê giảm trừ gia cảnh
5. Kiểm tra, cam đoan → Kết xuất XML để lưu
6. Nộp tờ khai + đính kèm tài liệu

---

## Phần 5 — Mẫu Biểu Quan Trọng

| Mẫu | Dùng cho | Đối tượng nộp |
|-----|---------|--------------|
| **02/QTT-TNCN** | Quyết toán TNCN năm | Cá nhân tự kê khai |
| **02-1/BK-QTT-TNCN** | Bảng kê NPT | Đính kèm 02/QTT |
| **05/QTT-TNCN** | Quyết toán cho NLĐ | Doanh nghiệp |
| **05-1/BK-QTT-TNCN** | Bảng kê người lao động | Đính kèm 05/QTT |
| **08/CK-TNCN** | Cam kết thu nhập chưa đến ngưỡng | Cá nhân KD < 60tr |
| **09/CKT-TNCN** | Chứng từ khấu trừ thuế | DN lập cho từng cá nhân |

---

## Phần 6 — Trình tự DN Quyết Toán (Mẫu 05/QTT-TNCN)

```
1. Thu thập bảng lương 12 tháng + phụ cấp + thưởng + equity
   ↓
2. Cộng tổng thu nhập chịu thuế từng nhân viên
   ↓
3. Trừ BHXH/BHYT/BHTN phần cá nhân đóng (theo trần)
   ↓
4. Áp dụng giảm trừ gia cảnh (15.5tr/tháng + 6.2tr/NPT/tháng)
   ↓
5. Trừ các khoản giảm trừ khác (từ thiện, bảo hiểm nhân thọ...)
   ↓
6. Tính PIT theo biểu lũy tiến 5 bậc 2026
   ↓
7. So sánh PIT tính được vs. PIT đã khấu trừ trong năm
   ↓
8. Hoàn thuế hoặc thu thêm (nếu có)
   ↓
9. Lập Mẫu 05/QTT-TNCN + Phụ lục 05-1/BK-QTT-TNCN
   ↓
10. Nộp trước 31/3 năm sau (DN); gửi 09/CKT-TNCN cho từng NLĐ
```

---

## Phần 7 — Tình Huống Phức Tạp

### 7.1 Đổi việc giữa năm

**Vấn đề:** Nhân viên làm Công ty A đến tháng 6, chuyển Công ty B từ tháng 7.

**Thực hiện:**
- Công ty A lập chứng từ 09/CKT-TNCN cho 6 tháng → chuyển cho nhân viên
- Công ty B **không được** cộng dồn với A → chỉ tính từ tháng 7
- Nhân viên: **bắt buộc tự quyết toán** (2 nguồn thu nhập)

> **Lỗi thường gặp:** Công ty B áp dụng giảm trừ gia cảnh đầy đủ từ tháng 7 → tính thuế thấp hơn thực tế → nhân viên nộp thêm khi quyết toán.

### 7.2 Expat rời Việt Nam

**Bắt buộc quyết toán trước ngày rời.** Quy trình:
1. Tính thu nhập từ đầu năm đến ngày rời
2. Xác định tư cách cư trú (183-day rule)
3. Nếu cư trú: biểu lũy tiến + toàn bộ thu nhập toàn cầu
4. Nộp tờ khai + nộp tiền thuế trước khi xuất cảnh

### 7.3 Freelancer nhiều nơi

- Mỗi nơi chi trả: khấu trừ 10% nếu ≥ 2 triệu/lần
- Cuối năm: **bắt buộc tự quyết toán** cộng tổng tất cả thu nhập theo biểu lũy tiến
- Nếu đã khấu trừ thừa → hoàn thuế; nếu thiếu → nộp thêm

---

## Phần 8 — Hồ Sơ Cần Chuẩn Bị (Cá nhân)

- [ ] CCCD/CMND (bản sao còn hiệu lực)
- [ ] Mã số thuế cá nhân (MST)
- [ ] Chứng từ khấu trừ thuế từ tất cả nơi chi trả (Mẫu 09/CKT-TNCN)
- [ ] Tờ khai 02/QTT-TNCN + phụ lục 02-1 (nếu có NPT)
- [ ] Hóa đơn đóng góp từ thiện/khuyến học (nếu có)
- [ ] Số tài khoản ngân hàng (nếu xin hoàn thuế)
- [ ] Hợp đồng lao động từ tất cả nơi làm việc trong năm (nếu cần)
