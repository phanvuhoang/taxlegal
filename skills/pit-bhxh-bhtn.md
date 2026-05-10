---
name: pit-bhxh-bhtn
version: 1.0.0
description: >
  Skill về BHXH một lần và trợ cấp thất nghiệp BHTN tại Việt Nam 2026. Bao gồm điều kiện
  rút BHXH 1 lần (Luật 41/2024), công thức tính, bảng ước tính nhanh, điều kiện hưởng BHTN,
  mức trần theo vùng, và tác động đến quyết toán thuế TNCN.
category: tax
tags: [bhxh, bhtn, bao-hiem-xa-hoi, social-insurance, unemployment, vietnam, 2026]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: BHXH Một Lần & Trợ Cấp Thất Nghiệp (2026)

> **Căn cứ BHXH:** Luật BHXH 2024 (Luật số 41/2024/QH15), hiệu lực từ 01/07/2025
> **Căn cứ BHTN:** Luật Việc làm 2025, NĐ 293/2025/NĐ-CP (lương tối thiểu vùng 2026)

---

## Phần 1 — BHXH Một Lần

### 1.1 Ai Được Rút BHXH 1 Lần?

> ⚠️ **CẢNH BÁO:** Rút BHXH 1 lần = MẤT toàn bộ thời gian đóng, mất quyền hưởng lương hưu, mất BHYT miễn phí khi về già.

#### Nhóm A: Tham gia BHXH TRƯỚC 01/07/2025

Được rút nếu đủ **đồng thời** 4 điều kiện:
1. Đã nghỉ việc (chấm dứt tham gia BHXH bắt buộc)
2. Sau **12 tháng** không đóng BHXH bắt buộc và không đóng BHXH tự nguyện
3. Chưa đủ **20 năm** đóng BHXH
4. Có đơn đề nghị hưởng

> **Đóng trên 20 năm: KHÔNG được rút** theo điều kiện này (trừ ngoại lệ bên dưới).

#### Nhóm B: Tham gia BHXH TỪ 01/07/2025 trở đi

**KHÔNG** được rút theo điều kiện "12 tháng nghỉ việc". Chỉ được rút nếu:
- Đủ tuổi nghỉ hưu nhưng chưa đủ **15 năm** đóng
- Ra nước ngoài định cư (có hồ sơ xác nhận)
- Mắc bệnh nguy hiểm đến tính mạng (ung thư, xơ gan mất bù, lao nặng, AIDS, bại liệt...)
- Suy giảm khả năng lao động từ **81%** trở lên

#### Decision tree nhanh

```
Bạn đóng BHXH trước hay sau 01/07/2025?
│
├── TRƯỚC 01/07/2025
│   ├── Đóng < 20 năm + nghỉ 12 tháng? → ĐỦ ĐIỀU KIỆN RÚT
│   └── Đóng ≥ 20 năm? → KHÔNG ĐỦ (trừ bệnh hiểm nghèo, ra nước ngoài)
│
└── TỪ 01/07/2025
    └── Chỉ rút khi: bệnh hiểm nghèo, ra nước ngoài, đủ tuổi hưu chưa đủ 15 năm
```

---

### 1.2 Công Thức Tính Mức Hưởng BHXH 1 Lần

```
Mức hưởng = (1.5 × MBQTL × Số năm đóng TRƯỚC 2014)
           + (2.0 × MBQTL × Số năm đóng TỪ 2014 trở đi)
```

- **MBQTL** = Mức Bình Quân Tiền Lương tháng đóng BHXH **đã nhân hệ số trượt giá** (tra trên VssID)
- **Số năm:** Tháng lẻ 1–6 = 0.5 năm; tháng lẻ 7–11 = 1 năm

### 1.3 Ví Dụ Tính Cụ Thể

| Case | Thời gian đóng | Trước 2014 | Từ 2014 | MBQTL | Công thức | Kết quả |
|------|---------------|-----------|---------|-------|-----------|---------|
| 1 | 10 năm (2013–2022) | 1 năm | 9 năm | 12 triệu | (1.5×12×1)+(2×12×9) | **234 triệu** |
| 2 | 15 năm (2010–2025) | 4 năm | 11.5 năm | 15 triệu | (1.5×15×4)+(2×15×11.5) | **435 triệu** |
| 3 | 12 năm (2014–2026) | 0 | 12 năm | 10 triệu | 2×10×12 | **240 triệu** |
| 4 | 18 năm (2005–2023) | 9 năm | 9.5 năm | 20 triệu | (1.5×20×9)+(2×20×9.5) | **650 triệu** |

### 1.4 Bảng Ước Tính Nhanh

| Số năm đóng | MBQTL 8tr | MBQTL 10tr | MBQTL 15tr | MBQTL 20tr |
|-------------|-----------|------------|------------|------------|
| 5 năm (sau 2014) | 80 tr | 100 tr | 150 tr | 200 tr |
| 10 năm (sau 2014) | 160 tr | 200 tr | 300 tr | 400 tr |
| 10 năm (5+5) | 140 tr | 175 tr | 262 tr | 350 tr |
| 15 năm (5+10) | 220 tr | 275 tr | 412 tr | 550 tr |
| 18 năm (9+9) | 252 tr | 315 tr | 472 tr | 630 tr |

*Chưa tính hệ số trượt giá. (X+Y) = X năm trước 2014 + Y năm từ 2014.*

### 1.5 So Sánh: Rút 1 Lần vs Bảo Lưu

| Tiêu chí | Rút 1 lần | Bảo lưu (chờ lương hưu) |
|----------|-----------|------------------------|
| Tiền nhận ngay | Có | Không |
| Lương hưu hàng tháng (trọn đời) | ❌ MẤT | ✅ 45–75% MBQTL |
| BHYT miễn phí khi nghỉ hưu | ❌ MẤT | ✅ Có |
| Trợ cấp mai táng + tiền tuất | ❌ MẤT | ✅ Có |
| Đi làm lại | Bắt đầu từ đầu (0 năm) | Cộng dồn thời gian cũ |

> **Ví dụ so sánh (15 năm đóng, MBQTL 15tr):**
> - Rút 1 lần: ~412 triệu (1 lần duy nhất)
> - Bảo lưu + đóng thêm 5 năm (20 năm) → lương hưu ≈ 6.75 triệu/tháng trọn đời + BHYT
> - Sống thêm 20 năm sau hưu: tổng nhận ≈ **1.62 tỷ** (≫ 412 triệu)

### 1.6 Hồ Sơ & Quy Trình Rút

| STT | Giấy tờ | Ghi chú |
|-----|---------|---------|
| 1 | Sổ BHXH (bản chính) | Đã chốt sổ tại đơn vị cũ |
| 2 | Đơn đề nghị (Mẫu 14-HSB) | Tải tại baohiemxahoi.gov.vn |
| 3 | CMND/CCCD (bản sao) | Còn hiệu lực |

- **Nộp tại:** BHXH quận/huyện nơi cư trú, hoặc online dichvucong.baohiemxahoi.gov.vn, hoặc app **VssID**
- **Thời gian xử lý:** Tối đa 10 ngày làm việc
- **Nhận tiền qua:** Tài khoản ngân hàng đã đăng ký

---

## Phần 2 — Trợ Cấp Thất Nghiệp (BHTN) 2026

### 2.1 Điều Kiện Hưởng

Đủ **đồng thời 4 điều kiện:**

1. **Đã chấm dứt HĐLĐ** đúng quy định (không phải đơn phương trái pháp luật)
2. **Đã đóng BHTN đủ thời gian:**
   - HĐLĐ ≥ 12 tháng: đóng đủ **12 tháng** trong **24 tháng** trước nghỉ
   - HĐLĐ 1–12 tháng: đóng đủ **12 tháng** trong **36 tháng** trước nghỉ
3. **Nộp hồ sơ** trong vòng **3 tháng** kể từ ngày nghỉ việc
4. **Chưa tìm được việc** sau 10 ngày kể từ ngày nộp hồ sơ

### 2.2 Công Thức Tính Mức Hưởng

```
Trợ cấp thất nghiệp/tháng = 60% × Bình quân lương đóng BHTN 6 tháng cuối
```

**Trần hưởng:** Không quá **5 × Lương tối thiểu vùng** tại tháng cuối đóng BHTN.

| Vùng | Lương tối thiểu (2026) | Trần TCTN/tháng |
|------|----------------------|----------------|
| Vùng I (HN, HCM...) | 5.110.000 đ | **25.550.000 đ** |
| Vùng II | 4.540.000 đ | **22.700.000 đ** |
| Vùng III | 3.970.000 đ | **19.850.000 đ** |
| Vùng IV | 3.570.000 đ | **17.850.000 đ** |

*Lương tối thiểu vùng theo NĐ 293/2025/NĐ-CP.*

### 2.3 Thời Gian Hưởng

| Thời gian đóng BHTN | Số tháng hưởng |
|---------------------|---------------|
| 12–36 tháng | **3 tháng** |
| 37–48 tháng | 4 tháng |
| 49–60 tháng | 5 tháng |
| 61–72 tháng | 6 tháng |
| Cứ thêm 12 tháng đóng | +1 tháng hưởng |
| Tối đa | **12 tháng** |

**Công thức:** Đóng 12–36 tháng = 3 tháng; sau đó cứ đóng thêm 12 tháng = +1 tháng hưởng (tối đa 12 tháng).

### 2.4 Ví Dụ Tính

**Case 1: Nhân viên văn phòng, đóng 3 năm (36 tháng), vùng I**
- Lương BQ 6 tháng cuối: 13 triệu
- TCTN/tháng = 60% × 13.000.000 = **7.800.000 đ**
- Thời gian: 36 tháng → **3 tháng**
- Tổng: 7.800.000 × 3 = **23.400.000 đ**

**Case 2: Công nhân, đóng 8 năm (96 tháng), vùng II**
- Lương BQ 6 tháng cuối: 8 triệu
- TCTN/tháng = 60% × 8.000.000 = **4.800.000 đ**
- Thời gian: 3 + (96−36)/12 = 3 + 5 = **8 tháng**
- Tổng: 4.800.000 × 8 = **38.400.000 đ**

**Case 3: Trưởng phòng, đóng 15 năm (180 tháng), vùng I, lương BQ 35 triệu**
- TCTN/tháng tính: 60% × 35.000.000 = 21.000.000
- Kiểm tra trần: 21.000.000 < 25.550.000 → **không vượt trần**
- Thời gian: 3 + (180−36)/12 = 3 + 12 = 15 → **tối đa 12 tháng**
- Tổng: 21.000.000 × 12 = **252.000.000 đ**

### 2.5 Bảng Ước Tính Nhanh

| Lương BQ 6 tháng cuối | TCTN/tháng | 3 tháng | 6 tháng | 12 tháng (tối đa) |
|----------------------|-----------|---------|---------|------------------|
| 8 triệu | 4.800.000 | 14.4 tr | 28.8 tr | 57.6 tr |
| 12 triệu | 7.200.000 | 21.6 tr | 43.2 tr | 86.4 tr |
| 15 triệu | 9.000.000 | 27 tr | 54 tr | 108 tr |
| 20 triệu | 12.000.000 | 36 tr | 72 tr | 144 tr |
| 30 triệu | 18.000.000 | 54 tr | 108 tr | 216 tr |

### 2.6 Hồ Sơ & Quy Trình BHTN

| STT | Giấy tờ | Ghi chú |
|-----|---------|---------|
| 1 | Đơn đề nghị hưởng TCTN | Mẫu tại Trung tâm DVVL |
| 2 | Sổ BHXH (bản chính) | Đã chốt sổ |
| 3 | HĐLĐ đã chấm dứt hoặc Quyết định thôi việc | Bản chính hoặc sao có xác nhận |
| 4 | CMND/CCCD | Bản sao |
| 5 | 2 ảnh 3×4 | Trong 6 tháng gần nhất |

**Nộp tại:** Trung tâm Dịch vụ Việc làm nơi cư trú (trong vòng 3 tháng từ ngày nghỉ)

**Lưu ý quan trọng:** Hàng tháng **BẮT BUỘC** đến Trung tâm DVVL thông báo tìm việc theo lịch hẹn. Không đến = bị tạm dừng trợ cấp tháng đó. 3 tháng liên tiếp không đến = chấm dứt.

### 2.7 Quyền Lợi Bổ Sung Khi Hưởng BHTN

| Quyền lợi | Chi tiết |
|-----------|---------|
| BHYT | Được cấp thẻ BHYT trong toàn bộ thời gian hưởng TCTN |
| Hỗ trợ tìm việc | Miễn phí qua Trung tâm DVVL |
| Đào tạo nghề | Hỗ trợ chi phí học nghề nếu đủ điều kiện |
| Tư vấn nghề | Miễn phí |

---

## Phần 3 — Tác Động Đến Thuế TNCN

### BHXH một lần và thuế

- **Tiền BHXH rút 1 lần** = **không phải thu nhập từ lao động** → **KHÔNG chịu thuế TNCN**
- Tuy nhiên nếu bao gồm **trợ cấp thôi việc vượt mức luật định** → phần vượt có thể chịu thuế

### BHTN và thuế

- **Trợ cấp thất nghiệp từ Quỹ BHTN nhà nước** → **KHÔNG chịu thuế TNCN** (thu nhập được miễn)
- Các trợ cấp do công ty tự chi trả (ngoài BHTN nhà nước) → có thể chịu thuế TNCN tùy cách cấu trúc

### BHXH cá nhân đóng và giảm trừ PIT

- Phần BHXH/BHYT/BHTN bắt buộc mà **cá nhân đóng** → được trừ khỏi thu nhập trước khi tính PIT
- Trần BHXH: **46.800.000 đ/tháng** → BHXH tối đa 3.744.000 đ/tháng
- Trần BHYT: **46.800.000 đ/tháng** → BHYT tối đa 702.000 đ/tháng
- Trần BHTN: theo vùng → Vùng I tối đa 106.200.000 × 1% = 1.062.000 đ/tháng
