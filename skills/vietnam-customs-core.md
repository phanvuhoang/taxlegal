---
name: vietnam-customs-core
version: 1.0.0
description: >
  Skill cốt lõi về hải quan Việt Nam: tổng quan hệ thống hải quan, cơ quan quản lý,
  quy trình khai báo hải quan điện tử VNACCS/VCIS, các loại tờ khai, và nguyên tắc
  cơ bản về trị giá hải quan, phân loại HS code và xuất xứ hàng hóa.
category: customs
tags: [customs, hai-quan, import, export, vnaccs, vcis, vietnam, ecus, declaration]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Hải Quan Việt Nam — Cốt Lõi

> **Căn cứ:** Luật Hải quan 54/2014/QH13 (sửa đổi 71/2022/QH15), Luật Thuế XNK 107/2016/QH13, NĐ 134/2016/NĐ-CP (sửa đổi NĐ 18/2021/NĐ-CP)

---

## Phần 1 — Cơ Quan Quản Lý & Hệ Thống

| Cơ quan | Chức năng |
|---------|---------|
| **Tổng cục Hải quan** (TCHQ) | Cơ quan trung ương; ban hành chính sách, giám sát |
| **Cục Hải quan tỉnh/TP** | Quản lý theo địa lý; phân công cho chi cục |
| **Chi cục Hải quan cửa khẩu** | Trực tiếp thông quan, kiểm tra hàng hóa |
| **VNACCS/VCIS** | Hệ thống khai báo hải quan điện tử tích hợp |

### Hệ thống khai báo điện tử VNACCS

- **VNACCS** (Vietnam Automated Cargo Clearance System): Khai báo thông quan tự động
- **VCIS** (Vietnam Customs Intelligence Information System): Hệ thống thông tin nghiệp vụ
- **ECUS** phần mềm phổ biến được các doanh nghiệp dùng để khai báo hải quan

**Quy trình phân luồng:**
- **Luồng Xanh:** Thông quan ngay, không kiểm tra thực tế
- **Luồng Vàng:** Kiểm tra hồ sơ giấy tờ (không kiểm thực tế hàng)
- **Luồng Đỏ:** Kiểm tra thực tế hàng hóa (mở container, lấy mẫu...)

---

## Phần 2 — Các Loại Tờ Khai Hải Quan

| Loại tờ khai | Mã | Sử dụng khi |
|-------------|----|----|
| Nhập khẩu thương mại | A11, A12 | Hàng nhập kinh doanh thông thường |
| Xuất khẩu thương mại | B11, B12, B13 | Hàng xuất kinh doanh, bao thanh toán |
| Nhập khẩu gia công | E11, E15 | Nguyên liệu nhập về gia công xuất khẩu |
| Xuất khẩu gia công | E21 | Hàng gia công xuất trả |
| Tạm nhập tái xuất | G11, G12 | Nhập tạm thời, hàng mượn |
| Tạm xuất tái nhập | G21 | Xuất máy móc đi sửa, dự hội chợ |
| Nhập sản xuất xuất khẩu (SXXK) | E31, E52 | Hàng nhập để SX hàng xuất khẩu |
| Kho ngoại quan | H11, H12 | Hàng gửi kho ngoại quan |

---

## Phần 3 — Quy Trình Thông Quan Cơ Bản

```
Bước 1: Chuẩn bị hồ sơ hải quan
  ↓
Bước 2: Khai báo tờ khai điện tử qua VNACCS (phân luồng tự động)
  ↓
Bước 3: Nộp thuế (nếu có) — trước hoặc sau thông quan tùy loại
  ↓
Bước 4: Kiểm tra (theo luồng xanh/vàng/đỏ)
  ↓
Bước 5: Thông quan — nhận hàng hoặc xuất hàng
  ↓
Bước 6: Lưu hồ sơ (5 năm theo quy định)
```

### Hồ sơ hải quan cơ bản

| Loại hồ sơ | Bắt buộc |
|-----------|---------|
| Tờ khai hải quan điện tử | ✅ |
| Hóa đơn thương mại (Commercial Invoice) | ✅ |
| Phiếu đóng gói (Packing List) | ✅ |
| Vận đơn (Bill of Lading/Airway Bill) | ✅ |
| Giấy chứng nhận xuất xứ (C/O) | Khi hưởng ưu đãi FTA |
| Giấy phép nhập/xuất khẩu | Khi hàng có điều kiện |
| Tờ khai trị giá | Khi giá trị > ngưỡng quy định |
| Kết quả kiểm tra chuyên ngành | Theo từng loại hàng |

---

## Phần 4 — Nguyên Tắc Cơ Bản

### 4.1 Trị giá hải quan (Customs Valuation)

**Phương pháp ưu tiên:** Trị giá giao dịch (Transaction Value) = Giá CIF (Cost + Insurance + Freight) tại cửa khẩu nhập VN.

```
Trị giá hải quan = Giá mua (FOB) + Phí bảo hiểm + Cước vận chuyển đến cửa khẩu VN
```

**6 phương pháp thay thế** (theo thứ tự nếu không áp dụng được phương pháp trước):
1. Trị giá giao dịch hàng giống hệt
2. Trị giá giao dịch hàng tương tự
3. Trị giá khấu trừ
4. Trị giá tính toán
5. Suy luận từ 4 phương pháp trên

> **Lưu ý:** Nếu giá khai báo thấp hơn đáng kể so với giá thị trường, hải quan có thể nghi vấn và yêu cầu bổ sung chứng từ hoặc ấn định trị giá.

### 4.2 Phân loại HS Code

- **HS Code** (Harmonized System Code): Mã phân loại hàng hóa quốc tế
- VN dùng **Biểu thuế xuất nhập khẩu** (ban hành theo NĐ 26/2023/NĐ-CP, cập nhật hàng năm)
- HS Code VN: 8 chữ số (6 chữ số quốc tế + 2 chữ số VN)
- Tra cứu: **thuongtruong.gdt.gov.vn** hoặc phần mềm hải quan

> **Nguyên tắc:** Phân loại sai HS Code → áp dụng sai thuế suất → rủi ro bị truy thu + phạt.

### 4.3 Xuất xứ hàng hóa

| Loại C/O | Hiệp định | Ưu đãi thuế |
|---------|-----------|------------|
| C/O Form D | ATIGA (ASEAN) | ≤ 0–5% |
| C/O Form AK | AKFTA (ASEAN-Hàn Quốc) | Giảm đáng kể |
| C/O Form AJ | AJCEP (ASEAN-Nhật Bản) | Giảm đáng kể |
| C/O Form AI | AIFTA (ASEAN-Ấn Độ) | Giảm một số dòng |
| C/O Form VJ | VJEPA (VN-Nhật Bản) | Giảm đáng kể |
| C/O Form VC | VCFTA (VN-Chile) | Giảm theo lộ trình |
| C/O Form VK | VKFTA (VN-Hàn Quốc) | Giảm đáng kể |
| C/O Form EUR.1 / REX | EVFTA (VN-EU) | Giảm mạnh |
| C/O Form UKVFTA | VN-Anh | Giảm theo lộ trình |
| C/O Form VN-CL/... | CPTPP | Giảm theo lộ trình |

---

## Phần 5 — Thuế Xuất Nhập Khẩu — Tổng Quan

### Các loại thuế liên quan đến nhập khẩu

```
Tổng chi phí thuế khi nhập khẩu =
  + Thuế nhập khẩu (nếu có)
  + Thuế GTGT nhập khẩu (hầu hết 10%, 5% một số mặt hàng)
  + Thuế tiêu thụ đặc biệt (nếu có — rượu, bia, thuốc lá, xe hơi...)
  + Thuế bảo vệ môi trường (nếu có — xăng dầu, túi nilon...)
  + Phí kiểm định/kiểm dịch (nếu có)
```

### Luồng tính thuế nhập khẩu

```
1. Xác định HS Code → Tra thuế suất NK
2. Kiểm tra C/O và FTA → Áp dụng thuế suất ưu đãi (nếu đủ điều kiện)
3. Tính thuế NK = Trị giá hải quan (CIF) × Thuế suất NK
4. Tính thuế GTGT NK = (Trị giá HQ + Thuế NK + TTĐB nếu có) × 10%
5. Tổng thuế phải nộp = Thuế NK + GTGT NK + TTĐB (nếu có)
```

---

## Phần 6 — Anti-Hallucination Rules Hải Quan

1. **HS Code:** KHÔNG suy đoán HS Code nếu mô tả hàng hóa không rõ ràng → hỏi thêm hoặc flag.
2. **Thuế suất:** Tra cứu Biểu thuế hiện hành (năm 2026 theo NĐ hiện hành) — không dùng số nhớ từ năm cũ.
3. **FTA:** Chỉ áp thuế suất FTA khi có C/O hợp lệ — không chỉ dựa vào nước xuất xứ.
4. **Trị giá:** Phải dùng trị giá giao dịch thực tế; không tự ước tính.
5. **Kiểm tra chuyên ngành:** Nhiều mặt hàng cần kiểm dịch, kiểm định trước khi thông quan → flag.
6. **Giấy phép:** Hàng cấm, hàng hạn chế nhập — PHẢI kiểm tra danh mục trước.
7. **Escalate:** Ấn định trị giá, phân loại HS tranh chấp, origin verification → escalate chuyên gia.
