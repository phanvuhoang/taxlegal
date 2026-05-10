---
name: pit-expat-nonresident
version: 1.0.0
description: >
  Skill chuyên về thuế TNCN người nước ngoài tại Việt Nam: quy tắc 183 ngày, flat 20%
  không cư trú, gross-up net salary, phúc lợi expat miễn thuế/chịu thuế, DTA credit,
  equity xuyên biên giới, và quyết toán trước khi rời Việt Nam. Theo Luật 109/2025.
category: tax
tags: [pit, tncn, expat, foreigner, non-resident, 183-day, gross-up, flat-20, dta, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế TNCN Người Nước Ngoài & Không Cư Trú

> **Căn cứ:** Luật Thuế TNCN (sửa đổi Luật 109/2025), TT 111/2013, TT 10/2022/TT-BTC

---

## Phần 1 — Quy Tắc 183 Ngày (Xác định Cư trú)

### Hai tiêu chí xác định cư trú thuế

| Tiêu chí | Điều kiện | Ghi chú |
|---------|-----------|---------|
| **Tiêu chí 1** | Có mặt tại VN ≥ 183 ngày trong **năm dương lịch** (1/1–31/12) | Cộng dồn tất cả ngày có mặt |
| **Tiêu chí 2** | Có mặt tại VN ≥ 183 ngày trong **12 tháng liên tục** kể từ ngày đến VN lần đầu | Áp dụng năm đầu tiên — thường có lợi hơn |

**Cư trú** = thỏa mãn **ÍT NHẤT 1** trong 2 tiêu chí.
**Không cư trú** = không thỏa mãn cả 2 tiêu chí.

> **Bổ sung:** Người nước ngoài có đăng ký thường trú tại VN (sổ hộ khẩu, thẻ tạm trú dài hạn) → LUÔN là cư trú thuế bất kể số ngày thực tế có mặt.

### Ví dụ — Năm Đầu Tiên

**Tình huống:** Chuyên gia Nhật đến VN ngày 01/08/2025.
- Năm 2025: 01/08 → 31/12 = **153 ngày** → < 183, không đủ Tiêu chí 1
- 12 tháng: 01/08/2025 → 31/07/2026:
  - Nếu ở VN thêm 30 ngày từ 1/1/2026 → tổng 153 + 30 = 183 ngày → **đủ Tiêu chí 2**
  - → Coi là **cư trú từ ngày 01/08/2025** (hồi tố)
  - → Phải kê khai thu nhập toàn cầu cho cả năm 2025

---

## Phần 2 — Hậu Quả Pháp Lý: Cư Trú vs Không Cư Trú

| | Cư trú | Không cư trú |
|---|--------|-------------|
| Phạm vi chịu thuế | **Thu nhập toàn cầu** (worldwide income) | Chỉ thu nhập **phát sinh tại VN** |
| Thuế suất | Biểu lũy tiến **5%–35%** (5 bậc 2026) | Flat **20%** (thu nhập từ lao động) |
| Kỳ quyết toán | Năm dương lịch | Cuối hợp đồng / trước khi rời VN |
| Giảm trừ gia cảnh | **Được áp dụng** (15.5tr/tháng) | **Không được áp dụng** |
| Giảm trừ NPT | **Được áp dụng** (6.2tr/người/tháng) | **Không được áp dụng** |
| Kê khai | Có thể ủy quyền cho DN khấu trừ thay | DN phải khấu trừ trực tiếp 20% |

---

## Phần 3 — Gross-up Net Salary

Nhiều expat ký HĐ quy định "net salary" (lương sau thuế được đảm bảo). Công ty phải gross-up để xác định thu nhập chịu thuế và số thuế phải nộp thay.

### Công thức Gross-up (Không cư trú — flat 20%)

```
Gross salary = Net salary ÷ (1 − 20%) = Net salary × 1.25

Thuế TNCN = Gross salary × 20%
```

**Ví dụ:**
- Net salary theo HĐ: 50.000.000 đ/tháng
- Gross = 50.000.000 ÷ 0.8 = **62.500.000 đ/tháng**
- Thuế = 62.500.000 × 20% = **12.500.000 đ/tháng** (công ty nộp thay)

### Công thức Gross-up (Cư trú — biểu lũy tiến)

Phức tạp hơn: cần giải phương trình ngược biểu thuế. Quy trình:

```
1. Xác định tổng giảm trừ (bản thân + NPT)
2. Tính TNTT thử = Net salary − Giảm trừ
3. Tính thuế từ TNTT thử theo biểu lũy tiến = T_thử
4. Gross salary thử = Net salary + T_thử
5. Tính lại TNTT = Gross − BHXH/BHYT/BHTN − Giảm trừ
6. Tính lại thuế T_mới
7. Lặp cho đến khi T_thử ≈ T_mới (sai số < 1.000 đ)
```

> **Khuyến nghị:** Dùng phần mềm kế toán hoặc spreadsheet để gross-up biểu lũy tiến. Không tính tay cho thu nhập cao.

---

## Phần 4 — Phúc Lợi Expat: Miễn Thuế vs Chịu Thuế

### Các khoản KHÔNG tính vào thu nhập chịu PIT

| Phúc lợi | Điều kiện miễn | Căn cứ |
|---------|---------------|--------|
| Tiền thuê nhà (công ty ký HĐ trực tiếp) | Tối đa **15% tổng thu nhập chịu thuế khác**; không vượt tiền thuê thực tế | Điều 11, TT 111/2013 |
| Vé máy bay về nước | 1 lần/năm cho expat và gia đình (nếu HĐ quy định) | Điều 11, TT 111/2013 |
| Học phí con cái tại VN | Theo hóa đơn thực từ trường học tại VN | Điều 11, TT 111/2013 |
| Phương tiện đi làm tập thể | Công ty bố trí phương tiện chung (không phải tiền mặt) | CV CQT hướng dẫn |
| Bữa ăn ca tập thể | ≤ 730.000 đ/tháng/người | NĐ liên quan |
| Đào tạo nghề nghiệp | Liên quan đến công việc; không phải học bổng cá nhân | Điều 11, TT 111/2013 |
| Điện thoại công vụ | Có quy chế phân bổ; dùng cho công việc | Thực tiễn CQT |

### Các khoản TÍNH vào thu nhập chịu PIT

| Phúc lợi | Thuế suất | Ghi chú |
|---------|-----------|---------|
| Tiền thuê nhà vượt 15% hoặc trả bằng tiền | 100% phần vượt | Phương án tiền mặt kém hơn |
| Thưởng Tết, thưởng hiệu quả (tiền mặt) | Biểu lũy tiến | Bất kể tên gọi |
| Thẻ sân golf, CLB cá nhân | 100% | Không phục vụ kinh doanh |
| Chi phí đi theo của gia đình | 100% | Vé bay, ăn ở cho vợ/chồng/con |
| Housing allowance bằng tiền mặt | 100% | Kém hơn để công ty ký HĐ trực tiếp |
| Xe hơi cá nhân dùng việc riêng | Giá trị sử dụng cá nhân | Phải phân bổ công/tư |

### So sánh chiến lược nhà ở

```
Phương án 1 (tốt hơn): Công ty ký HĐ thuê nhà trực tiếp
  Thu nhập chịu thuế (không kể nhà): 100 triệu/tháng
  Tiền thuê: 20 triệu → Miễn 15% × 100tr = 15 triệu; vượt: 5 triệu
  TNCT = 100 + 5 = 105 triệu

Phương án 2 (kém hơn): Trả housing allowance bằng tiền
  TNCT = 100 + 20 = 120 triệu
  
Chênh lệch thuế: (120 − 105) × 35% = 5.25 triệu/tháng tiết kiệm từ Phương án 1
```

---

## Phần 5 — Thuế Hiệp Định (DTA Credit)

### Nguyên tắc

Nếu expat đã nộp thuế ở nước nguồn (nước cư trú hoặc nước có thu nhập), VN cư trú có thể được **khấu trừ thuế đã nộp** (Foreign Tax Credit — FTC):

```
PIT tại VN = PIT tính trên thu nhập toàn cầu − FTC
FTC = Min(Thuế đã nộp ở nước ngoài, PIT VN tính trên cùng khoản thu nhập)
```

### Hồ sơ cần cho DTA credit

- [ ] Chứng từ nộp thuế nước ngoài (tax payment certificate / foreign tax receipt)
- [ ] Bản dịch công chứng (nếu không phải tiếng Anh/Việt)
- [ ] Tờ khai quyết toán nước ngoài
- [ ] Phân bổ thu nhập theo số ngày làm việc tại từng nước

> **Các DTA VN đã ký:** Trên 80 hiệp định (Nhật, Hàn, Sing, Pháp, Đức, Anh, Mỹ, TQ...). Tra cứu tại: gdt.gov.vn/content/tintuc/Lists/News.

---

## Phần 6 — Equity Xuyên Biên Giới

### Phân bổ thu nhập vesting period

Khi nhân viên làm việc tại nhiều nước trong thời gian vesting:

```
Thu nhập chịu PIT tại VN = Tổng giá trị equity × (Số ngày làm việc tại VN ÷ Tổng ngày vesting)
```

**Ví dụ:**
- Vesting: 4 năm (1.460 ngày)
- Số ngày tại VN: 730 ngày
- RSU khi vest: 200.000 USD
- Chịu PIT tại VN = 200.000 × (730/1.460) = **100.000 USD**

### Hồ sơ cần chuẩn bị

- [ ] Travel log / work calendar xác nhận ngày làm việc tại từng nước
- [ ] Hợp đồng/kế hoạch equity từ công ty mẹ
- [ ] Giá thị trường tại ngày exercise/vest (Bloomberg, sàn chứng khoán)

---

## Phần 7 — Quyết Toán Trước Khi Rời VN

**Bắt buộc quyết toán** trước ngày xuất cảnh lần cuối.

### Quy trình

1. Tính thu nhập từ đầu năm đến ngày rời VN
2. Xác định tư cách cư trú cuối cùng (đủ 183 ngày chưa?)
3. Nếu **cư trú**: biểu lũy tiến + thu nhập toàn cầu (từ VN + nước ngoài)
4. Nếu **không cư trú**: 20% flat chỉ trên thu nhập phát sinh tại VN
5. Nộp tờ khai + nộp thuế trước ngày xuất cảnh
6. Xin xác nhận hoàn thành nghĩa vụ thuế (nếu cần visa/work permit nước khác)

> **Lưu ý:** Một số cơ quan VN (cơ quan quản lý XNC) có thể yêu cầu clearance certificate trước khi gia hạn visa/work permit. Tốt nhất quyết toán sớm.

---

## Phần 8 — Checklist Expat

**Xác định tư cách cư trú:**
- [ ] Đếm ngày có mặt tại VN theo cả 2 tiêu chí
- [ ] Kiểm tra đăng ký thường trú (thẻ tạm trú, sổ hộ khẩu)
- [ ] Xác nhận năm đầu tiên: áp dụng 12-tháng liên tục nếu có lợi hơn

**Nếu cư trú:**
- [ ] Tổng hợp thu nhập toàn cầu (VN + nước ngoài)
- [ ] Kiểm tra DTA với nước nguồn → tính FTC
- [ ] HĐ quy định net hay gross? → Gross-up nếu net

**Phúc lợi:**
- [ ] Nhà ở: công ty ký HĐ thuê trực tiếp (tốt hơn) hay housing allowance?
- [ ] Liệt kê tất cả phúc lợi và phân loại miễn thuế / chịu thuế

**Equity:**
- [ ] Loại equity: stock option / RSU / ESPP / phantom stock?
- [ ] Phân bổ thu nhập nếu làm nhiều nước trong vesting period
- [ ] Phân loại: tiền lương hay đầu tư vốn? (Tham khảo CQT nếu giá trị lớn)
