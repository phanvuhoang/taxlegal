---
name: tax-return
version: 1.0.0
description: >
  Vietnam tax return filing — CIT/VAT/PIT/FCT provisional and annual returns, deadlines,
  penalties for late filing and payment, e-tax platforms, and conservative defaults.
category: tax
tags: [tax-return, ke-khai-thue, deadline, cit, vat, pit, fct, penalty, etax, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Kê khai và Nộp thuế — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Luật quản lý thuế | 38/2019/QH14 | Luật gốc về quản lý thuế |
| Nghị định hướng dẫn | 126/2020/NĐ-CP | Hướng dẫn LQT 38 (kê khai, nộp thuế) |
| Thông tư hướng dẫn | 80/2021/TT-BTC | Hướng dẫn chi tiết NĐ126 |
| Xử phạt vi phạm hành chính | 125/2020/NĐ-CP | Mức phạt vi phạm thuế |
| Ưu đãi miễn/giảm phạt | 91/2022/NĐ-CP | Miễn giảm tiền phạt khi tự nguyện khai bổ sung |

## Lịch kê khai thuế tổng hợp

### Thuế Thu nhập Doanh nghiệp (CIT / TNDN)

| Loại tờ khai | Kỳ tính thuế | Hạn nộp tờ khai | Hạn nộp tiền |
|-------------|-------------|----------------|-------------|
| Tạm nộp quý (ước tính) | Quý | **30 ngày sau khi kết thúc quý** | Cùng ngày nộp tờ khai |
| Quyết toán năm | Năm tài chính | **90 ngày sau khi kết thúc năm** | Cùng ngày nộp tờ khai QT |
| Khai bổ sung | Khi phát hiện sai sót | 10 ngày kể từ ngày phát hiện | Ngay khi khai bổ sung |

**Quy tắc tạm nộp (từ NĐ 126/2020)**:
- Tổng số thuế CIT tạm nộp 3 quý đầu (Q1+Q2+Q3) phải ≥ **75% số thuế CIT phải nộp cả năm**
- Nếu tạm nộp < 75%: phạt tiền chậm nộp **0.03%/ngày** trên phần thiếu từ hạn nộp Q3 đến ngày nộp

**Ví dụ deadline năm tài chính 31/12:**
- Q1: hạn 30/04
- Q2: hạn 31/07
- Q3: hạn 31/10
- Q4 + Quyết toán: hạn 31/03 năm sau

### Thuế Giá trị Gia tăng (VAT / GTGT)

| Phương pháp kê khai | Điều kiện | Hạn nộp |
|--------------------|----------|---------|
| **Khai tháng** | Doanh thu năm trước ≥ VND 50 tỷ | Ngày **20** của tháng sau |
| **Khai quý** | Doanh thu năm trước < VND 50 tỷ | Ngày **30** của tháng đầu quý sau |
| **Khai theo lần phát sinh** | Dự án đầu tư; không phát sinh thường xuyên | 10 ngày kể từ ngày phát sinh |

**Đăng ký khai quý/tháng**: Thực hiện 1 lần và duy trì ít nhất 2 năm liên tiếp.

### Thuế Thu nhập Cá nhân (PIT / TNCN)

| Loại tờ khai | Điều kiện | Hạn nộp |
|-------------|----------|---------|
| Khấu trừ tháng | Tổ chức có số thuế khấu trừ ≥ VND 50 triệu/tháng | Ngày **20** tháng sau |
| Khấu trừ quý | Tổ chức có số thuế khấu trừ < VND 50 triệu/tháng | Ngày **30** tháng đầu quý sau |
| Quyết toán PIT của tổ chức trả thu nhập | Năm | **90 ngày** sau khi kết thúc năm dương lịch |
| Quyết toán PIT của cá nhân trực tiếp | Năm (nếu phải QT) | **90 ngày** sau khi kết thúc năm dương lịch |
| PIT khi kết thúc hợp đồng lao động | Khi nghỉ việc | 45 ngày kể từ ngày nghỉ |

**Các trường hợp cá nhân PHẢI trực tiếp quyết toán PIT:**
- Có số thuế phải nộp thêm > VND 50,000
- Có số thuế nộp thừa muốn hoàn
- Có thu nhập từ nhiều nơi trả

### Thuế Nhà thầu (FCT)

| Phương pháp | Hạn kê khai và nộp |
|------------|-------------------|
| PP1 (Bên VN khấu trừ nộp thay) | **10 ngày** kể từ ngày trả tiền cho nhà thầu |
| PP2/PP3 (Nhà thầu trực tiếp) | Theo lịch VAT/CIT thông thường |
| Quyết toán khi kết thúc hợp đồng | **45 ngày** kể từ ngày kết thúc hợp đồng |

## Chế độ phạt vi phạm hành chính thuế (NĐ 125/2020)

### Phạt chậm nộp tờ khai

| Vi phạm | Mức phạt |
|---------|---------|
| Nộp chậm 1–5 ngày (có tình tiết giảm nhẹ) | Cảnh cáo |
| Nộp chậm 1–30 ngày | VND **2,000,000** |
| Nộp chậm 31–60 ngày | VND **3,500,000** |
| Nộp chậm 61–90 ngày | VND **7,500,000** |
| Nộp chậm > 90 ngày (không phát sinh thuế) | VND **7,500,000** |
| Nộp chậm > 90 ngày (có phát sinh thuế) | VND **15,000,000** |
| Không nộp tờ khai | VND **7,500,000 – 15,000,000** |

### Phạt chậm nộp tiền thuế

```
Tiền chậm nộp = Số tiền thuế nộp chậm × 0.03%/ngày × Số ngày chậm
```

- Áp dụng từ ngày tiếp theo ngày hết hạn nộp thuế
- Không có tối đa — tích lũy theo số ngày thực tế
- Áp dụng cả khi đã nộp tờ khai đúng hạn nhưng nộp tiền chậm

**Ví dụ**: Nộp chậm thuế VND 100 triệu trong 30 ngày:
- Tiền chậm nộp = 100,000,000 × 0.03% × 30 = **VND 900,000**

### Phạt khai sai dẫn đến thiếu thuế

| Vi phạm | Mức phạt |
|---------|---------|
| Khai sai nhưng tự nguyện khai bổ sung trước thanh tra | Miễn phạt hành chính, chỉ nộp tiền chậm nộp |
| Khai sai bị phát hiện qua thanh tra | 20% số thuế thiếu |
| Trốn thuế (có hành vi gian lận) | 100–300% số thuế thiếu |

## Giảm nhẹ xử phạt — Tự nguyện khai bổ sung

**Theo Điều 133, LQT 38/2019 và NĐ 91/2022:**
- Khai bổ sung **trước khi CQT công bố quyết định thanh tra**: miễn toàn bộ phạt vi phạm hành chính, chỉ nộp tiền chậm nộp 0.03%/ngày
- Khai bổ sung **trong quá trình thanh tra** (trước khi có kết luận): giảm 50% mức phạt

## Nền tảng kê khai điện tử

| Công cụ | Mô tả | Phù hợp |
|---------|-------|---------|
| **HTKK** (Hỗ trợ kê khai) | Phần mềm desktop, lập tờ khai XML | Kế toán doanh nghiệp |
| **eTax** (Thuế điện tử) | Cổng web kê khai và nộp thuế | Tất cả đối tượng |
| **eTax Mobile** | App điện thoại | Cá nhân và hộ kinh doanh |
| **VNPT** / **Viettel** Invoice | Phần mềm hóa đơn điện tử (nhà cung cấp) | Hóa đơn điện tử |

**Địa chỉ cổng eTax**: https://thuedientu.gdt.gov.vn

## Nguyên tắc mặc định thận trọng (Conservative Defaults)

| Tình huống | Mặc định |
|-----------|---------|
| Không chắc chắn kỳ kê khai (tháng vs quý) | Kê khai theo **tháng** (hạn sớm hơn) |
| Không xác định được ngày kết thúc hợp đồng FCT | Coi như hợp đồng kết thúc từ lần thanh toán cuối |
| Chưa có số liệu tạm nộp CIT chính xác | Tạm nộp **ít nhất 80%** dự kiến để đảm bảo đạt 75% cả năm |
| Phát hiện sai sót trong kỳ trước | Khai bổ sung **ngay lập tức** trước khi CQT thanh tra |
| Deadline rơi vào ngày nghỉ/lễ | Nộp trước ngày làm việc liền trước ngày nghỉ |

## Checklist kê khai thuế tháng/quý

- [ ] VAT: Nộp tờ khai và tiền trước ngày 20 (tháng) hoặc ngày 30 (quý)
- [ ] PIT khấu trừ: Nộp cùng kỳ với VAT
- [ ] FCT (PP1): Nộp trong 10 ngày kể từ ngày trả tiền
- [ ] CIT tạm nộp quý: Tính tạm nộp, nộp trước ngày 30 sau khi kết thúc quý
- [ ] Kiểm tra tích lũy tạm nộp CIT có ≥ 75% ước tính cả năm không
- [ ] Đối chiếu dữ liệu hóa đơn điện tử với tờ khai VAT

## Checklist quyết toán thuế năm

- [ ] CIT quyết toán: Nộp trước ngày 31/03 (năm tài chính = năm dương lịch)
- [ ] PIT quyết toán (tổ chức): Nộp trước ngày 31/03
- [ ] PIT quyết toán (cá nhân): Nộp trước ngày 31/03 (nếu phải QT trực tiếp)
- [ ] Đối chiếu tổng tạm nộp CIT với số thuế thực tế → nộp bổ sung hoặc đề nghị hoàn
- [ ] Quyết toán FCT các hợp đồng kết thúc trong năm
- [ ] Lưu trữ toàn bộ tờ khai + biên lai + hồ sơ tối thiểu 10 năm
