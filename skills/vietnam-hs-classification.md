---
name: vietnam-hs-classification
version: 1.0.0
description: >
  Skill phân loại HS Code hàng hóa xuất nhập khẩu Việt Nam: cấu trúc biểu thuế HS,
  quy tắc phân loại GRI, các nhóm hàng phổ biến, tra cứu HS Code, xin phân loại
  trước (advance ruling), và rủi ro phân loại sai.
category: customs
tags: [customs, hs-code, phan-loai, tariff-classification, gri, vietnam, harmonized-system]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Phân Loại HS Code Hàng Hóa Xuất Nhập Khẩu

> **Căn cứ:** Công ước Harmonized System (HS Convention), Biểu thuế XNK VN (NĐ 26/2023/NĐ-CP)

---

## Phần 1 — Cấu Trúc HS Code Việt Nam

```
8471.30.00
├── 84: Chương (Chapter) — Lò phản ứng hạt nhân, nồi hơi, máy...
│   └── 8471: Nhóm (Heading) — Máy xử lý dữ liệu tự động...
│       └── 8471.30: Phân nhóm HS 6 số (theo HS quốc tế)
│           └── 8471.30.00: Phân nhóm VN 8 số (2 số thêm của VN)
```

- **Cấp 2 số (Chương):** 98 chương; 1–24 nông sản; 25–27 khoáng sản; 28–38 hóa chất; 39–40 nhựa/cao su; 41–43 da; 44–49 gỗ/giấy; 50–63 dệt may; 64–67 giày dép; 68–70 đá/thủy tinh; 72–83 kim loại; 84–85 máy móc điện tử; 86–89 giao thông; 90–92 quang học; 93 vũ khí; 94–96 đồ dùng; 97–98 tác phẩm nghệ thuật.
- **VN dùng hệ thống 8 chữ số** (HS 6 số quốc tế + 2 chữ số phân nhóm VN)

---

## Phần 2 — Quy Tắc Phân Loại GRI (6 Quy tắc)

### GRI 1: Tra nhóm trước

Phân loại theo tên nhóm (heading) và ghi chú chương/phần trước. Đây là quy tắc ưu tiên số 1.

### GRI 2: Mặt hàng chưa hoàn chỉnh và hỗn hợp

- GRI 2(a): Mặt hàng chưa hoàn chỉnh/chưa lắp ráp → phân loại như đã hoàn chỉnh (nếu có đặc trưng cơ bản)
- GRI 2(b): Hỗn hợp nguyên liệu → phân loại theo GRI 3

### GRI 3: Khi phân loại được vào 2+ nhóm

- GRI 3(a): Nhóm mô tả cụ thể nhất ưu tiên hơn nhóm chung
- GRI 3(b): Hỗn hợp/sản phẩm kết hợp → theo thành phần tạo nên đặc trưng cơ bản
- GRI 3(c): Nếu vẫn không phân biệt được → nhóm có số thứ tự cao nhất trong biểu thuế

### GRI 4: Hàng hóa không thuộc nhóm nào

Phân loại vào nhóm tương tự nhất.

### GRI 5: Hộp đựng và bao bì đặc biệt

Phân loại theo hàng hóa bên trong (nếu phù hợp đặc biệt cho mặt hàng đó).

### GRI 6: Phân nhóm

Áp dụng GRI 1–5 ở cấp phân nhóm (so sánh trong cùng mức phân nhóm).

---

## Phần 3 — Nhóm Hàng Phổ Biến

### Hàng điện tử & CNTT

| Mặt hàng | HS Code thông dụng |
|---------|---------------------|
| Điện thoại thông minh | 8517.12.xx |
| Máy tính xách tay | 8471.30.xx |
| Máy tính để bàn | 8471.41.xx hoặc 8471.49.xx |
| Linh kiện điện tử | 85.xx (tùy loại) |
| Máy in | 8443.3x.xx |
| Camera an ninh | 8525.80.xx |
| Pin lithium | 8507.60.xx |

### Hàng dệt may

| Mặt hàng | HS Code thông dụng |
|---------|---------------------|
| Vải cotton | 5208-5212 (tùy loại dệt và trọng lượng) |
| Áo T-shirt cotton | 6109.10.xx |
| Quần dài | 6203.4x.xx (nam) / 6204.6x.xx (nữ) |
| Giày da | 6403.xx.xx |

### Hàng nông sản & thực phẩm

| Mặt hàng | HS Code thông dụng |
|---------|---------------------|
| Gạo | 1006.xx.xx |
| Cà phê nhân | 0901.11.xx |
| Hạt điều chưa chế biến | 0801.31.xx |
| Tôm đông lạnh | 0306.xx.xx |
| Trái cây tươi | 08.xx |

### Máy móc & thiết bị

| Mặt hàng | HS Code thông dụng |
|---------|---------------------|
| Máy CNC | 8457.xx.xx hoặc 8458-8463 |
| Máy bơm | 8413.xx.xx |
| Động cơ điện | 8501.xx.xx |
| Biến thế | 8504.xx.xx |
| Xe nâng hàng | 8427.xx.xx |

---

## Phần 4 — Tra Cứu HS Code

### Nguồn tra cứu chính thức

| Nguồn | URL | Nội dung |
|-------|-----|---------|
| Cổng TCHQ | **customs.gov.vn** | Biểu thuế VN, danh mục |
| Thuế VN | **thuongtruong.gdt.gov.vn** | Tra HS Code, thuế suất |
| ECUS phần mềm | Phần mềm khai báo | Tra cứu nội bộ DN |
| WCO HS Database | **wcoomd.org** | Tham chiếu HS quốc tế |

### Quy trình tra cứu thực tế

```
1. Xác định bản chất hàng hóa (nguyên liệu? chế biến? máy móc? tiêu dùng?)
2. Tra theo chương phù hợp trong biểu thuế
3. Đọc ghi chú chương/phần (Notes) — thường loại trừ các mặt hàng đặc biệt
4. Tra nhóm (4 số) phù hợp nhất
5. Tra phân nhóm (6 số quốc tế, 8 số VN)
6. Đối chiếu với hàng đã khai báo trước đây nếu có
```

---

## Phần 5 — Advance Ruling (Phân Loại Trước)

### Khi nào cần advance ruling?

- Hàng hóa mới, chưa từng nhập/xuất
- HS Code đang tranh chấp với hải quan
- Giá trị lô hàng lớn, rủi ro phân loại sai cao
- Hàng hóa công nghệ mới (AI chips, thiết bị EV, sản phẩm y tế mới)

### Quy trình xin advance ruling

1. Nộp đơn đến **Tổng cục Hải quan** (không nộp tại chi cục)
2. Kèm: mô tả chi tiết hàng hóa, tài liệu kỹ thuật, catalog, mẫu hàng (nếu cần)
3. TCHQ trả lời trong **30 ngày** (phức tạp: 60 ngày)
4. Kết quả có giá trị ràng buộc cho **3 năm**

---

## Phần 6 — Rủi Ro Phân Loại Sai

### Hậu quả

| Lỗi | Hậu quả |
|-----|---------|
| Khai HS Code dẫn đến thuế suất thấp hơn thực tế | Truy thu thuế + lãi 0.03%/ngày |
| Khai nhầm HS Code được miễn thuế | Phạt + truy thu |
| Phân loại nhầm để hưởng FTA không đúng | Phạt + truy thu thuế FTA đã được ưu đãi |
| Cố ý khai sai | Phạt hành chính + truy cứu hình sự |

### Các HS Code dễ phân loại nhầm

| Trường hợp | Mô tả |
|-----------|-------|
| Phần mềm đóng gói vs. phần cứng | Phần mềm đóng gói = hàng hóa (HS 85.23); service = không phải hàng |
| Máy móc đa chức năng | Áp dụng GRI 3(b) — theo chức năng chính |
| Bộ phận vs. phụ kiện | Bộ phận (parts) thường thuế cao hơn phụ kiện |
| Thực phẩm chức năng vs. dược phẩm | Dược phẩm (Ch. 30) thường thuế thấp hơn thực phẩm |
| Vải dệt kim vs. vải dệt thoi | Khác nhóm 60 (dệt kim) vs. 50–58 (dệt thoi) |
