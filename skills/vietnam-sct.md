---
name: vietnam-sct
version: 1.0.0
description: >
  Vietnam Special Consumption Tax (SCT) — excise tax on luxury and restricted goods and services.
  Covers SCT Law 27/2008, taxable goods/services, rate tables, price calculation, export exemption,
  and input SCT offset mechanism.
category: tax
tags: [sct, ttdb, special-consumption-tax, excise-tax, vietnam, luxury-tax]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế Tiêu thụ Đặc biệt (SCT/TTĐB) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Luật TTĐB | 27/2008/QH12 (sửa 70/2014, 106/2016) | Luật gốc |
| Nghị định hướng dẫn | 108/2015/NĐ-CP (sửa 14/2019/NĐ-CP) | Hướng dẫn tổng quát |
| Thông tư hướng dẫn | 195/2015/TT-BTC (sửa 20/2017/TT-BTC) | Hướng dẫn chi tiết |
| Luật sửa đổi 2024 | 56/2024/QH15 | Tăng thuế rượu bia, thuốc lá từ 2026 |

## Hàng hóa, dịch vụ chịu thuế TTĐB

### Nhóm hàng hóa

| Nhóm | Hàng hóa cụ thể | Thuế suất |
|------|----------------|-----------|
| Thuốc lá | Điếu thuốc, xì gà, thuốc lá khác | **75%** |
| Rượu | Rượu từ 20 độ trở lên | **65%** |
| Rượu nhẹ | Rượu dưới 20 độ | **35%** |
| Bia | Bia chai, bia lon, bia hơi | **65%** |
| Ô tô | Xe dưới 9 chỗ ngồi, dung tích ≤ 1.5L | **35%** |
| Ô tô | Xe dưới 9 chỗ ngồi, dung tích 1.5L–2.0L | **40%** |
| Ô tô | Xe dưới 9 chỗ ngồi, dung tích 2.0L–2.5L | **50%** |
| Ô tô | Xe dưới 9 chỗ ngồi, dung tích 2.5L–3.0L | **60%** |
| Ô tô | Xe dưới 9 chỗ ngồi, dung tích > 3.0L | **150%** |
| Xe điện | Xe điện dưới 9 chỗ (ưu đãi giai đoạn 2022–2027) | **3%** |
| Xe máy | Xe máy ≥ 125cc | **20%** |
| Điều hòa | Điều hòa không khí ≤ 90.000 BTU | **10%** |
| Bài lá | Bài lá (playing cards) | **40%** |
| Vàng mã | Vàng mã, hàng mã (votive paper goods) | **70%** |
| Xăng | Xăng các loại | **10%** |
| Máy bay | Tàu bay | **30%** |
| Du thuyền | Du thuyền (yachts) | **30%** |

### Nhóm dịch vụ

| Dịch vụ | Thuế suất |
|---------|-----------|
| Kinh doanh vũ trường | **40%** |
| Kinh doanh mát-xa, karaoke | **30%** |
| Kinh doanh casino, trò chơi điện tử có thưởng | **35%** |
| Kinh doanh đặt cược (betting) | **30%** |
| Kinh doanh golf (phí thành viên, vé vào chơi) | **20%** |
| Kinh doanh xổ số | **15%** |

## Giá tính thuế TTĐB

### Công thức cơ bản

**Đối với hàng hóa sản xuất trong nước:**

```
Giá tính TTĐB = Giá bán của cơ sở sản xuất / (1 + Thuế suất TTĐB)
```

**Lưu ý**: Giá bán của cơ sở sản xuất là giá bán cho đại lý/khách hàng đầu tiên, KHÔNG bao gồm VAT và TTĐB.

**Ví dụ tính toán (bia, thuế suất 65%):**
- Giá bán xuất xưởng (đã có TTĐB): 100,000 VND
- Giá tính TTĐB = 100,000 / (1 + 65%) = 100,000 / 1.65 = **60,606 VND**
- TTĐB = 60,606 × 65% = **39,394 VND**

**Đối với hàng hóa nhập khẩu:**

```
Giá tính TTĐB = Giá CIF + Thuế nhập khẩu
TTĐB = Giá tính TTĐB × Thuế suất TTĐB
```

**Đối với dịch vụ:**

```
Giá tính TTĐB = Doanh thu của cơ sở kinh doanh dịch vụ / (1 + Thuế suất TTĐB)
```

## Trường hợp không chịu/miễn TTĐB

| Trường hợp | Căn cứ pháp lý |
|-----------|----------------|
| Hàng hóa xuất khẩu (có chứng từ XK hợp lệ) | Điều 3, Luật TTĐB 27/2008 |
| Hàng hóa nhập khẩu từ nước ngoài bán cho tổ chức miễn thuế | Điều 3 |
| Hàng bay tàu bay, tàu biển cung ứng cho vận chuyển quốc tế | Điều 3 |
| Xe chuyên dụng phục vụ quốc phòng, an ninh | Điều 3 |
| Điều hòa lắp đặt trên phương tiện vận tải | Điều 5, NĐ108 |

## Cơ chế khấu trừ thuế TTĐB đầu vào

**Nguyên tắc**: Cơ sở sản xuất hàng chịu TTĐB được khấu trừ TTĐB đã nộp ở khâu trước nếu nguyên liệu đầu vào cũng chịu TTĐB.

**Điều kiện khấu trừ (Điều 8, Luật TTĐB):**
1. Nguyên liệu đầu vào đã nộp TTĐB
2. Nguyên liệu mua từ cơ sở sản xuất trong nước (không áp dụng với nhập khẩu)
3. Có hóa đơn GTGT và chứng từ thanh toán hợp lệ
4. Nguyên liệu thực tế đã sử dụng để sản xuất ra hàng hóa chịu TTĐB

**Ví dụ**: Nhà máy sản xuất rượu mua đường chịu TTĐB → được khấu trừ TTĐB của đường đã nộp khi tính TTĐB của rượu.

**Công thức khấu trừ:**
```
TTĐB phải nộp = TTĐB của hàng bán ra − TTĐB đã nộp ở nguyên liệu đầu vào tương ứng
```

## Kê khai và nộp thuế TTĐB

| Tờ khai | Kỳ tính thuế | Hạn nộp |
|---------|-------------|---------|
| Tờ khai tháng | Tháng dương lịch | Ngày 20 tháng sau |
| Tờ khai hàng hóa nhập khẩu | Từng lần nhập khẩu | Cùng thời điểm nộp thuế NK |

## Nguyên tắc mặc định thận trọng (Conservative Defaults)

| Tình huống | Mặc định |
|-----------|---------|
| Không xác định được dung tích xe ô tô | Áp dụng mức thuế cao hơn |
| Hàng hóa vừa có thể chịu/không chịu TTĐB | Coi là chịu TTĐB và tính thuế |
| Xuất khẩu nhưng chứng từ chưa đủ | Chưa khấu trừ/hoàn thuế cho đến khi có đủ hồ sơ |
| Nguyên liệu đầu vào nghi vấn đã nộp TTĐB | Không khấu trừ cho đến khi xác minh |
| Dịch vụ kết hợp (ví dụ: sân golf + nhà hàng) | Tách doanh thu từng hoạt động; nếu không tách được → áp dụng mức cao nhất |

## Checklist thực hành SCT/TTĐB

- [ ] Xác định hàng hóa/dịch vụ có thuộc đối tượng chịu TTĐB không
- [ ] Xác định đúng mức thuế suất theo loại và đặc điểm kỹ thuật
- [ ] Tính giá tính TTĐB theo công thức đúng (chia cho 1 + thuế suất)
- [ ] Kiểm tra điều kiện miễn/không chịu TTĐB (đặc biệt hàng xuất khẩu)
- [ ] Xác định có nguyên liệu đầu vào đã nộp TTĐB cần khấu trừ không
- [ ] Kê khai tháng đúng hạn (ngày 20 tháng sau)
- [ ] Lưu hồ sơ: hóa đơn đầu vào, chứng từ xuất khẩu, bảng phân bổ nguyên liệu
