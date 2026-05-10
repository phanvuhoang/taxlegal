---
name: pit-2026-core
version: 1.0.0
description: >
  Skill cốt lõi về thuế Thu nhập Cá nhân (TNCN/PIT) theo Luật 109/2025/QH15 — áp dụng từ
  01/01/2026. Bao gồm biểu thuế 5 bậc mới, giảm trừ gia cảnh nâng lên, ngưỡng miễn thuế HKD
  1 tỷ, và bãi bỏ thuế khoán. Bổ sung cho vietnam-pit.md (không lặp lại quy trình kê khai cơ bản).
category: tax
tags: [pit, tncn, 2026, luat-109, vietnam, personal-income-tax, progressive-tax]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế TNCN 2026 — Cốt lõi (Luật 109/2025/QH15)

> **Phiên bản pháp lý:** Luật Thuế TNCN sửa đổi — Luật số 109/2025/QH15
> **Hiệu lực:** 01/01/2026
> **Nguồn bổ sung:** NQ 110/2025/UBTVQH15 (giảm trừ), NĐ 141/2026/NĐ-CP (ngưỡng HKD), NQ 198/2025/QH15 (bãi bỏ thuế khoán)

---

## Phần 1 — Biểu Thuế Lũy Tiến 2026

### Biểu thuế 5 bậc (Luật 109/2025/QH15)

| Bậc | Thu nhập tính thuế/tháng | Thuế suất | Công thức rút gọn |
|-----|--------------------------|-----------|-------------------|
| 1 | ≤ 10.000.000 đ | 5% | TN × 5% |
| 2 | 10.000.001 – 30.000.000 đ | 10% | TN × 10% − 500.000 |
| 3 | 30.000.001 – 60.000.000 đ | 20% | TN × 20% − 3.500.000 |
| 4 | 60.000.001 – 100.000.000 đ | 30% | TN × 30% − 9.500.000 |
| 5 | > 100.000.000 đ | 35% | TN × 35% − 14.500.000 |

> **Lưu ý so với biểu cũ (7 bậc):** Luật 109 gộp bậc 1 (0–5tr) và bậc 2 (5–10tr) thành 1 bậc duy nhất 5%, rút bậc 35% xuống ngưỡng >100 triệu/tháng.

### Cách tính nhanh (Thu nhập tính thuế đã trừ giảm trừ)

```
Thu nhập tính thuế (TNTT) = Thu nhập chịu thuế − Giảm trừ bản thân − Giảm trừ NPT − BHXH/BHYT/BHTN cá nhân đóng − Các khoản giảm trừ khác

Thuế TNCN = TNTT × Thuế suất − Số tiền trừ (công thức rút gọn)
```

### Ví dụ tính thuế 2026

**Ví dụ 1: Nhân viên, lương gross 25 triệu, không NPT**
- BHXH: 25.000.000 × 8% = 2.000.000
- BHYT: 25.000.000 × 1.5% = 375.000
- BHTN: 25.000.000 × 1% = 250.000
- Thu nhập chịu thuế = 25.000.000 − 2.000.000 − 375.000 − 250.000 = 22.375.000
- TNTT = 22.375.000 − 15.500.000 (bản thân) = **6.875.000**
- Thuế = 6.875.000 × 5% = **343.750 đ/tháng**

**Ví dụ 2: Manager, lương 60 triệu, 2 NPT**
- BHXH: 46.800.000 × 8% = 3.744.000 (trần BHXH 46.8 triệu)
- BHYT: 46.800.000 × 1.5% = 702.000
- BHTN: 60.000.000 × 1% = 600.000 (trần theo vùng — kiểm tra)
- Thu nhập chịu thuế = 60.000.000 − 3.744.000 − 702.000 − 600.000 = 54.954.000
- Giảm trừ: 15.500.000 + 2 × 6.200.000 = 27.900.000
- TNTT = 54.954.000 − 27.900.000 = **27.054.000**
- Thuế = 27.054.000 × 10% − 500.000 = **2.205.400 đ/tháng**

**Ví dụ 3: Senior Manager, lương 120 triệu, 1 NPT**
- BHXH trần: 46.800.000 × 8% = 3.744.000
- BHYT trần: 46.800.000 × 1.5% = 702.000
- BHTN Vùng I: 106.200.000 × 1% = 1.062.000
- Thu nhập chịu thuế = 120.000.000 − 3.744.000 − 702.000 − 1.062.000 = 114.492.000
- Giảm trừ: 15.500.000 + 6.200.000 = 21.700.000
- TNTT = 114.492.000 − 21.700.000 = **92.792.000**
- Thuế = 92.792.000 × 30% − 9.500.000 = **18.337.600 đ/tháng**

---

## Phần 2 — Giảm Trừ Gia Cảnh 2026

### Mức giảm trừ (NQ 110/2025/UBTVQH15)

| Loại giảm trừ | Mức/tháng | Mức/năm |
|--------------|-----------|---------|
| Giảm trừ bản thân | **15.500.000 đ** | 186.000.000 đ |
| Giảm trừ mỗi người phụ thuộc (NPT) | **6.200.000 đ** | 74.400.000 đ |

> **Thay đổi so với 2025:** Tăng từ 11.000.000 → 15.500.000 (bản thân) và 4.400.000 → 6.200.000 (NPT) theo NQ 110/2025.

### Điều kiện đăng ký NPT

**Đăng ký lần đầu:** Nộp Mẫu 12/ĐK-TNCN kèm hồ sơ chứng minh (khai sinh, hôn thú, CCCD...)
**Deadline hồi tố:** Đăng ký trước 31/12 năm tính thuế để áp dụng từ đầu năm đó
**Mỗi NPT:** chỉ được 1 người khai trừ; không được khai đồng thời ở 2 người

### Các khoản được trừ khác

| Khoản | Điều kiện | Giới hạn |
|-------|-----------|---------|
| Đóng góp từ thiện, nhân đạo, khuyến học | Có hóa đơn/chứng từ hợp lệ | Không vượt TNCT sau giảm trừ gia cảnh |
| BHXH bắt buộc | 8% lương (trần 46.8 triệu) | Theo thực tế |
| BHYT bắt buộc | 1.5% lương (trần 46.8 triệu) | Theo thực tế |
| BHTN bắt buộc | 1% lương (trần theo vùng) | Theo thực tế |
| BHNN đặc thù | Theo quy định ngành | Theo thực tế |
| Bảo hiểm nhân thọ (tuỳ chọn) | HĐ ký từ 2022 trở đi | Tối đa 1.000.000 đ/tháng |

---

## Phần 3 — BHXH/BHYT/BHTN Trần 2026

### Trần đóng bảo hiểm bắt buộc

| Loại | Trần đóng | Tỷ lệ NLĐ | BHXH tháng tối đa |
|------|-----------|-----------|-------------------|
| BHXH | 46.800.000 đ/tháng (20 × lương cơ sở 2.340.000) | 8% | 3.744.000 đ |
| BHYT | 46.800.000 đ/tháng | 1.5% | 702.000 đ |
| BHTN | Vùng I: 106.200.000 / Vùng II: 94.600.000 / Vùng III: 82.600.000 / Vùng IV: 74.400.000 | 1% | Tùy vùng |

> **Lưu ý:** Phần lương vượt trần vẫn là thu nhập chịu TNCN nhưng KHÔNG đóng BHXH.

---

## Phần 4 — Ngưỡng Miễn Thuế Hộ Kinh Doanh (HKD)

### Quy định mới (NĐ 141/2026/NĐ-CP)

| Nội dung | Quy định |
|----------|---------|
| **Ngưỡng miễn thuế** | Doanh thu ≤ **1.000.000.000 đ/năm** |
| Áp dụng từ | 01/01/2026 |
| Đối tượng | Hộ kinh doanh, cá nhân kinh doanh |
| Căn cứ | NĐ 141/2026/NĐ-CP hướng dẫn Luật 109/2025 |

**HKD có doanh thu > 1 tỷ:** Phải kê khai và nộp thuế TNCN (và thuế GTGT) trên toàn bộ doanh thu.

### Bãi bỏ thuế khoán (NQ 198/2025/QH15 — hiệu lực 01/01/2026)

> **QUAN TRỌNG:** Chế độ thuế khoán (lump-sum tax) cho HKD **ĐÃ BỊ BÃI BỎ** từ 01/01/2026.
> - Các HKD trước đây nộp thuế khoán nay phải chuyển sang kê khai thực tế (NQ 68/2026/NĐ-CP + TT 18/2026/TT-BTC)
> - HKD doanh thu ≤ 1 tỷ: miễn thuế TNCN (vẫn phải đăng ký kinh doanh nếu theo quy định)
> - HKD doanh thu > 1 tỷ: kê khai thuế TNCN + GTGT theo phương pháp trực tiếp

---

## Phần 5 — Thuế Suất theo Loại Thu Nhập

### Bảng tổng hợp thuế suất 2026

| Loại thu nhập | Thuế suất | Kê khai |
|---------------|-----------|---------|
| Tiền lương, tiền công (cư trú) | Biểu lũy tiến 5–35% | Hàng tháng/quý + quyết toán năm |
| Tiền lương, tiền công (không cư trú) | 20% flat | Khấu trừ tại nguồn |
| Thu nhập từ đầu tư vốn (cổ tức, lãi vay) | 5% | Khấu trừ tại nguồn |
| Chuyển nhượng vốn (cổ phần, vốn góp) | 20% trên lợi nhuận hoặc 0.1% giá chuyển nhượng | Theo từng lần |
| Chuyển nhượng bất động sản | 2% giá chuyển nhượng | Mỗi lần chuyển nhượng |
| Thu nhập từ bản quyền | 5% phần vượt 10 triệu | Khấu trừ tại nguồn |
| Thu nhập từ nhượng quyền thương mại | 5% phần vượt 10 triệu | Khấu trừ tại nguồn |
| Thu nhập từ trúng thưởng | 10% phần vượt 10 triệu | Khấu trừ tại nguồn |
| Thu nhập từ thừa kế, quà tặng | 10% phần vượt 10 triệu | Kê khai nộp |
| Thu nhập từ kinh doanh (cá nhân KD) | Tỷ lệ theo ngành × doanh thu | Kê khai hàng quý/năm |

### Tỷ lệ thuế thu nhập từ kinh doanh cá nhân (theo ngành)

| Ngành nghề | Tỷ lệ TNCN | Tỷ lệ GTGT |
|-----------|------------|------------|
| Phân phối, cung cấp hàng hóa | 0.5% | 1% |
| Dịch vụ, xây dựng (không bao thầu NVL) | 2% | 5% |
| Sản xuất, vận tải, dịch vụ có gắn hàng hóa, xây dựng có bao thầu NVL | 1.5% | 3% |
| Hoạt động khác | 1% | 2% |
| KOL/Content Creator/Tư vấn/IT Freelancer | 2% (dịch vụ) | 5% |

---

## Phần 6 — Anti-Hallucination Rules

> **BẮT BUỘC:** Tuân thủ 8 nguyên tắc sau trước khi đưa ra bất kỳ con số nào.

1. **Biểu thuế:** Luôn dùng biểu 2026 (5 bậc). KHÔNG dùng biểu 7 bậc cũ.
2. **Giảm trừ:** Bản thân **15.500.000**, NPT **6.200.000**. KHÔNG dùng số cũ (11tr/4.4tr).
3. **Trần BHXH:** **46.800.000** (= 20 × 2.340.000 lương cơ sở 2026). KHÔNG dùng trần cũ.
4. **Ngưỡng HKD:** **1 tỷ/năm** từ 01/01/2026. Thuế khoán **ĐÃ BỊ BÃI BỎ**.
5. **Cư trú vs không cư trú:** Flat 20% chỉ áp dụng KHÔNG cư trú; cư trú dùng biểu lũy tiến.
6. **Không suy đoán:** Nếu chưa có thông tin (số NPT, vùng lương tối thiểu...) → hỏi thêm.
7. **Escalate:** Thu nhập từ equity, chuyển nhượng BĐS, thuế quốc tế → flag chuyển chuyên gia.
8. **Disclaimer:** Mọi tính toán chỉ mang tính tham khảo, cần xác nhận với chuyên gia thuế có chứng chỉ.

---

## Phần 7 — Checklist Tính Thuế (8 Bước)

- [ ] 1. Xác định loại thu nhập (tiền lương / kinh doanh / đầu tư / chuyển nhượng...)
- [ ] 2. Xác định tư cách cư trú thuế (cư trú / không cư trú)
- [ ] 3. Xác định kỳ tính thuế (tháng / quý / năm / từng lần)
- [ ] 4. Tổng hợp thu nhập chịu thuế (gộp tất cả nguồn nếu quyết toán năm)
- [ ] 5. Tính trừ BHXH/BHYT/BHTN cá nhân đóng (theo trần)
- [ ] 6. Áp dụng giảm trừ gia cảnh (bản thân 15.5tr + NPT 6.2tr/người)
- [ ] 7. Áp dụng các khoản giảm trừ khác (từ thiện, bảo hiểm nhân thọ...)
- [ ] 8. Tính thuế theo biểu lũy tiến 5 bậc hoặc thuế suất tương ứng

---

## Căn Cứ Pháp Lý

| Văn bản | Nội dung |
|---------|----------|
| Luật số 109/2025/QH15 | Sửa đổi Luật Thuế TNCN — biểu thuế 5 bậc, giảm trừ mới |
| NQ 110/2025/UBTVQH15 | Mức giảm trừ gia cảnh: 15.5tr/6.2tr |
| NĐ 141/2026/NĐ-CP | Ngưỡng miễn thuế HKD 1 tỷ/năm |
| NQ 198/2025/QH15 | Bãi bỏ chế độ thuế khoán từ 01/01/2026 |
| NĐ 68/2026/NĐ-CP | Hướng dẫn HKD/CNKD theo quy định mới |
| TT 18/2026/TT-BTC | Hướng dẫn kê khai HKD sau khi bãi bỏ thuế khoán |
| TT 111/2013/TT-BTC | Hướng dẫn Luật Thuế TNCN (vẫn có hiệu lực phần không mâu thuẫn) |
| NĐ 293/2025/NĐ-CP | Lương tối thiểu vùng 2026 (dùng tính trần BHTN) |
