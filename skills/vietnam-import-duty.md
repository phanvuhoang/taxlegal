---
name: vietnam-import-duty
version: 1.0.0
description: >
  Skill về thuế nhập khẩu Việt Nam: cơ cấu biểu thuế, thuế suất thông thường/ưu đãi/FTA,
  tính toán thuế NK, GTGT nhập khẩu, TTĐB nhập khẩu, các trường hợp miễn giảm thuế NK,
  và escalation path cho hàng hóa phức tạp.
category: customs
tags: [customs, import-duty, thue-nhap-khau, fta, hs-code, cif, vietnam, tariff]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế Nhập Khẩu Việt Nam

> **Căn cứ:** Luật Thuế XNK 107/2016/QH13, NĐ 134/2016/NĐ-CP (miễn giảm), NĐ 26/2023/NĐ-CP (Biểu thuế)

---

## Phần 1 — Cơ Cấu Thuế Suất Nhập Khẩu

### Ba loại thuế suất

| Loại thuế suất | Áp dụng cho | Ghi chú |
|---------------|------------|---------|
| **Thuế suất thông thường (MFN — Most Favored Nation)** | Hàng nhập từ các nước WTO (hoặc có hiệp định song phương) | Mức cơ bản |
| **Thuế suất ưu đãi đặc biệt (FTA rates)** | Hàng có C/O từ các nước trong FTA với VN | Thấp hơn MFN, tiến về 0% theo lộ trình |
| **Thuế suất thông thường (non-MFN)** | Hàng từ nước chưa có quan hệ thương mại đặc biệt | = 150% × MFN rate |

### Các FTA chủ yếu của Việt Nam (2026)

| Hiệp định | Đối tác | Ghi chú |
|----------|---------|---------|
| ATIGA | ASEAN 10 nước | Hầu hết về 0% hoặc rất thấp |
| VJEPA | Nhật Bản | Giảm mạnh hàng công nghiệp, nông sản |
| VKFTA | Hàn Quốc | Giảm mạnh hàng điện tử, nông sản |
| AKFTA | ASEAN + Hàn Quốc | |
| AJCEP | ASEAN + Nhật Bản | |
| AIFTA | ASEAN + Ấn Độ | Hạn chế hơn |
| EVFTA | EU 27 nước | Giảm mạnh hàng EU vào VN theo lộ trình |
| UKVFTA | Anh | Tương tự EVFTA |
| CPTPP | 11 nước (Nhật, Canada, Úc, Mexico...) | |
| RCEP | ASEAN + Trung Quốc, Nhật, Hàn, Úc, NZ | Hiệu lực từ 2022 |
| VIFTA | Israel | Hiệu lực từ 2024 |
| VCFTA | Chile | |

---

## Phần 2 — Công Thức Tính Thuế Nhập Khẩu

### Bước tính cơ bản

```
BƯỚC 1: Xác định HS Code (8 số)
BƯỚC 2: Tra thuế suất MFN và FTA (nếu có C/O)
BƯỚC 3: Tính Trị giá hải quan (CIF)
  CIF = Giá FOB + Phí bảo hiểm + Cước vận chuyển đến cảng VN
BƯỚC 4: Tính Thuế nhập khẩu
  Thuế NK = Trị giá HQ × Thuế suất NK
BƯỚC 5: Tính TTĐB (nếu hàng chịu TTĐB)
  Thuế TTĐB = (Trị giá HQ + Thuế NK) × Thuế suất TTĐB
BƯỚC 6: Tính Thuế GTGT nhập khẩu
  Thuế GTGT NK = (Trị giá HQ + Thuế NK + Thuế TTĐB) × Thuế suất GTGT
```

### Ví dụ tính thuế nhập khẩu

**Nhập khẩu máy tính xách tay từ Nhật (VJEPA):**
- CIF value: 1.000 USD = 25.000.000 đ (tỷ giá 25.000)
- HS Code: 8471.30.00 → Thuế MFN: 0% (đã về 0)
- C/O VJEPA: Thuế suất VJEPA = 0%
- Thuế NK = 25.000.000 × 0% = **0 đ**
- Thuế GTGT = 25.000.000 × 10% = **2.500.000 đ**
- **Tổng thuế = 2.500.000 đ**

**Nhập khẩu xe hơi phân khối < 2.0L từ Hàn Quốc (VKFTA):**
- CIF value: 25.000 USD = 625.000.000 đ (tỷ giá 25.000)
- HS Code: 8703.23.xx → Thuế MFN: 70%, VKFTA: 30% (giả định lộ trình)
- Áp dụng VKFTA (có C/O Form VK)
- Thuế NK = 625.000.000 × 30% = **187.500.000 đ**
- Thuế TTĐB (giả định 45%) = (625.000.000 + 187.500.000) × 45% = **365.625.000 đ**
- Thuế GTGT = (625.000.000 + 187.500.000 + 365.625.000) × 10% = **117.812.500 đ**
- **Tổng thuế = 670.937.500 đ**

---

## Phần 3 — Thuế Suất Phổ Biến (Tham Khảo, Tra Cứu Lại Biểu Thuế Hiện Hành)

> **LƯU Ý:** Thuế suất thay đổi theo lộ trình và đàm phán FTA. Luôn tra cứu biểu thuế chính thức tại thuongtruong.gdt.gov.vn trước khi tư vấn.

| Nhóm hàng | HS nhóm | Thuế MFN ước tính | Ghi chú |
|----------|---------|-------------------|---------|
| Điện thoại, linh kiện điện tử | 85.xx | 0–15% | Nhiều đã về 0% theo ITA |
| Máy tính, thiết bị IT | 84.xx, 84.71 | 0–10% | Hầu hết 0% theo ITA |
| Xe hơi nguyên chiếc | 87.03 | 60–80% | Tùy phân khối; ATIGA đã về 0% từ ASEAN |
| Xe máy | 87.11 | 45% | |
| Xăng dầu | 27.10 | 10–20% | + Thuế BVMT |
| Sắt thép | 72.xx | 10–25% | Biến động theo chính sách |
| Vải, may mặc | 50–63 | 10–30% | |
| Thực phẩm chế biến | 16–24 | 10–30% | |
| Máy móc công nghiệp | 84.xx | 0–10% | Nhiều mặt hàng miễn thuế NK |
| Dược phẩm | 30.xx | 0–5% | Thường rất thấp |
| Nguyên liệu dệt may (sợi, vải) | 52–56 | 0–12% | |

---

## Phần 4 — Miễn, Giảm Thuế Nhập Khẩu

### Các trường hợp miễn thuế phổ biến (NĐ 134/2016 sửa đổi NĐ 18/2021)

| Trường hợp | Điều kiện |
|-----------|-----------|
| **Hàng nhập để SXXK** | Sản xuất hàng xuất khẩu → miễn thuế NK nguyên liệu; hoàn thuế khi xuất |
| **Hàng gia công xuất khẩu** | Toàn bộ NL/VT nhập cho gia công xuất → miễn thuế NK |
| **Máy móc thiết bị tạo TSCĐ** | DN FDI hoặc DN dự án ưu đãi → miễn trong thời hạn ưu đãi |
| **Hàng nhập khẩu khu phi thuế quan (EPZ, FEZ)** | Từ nước ngoài vào khu → miễn thuế; từ khu ra nội địa → thu |
| **Nguyên liệu SX sản phẩm phần mềm** | Theo chính sách ưu đãi CNTT |
| **Hàng nhập khẩu trong mức miễn thuế** | Quà tặng, hành lý cá nhân trong định mức |
| **Hàng viện trợ không hoàn lại** | Theo quyết định cơ quan nhà nước |

### Miễn thuế nhập khẩu cho khu chế xuất (EPZ)

- Hàng từ **nước ngoài vào EPZ**: miễn thuế NK
- Hàng từ **nội địa vào EPZ**: coi như xuất khẩu (có thể hoàn GTGT)
- Hàng từ **EPZ ra nội địa**: coi như nhập khẩu (thu đủ thuế NK + GTGT + TTĐB)

---

## Phần 5 — Checklist Nhập Khẩu

- [ ] Xác định HS Code 8 chữ số chính xác
- [ ] Tra thuế suất MFN trên biểu thuế hiện hành (NĐ 26/2023 hoặc cập nhật)
- [ ] Kiểm tra C/O — loại C/O, nước xuất xứ, FTA phù hợp
- [ ] Tra thuế suất FTA theo hiệp định tương ứng (có thể thấp hơn nhiều)
- [ ] Tính CIF value chính xác (FOB + Insurance + Freight)
- [ ] Kiểm tra hàng có chịu TTĐB không
- [ ] Tính GTGT NK = (CIF + Thuế NK + TTĐB) × 10%
- [ ] Kiểm tra điều kiện miễn giảm (SXXK, gia công, FDI...)
- [ ] Kiểm tra hàng có cần giấy phép/kiểm tra chuyên ngành không
- [ ] Xác nhận phương thức nộp thuế (nộp ngay / bảo lãnh / ân hạn)
