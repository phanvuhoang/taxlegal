---
name: pit-advanced
version: 1.0.0
description: >
  Skill chuyên sâu về PIT — các trường hợp phức tạp: người nước ngoài, equity compensation,
  phúc lợi bằng hiện vật, quyết toán TNCN, phân bổ thu nhập xuyên biên giới.
  Bổ sung cho skill vietnam-pit.md.
category: tax
tags: [pit, tncn, expatriate, equity, stock-options, benefits-in-kind, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế Thu nhập Cá nhân — Nâng cao (PIT Advanced)

> **Quan hệ với vietnam-pit.md:** Skill này bổ sung cho `vietnam-pit.md` (cơ bản). Không lặp lại biểu thuế lũy tiến, giảm trừ gia cảnh chuẩn, và quy trình kê khai cơ bản. Tập trung vào các tình huống phức tạp thường gặp trong tư vấn doanh nghiệp FDI và nhân sự quốc tế.

**Căn cứ pháp lý chính:**
- Luật TNCN 04/2007/QH12 (sửa đổi bởi 26/2012/QH13, 71/2014/QH13)
- Thông tư 111/2013/TT-BTC — hướng dẫn chính (sửa đổi bởi TT92/2015, TT25/2018)
- Thông tư 10/2022/TT-BTC — hướng dẫn về người không cư trú

---

## A. Người nước ngoài (Expatriates) — Xác định Tư cách Cư trú

### Tiêu chí Cư trú Thuế

**Cư trú (Resident)** nếu thỏa mãn MỘT trong hai điều kiện:

| Tiêu chí | Mô tả | Cách tính |
|---------|-------|----------|
| **Tiêu chí 1** | Có mặt tại VN ≥183 ngày trong năm dương lịch | Cộng dồn tất cả ngày có mặt tại VN từ 1/1 đến 31/12 |
| **Tiêu chí 2** | Có mặt tại VN ≥183 ngày trong 12 tháng liên tục tính từ ngày đến VN lần đầu | Áp dụng cho năm đầu tiên đến VN — thường có lợi hơn Tiêu chí 1 |

**Không cư trú (Non-resident):** Không đáp ứng cả 2 tiêu chí trên.

### Hậu quả Pháp lý

| | Cư trú | Không cư trú |
|---|--------|-------------|
| Phạm vi chịu thuế | Thu nhập toàn cầu (Worldwide income) | Chỉ thu nhập phát sinh tại VN |
| Thuế suất | Biểu lũy tiến 5%–35% | Flat 20% (thu nhập từ lao động) |
| Kỳ quyết toán | Năm dương lịch (1/1–31/12) | Cuối hợp đồng / khi rời VN |
| Giảm trừ gia cảnh | Được áp dụng | Không được áp dụng |
| Kê khai | Có thể ủy quyền cho DN khấu trừ | DN phải khấu trừ trực tiếp |

### Ví dụ Thực tế — Năm Đầu Tiên

**Tình huống:** Chuyên gia người Nhật đến VN ngày 01/08/2024 để làm việc.
- Năm 2024: có mặt từ 01/08 đến 31/12 = 153 ngày → < 183 ngày theo Tiêu chí 1
- Tuy nhiên: 12 tháng từ 01/08/2024 đến 31/07/2025:
  - 01/08/2024 – 31/12/2024: 153 ngày
  - 01/01/2025 – 31/07/2025: cần thêm 30 ngày nữa để đủ 183 ngày
  - Nếu đủ 183 ngày trong 12 tháng đầu → được coi là cư trú từ ngày đầu đến VN

**Hệ quả:** Nếu là cư trú, thuế năm 2024 được tính theo biểu lũy tiến (thường thấp hơn 20% flat cho thu nhập cao), nhưng phải kê khai toàn bộ thu nhập toàn cầu.

### Gross-up khi Hợp đồng Quy định Net Salary

Nhiều expat ký HĐ lao động với mức "net salary" (lương sau thuế do DN bảo đảm). Kế toán cần gross-up để xác định thu nhập chịu thuế thực tế:

**Công thức Gross-up (lương cư trú):**

```
Thu nhập chịu thuế = (Net salary − Giảm trừ gia cảnh − Giảm trừ BHXH) + X
Trong đó X là thuế TNCN (tra theo biểu lũy tiến)
→ Giải bằng phương pháp thử dần hoặc công thức ngược biểu thuế
```

**Công thức Gross-up (không cư trú, flat 20%):**
```
Gross salary = Net salary / (1 − 20%) = Net salary × 1,25
```

**Ví dụ (không cư trú):**
- Net salary theo HĐ: 50.000.000 đ/tháng
- Gross salary = 50.000.000 / 0,8 = **62.500.000 đ/tháng**
- TNCN = 62.500.000 × 20% = **12.500.000 đ/tháng** (DN nộp thay)

---

## B. Equity Compensation — Quyền chọn cổ phiếu và cổ phiếu thưởng

### Phân loại và Thời điểm Tính Thuế

| Loại | Khi nào tính PIT | Căn cứ tính |
|------|-----------------|------------|
| **Stock Options (ESO)** | Tại thời điểm exercise (thực hiện quyền mua) | (Giá thị trường − Giá exercise) × Số cổ phiếu |
| **RSU (Restricted Stock Units)** | Tại thời điểm vest (nhận cổ phiếu thực tế) | Giá thị trường tại ngày vest × Số cổ phiếu |
| **ESPP (Employee Stock Purchase Plan)** | Khi mua cổ phiếu với giá ưu đãi | (Giá thị trường − Giá mua ưu đãi) × Số cổ phiếu |
| **Phantom Stock / SARs** | Khi nhận tiền mặt tương đương | Số tiền nhận được |

### Phân loại Thu nhập (⚠️ Vùng Xám)

**Vấn đề:** Thu nhập từ equity compensation được phân loại là:
- **Thu nhập từ tiền lương, tiền công** (biểu lũy tiến 5–35%) — quan điểm phổ biến hơn; phù hợp khi gắn với điều kiện làm việc
- **Thu nhập từ đầu tư vốn** (20% flat) — có thể lập luận nếu cổ phiếu được nhận và nắm giữ như tài sản đầu tư

**Thực tiễn hiện tại:** Nhiều CQT địa phương phân loại stock option là thu nhập từ tiền lương → biểu lũy tiến. **Cần xác nhận quan điểm CQT địa phương trước khi kê khai.**

**Khuyến nghị:** Nếu giá trị lớn → xin xác nhận từ CQT (ruling) trước khi exercise để tránh rủi ro.

### Phân bổ Thu nhập Xuyên biên giới

Khi nhân viên làm việc tại nhiều nước trong thời gian vesting:

```
Thu nhập chịu PIT tại VN = Tổng giá trị equity × (Số ngày làm việc tại VN / Tổng số ngày vesting)
```

**Ví dụ:**
- Tổng thời gian vesting: 4 năm (1.460 ngày)
- Số ngày làm việc tại VN trong vesting period: 730 ngày
- Tổng giá trị RSU khi vest: 200.000 USD
- Thu nhập chịu PIT tại VN = 200.000 × (730/1.460) = **100.000 USD**

**Hồ sơ cần chuẩn bị:**
- Tài liệu xác nhận ngày làm việc tại từng quốc gia (travel log, work calendar)
- Hợp đồng/kế hoạch equity từ công ty mẹ
- Bằng chứng giá thị trường tại ngày exercise/vest (Bloomberg, stock exchange data)

---

## C. Phúc lợi bằng hiện vật (Benefits in Kind)

### Các khoản KHÔNG tính vào Thu nhập chịu PIT

| Khoản phúc lợi | Điều kiện miễn | Căn cứ |
|---------------|---------------|--------|
| Tiền thuê nhà do DN thuê cho expat | Tối đa 15% tổng thu nhập chịu thuế khác; không vượt tiền thuê thực tế | Điều 11, TT111/2013 |
| Vé máy bay về nước | 1 lần/năm cho người nước ngoài và gia đình (nếu HĐ quy định) | Điều 11, TT111/2013 |
| Học phí con em người nước ngoài | Học tại VN; theo hóa đơn thực tế từ trường học | Điều 11, TT111/2013 |
| Phương tiện vận chuyển đi làm | Do DN bố trí phương tiện chung (không phải tiền mặt/xe cá nhân) | Công văn hướng dẫn CQT |
| Bữa ăn ca tập thể | Theo mức quy định (≤730.000đ/tháng/người cho bữa ca) | NĐ liên quan |
| Điện thoại công vụ | Dùng cho công việc; có quy chế phân bổ rõ ràng | Thực tiễn CQT |
| Đào tạo nghề nghiệp | Chi phí đào tạo liên quan đến công việc; không phải học bổng cá nhân | Điều 11, TT111/2013 |

### Các khoản TÍNH vào Thu nhập chịu PIT

| Khoản phúc lợi | Thuế suất | Ghi chú |
|---------------|-----------|---------|
| Thưởng tiền mặt (mọi loại) | Biểu lũy tiến | Kể cả thưởng Tết, thưởng hiệu quả |
| Tiền thuê nhà vượt 15% | Phần vượt + phần không đáp ứng điều kiện | Tính vào thu nhập tháng |
| Thẻ sân golf, CLB cá nhân | 100% giá trị | Không phải mục đích kinh doanh |
| Chi phí gia đình đi theo | 100% | Vé máy bay, ăn ở cho vợ/chồng/con |
| Phụ cấp tiền mặt (bất kỳ loại) | Biểu lũy tiến | Trừ một số phụ cấp đặc thù |
| Trợ cấp nhà ở bằng tiền mặt | 100% | Thay vì công ty thuê nhà trực tiếp |
| Xe hơi cá nhân dùng việc riêng | Giá trị sử dụng cá nhân | Cần phân bổ công/tư |

### Lưu ý Thực tiễn — Nhà ở cho Expat

**Phương án 1 (tốt hơn về thuế):** Công ty ký hợp đồng thuê nhà trực tiếp với chủ nhà → trả tiền thuê thẳng cho chủ nhà → khoản miễn tối đa 15% thu nhập chịu thuế.

**Phương án 2 (kém hơn về thuế):** Công ty trả thêm "housing allowance" bằng tiền mặt vào lương → tính 100% vào thu nhập chịu thuế.

**Ví dụ so sánh:**
```
Expat có thu nhập chịu thuế (không kể nhà ở): 100.000.000 đ/tháng
Tiền thuê nhà: 20.000.000 đ/tháng

Phương án 1 (Công ty ký HĐ thuê nhà):
  → Miễn tối đa 15% × 100.000.000 = 15.000.000 đ
  → Phần vượt 5.000.000 đ → tính vào thu nhập chịu thuế
  → Tổng thu nhập chịu thuế: 100.000.000 + 5.000.000 = 105.000.000 đ

Phương án 2 (Housing allowance bằng tiền):
  → Tính 100% 20.000.000 vào thu nhập
  → Tổng thu nhập chịu thuế: 100.000.000 + 20.000.000 = 120.000.000 đ
```

---

## D. Quyết toán TNCN — Các Tình huống Phức tạp

### Ai PHẢI Tự Quyết toán?

| Trường hợp | Bắt buộc tự quyết toán | Ghi chú |
|-----------|----------------------|---------|
| Có thu nhập từ 2+ nguồn (trừ trường hợp ủy quyền) | Có | Ngay cả khi từng nguồn đã khấu trừ đúng |
| Số thuế phải nộp thêm > 50.000 đ | Có | Dù chỉ 1 nguồn |
| Muốn hoàn thuế | Có | Không thể ủy quyền nếu muốn hoàn |
| Cá nhân nước ngoài kết thúc hợp đồng rời VN | Có | Phải quyết toán trước khi rời |

### Ai Được Ủy quyền?

Cá nhân được ủy quyền cho DN khấu trừ quyết toán thay nếu **đồng thời** thỏa mãn:
1. Chỉ có 1 nguồn thu nhập từ tiền lương/tiền công
2. Không phát sinh hoàn thuế hoặc nộp thêm (hoặc nộp thêm ≤50.000 đ)
3. Đang làm việc tại DN tại thời điểm ủy quyền

**Lỗi thường gặp:** Cá nhân làm thêm freelance (nhận thù lao từ nơi khác) nhưng vẫn ủy quyền cho DN chính → sai; phải tự quyết toán cộng tất cả thu nhập.

### Trình tự Quyết toán TNCN Năm cho DN

```
[Thu thập bảng lương 12 tháng + tất cả phụ cấp, thưởng]
         ↓
[Cộng toàn bộ thu nhập chịu thuế của từng nhân viên]
         ↓
[Trừ giảm trừ gia cảnh (cá nhân + người phụ thuộc)]
[Trừ BHXH, BHYT, BHTN phần cá nhân đóng]
[Trừ các khoản giảm trừ khác (từ thiện, bảo hiểm nhân thọ...)]
         ↓
[Tính PIT theo biểu lũy tiến]
         ↓
[So sánh với PIT đã khấu trừ trong năm]
         ↓
[Hoàn thuế hoặc nộp thêm (nếu có)]
         ↓
[Lập Mẫu 05/QTT-TNCN + Phụ lục 05-1/BK-QTT-TNCN]
[Nộp trước 31/3 năm sau (DN); 30/4 năm sau (cá nhân tự quyết toán)]
```

### Deadline và Phạt chậm nộp

| Đối tượng | Deadline | Phạt chậm nộp tờ khai | Phạt chậm nộp tiền |
|---------|---------|----------------------|-------------------|
| DN quyết toán thay | 31/3 năm sau | 1–3 triệu tùy số ngày | 0,03%/ngày trên số tiền chậm |
| Cá nhân tự quyết toán | 30/4 năm sau | 1–3 triệu tùy số ngày | 0,03%/ngày |
| Cá nhân nước ngoài rời VN | Trước ngày rời | Tùy trường hợp | 0,03%/ngày |

---

## E. Nhà thầu Cá nhân (Individual Contractors)

### Phân biệt HĐLĐ và HĐ Dịch vụ

| Tiêu chí | HĐLĐ | HĐ Dịch vụ |
|---------|------|-----------|
| Bản chất | Quan hệ lao động (employer–employee) | Quan hệ hợp đồng dân sự |
| Thời gian | Cố định hoặc vô thời hạn | Theo từng dự án/gói công việc |
| Kiểm soát công việc | DN kiểm soát cách thực hiện | Bên cung cấp DV tự quyết cách làm |
| Công cụ | Do DN cung cấp | Do nhà thầu tự chuẩn bị |
| BHXH | DN và NLĐ đóng BHXH | Không bắt buộc |
| Thuế PIT | Biểu lũy tiến (sau giảm trừ gia cảnh) | 10% khấu trừ tại nguồn (≥2 triệu/lần) |

**⚠️ Rủi ro Re-characterization:** CQT có thể re-classify HĐ dịch vụ thành HĐLĐ nếu thực chất là quan hệ lao động → truy thu BHXH + TNCN theo biểu lũy tiến + phạt.

### Khấu trừ PIT cho Nhà thầu Cá nhân

**Ngưỡng khấu trừ:** ≥2.000.000 đ/lần (trước ngày 1/1/2022: ≥2.000.000/lần; sau đó theo quy định cập nhật)

**Thuế suất:**
- Nếu tổng thu nhập cả năm từ DN này < 60 triệu → không phải khấu trừ 10% (nếu cá nhân có cam kết MST và thu nhập tổng không quá 60 triệu)
- Nếu tổng thu nhập từ DN > 60 triệu/năm → phải khấu trừ 10%

**Kê khai của DN:**
- Hàng tháng/quý: kê khai trong Mẫu 05/KK-TNCN
- Cuối năm: lập chứng từ khấu trừ 09/CKT-TNCN cho từng cá nhân
- Nộp thay vào NSNN: cùng kỳ khấu trừ TNCN nhân viên

### Cá nhân Doanh thu Lớn (>200 triệu/năm)

Nếu cá nhân ký nhiều HĐ dịch vụ với tổng doanh thu >200 triệu/năm:
- Phải kê khai như hộ kinh doanh (theo phương pháp khoán hoặc kê khai)
- Đăng ký kinh doanh (nếu chưa có)
- Nộp thuế môn bài, TNCN theo tỷ lệ trên doanh thu

---

## F. Các Tình huống Phức tạp Thường gặp

### Tình huống 1: Đổi việc giữa năm — Quyết toán thế nào?

**Bối cảnh:** Nhân viên làm việc tại Công ty A đến tháng 6, sau đó chuyển sang Công ty B.

**Vấn đề:** Hai nguồn thu nhập trong năm → phải tự quyết toán.

**Thực hiện:**
1. Công ty A: lập chứng từ khấu trừ TNCN (09/CKT) cho phần thu nhập 6 tháng
2. Công ty B: không được cộng dồn với Công ty A → chỉ tính từ tháng 7
3. Nhân viên: cộng tổng thu nhập 2 nguồn, tự quyết toán, nộp thêm hoặc hoàn thuế

**Lỗi phổ biến:** Công ty B áp dụng giảm trừ gia cảnh đầy đủ từ tháng 7 (thay vì chỉ tính phần chưa được dùng) → tính thuế thấp hơn thực tế → nhân viên phải nộp thêm khi quyết toán.

### Tình huống 2: Nhân viên nhận cổ phần ưu đãi từ công ty khởi nghiệp

**Bối cảnh:** Start-up cấp cổ phần cho nhân viên sáng lập với giá 0 đồng (founder shares).

**Vấn đề:** Khi nào tính PIT? Căn cứ tính là gì?
- Tại thời điểm nhận (0 đồng → giá thị trường thấp/bằng 0 cho start-up giai đoạn đầu)?
- Tại thời điểm bán cổ phần sau khi startup phát triển?

**Phân tích:**
- Phần chênh lệch khi nhận (nếu có) → PIT ngay
- Lãi khi bán cổ phần → PIT 20% (chuyển nhượng vốn)
- Thực tiễn: many early-stage startups chưa có giá thị trường rõ ràng → thường không phát sinh PIT tại thời điểm cấp; phát sinh tại thời điểm thoái vốn

### Tình huống 3: Expat làm việc 6 tháng VN, 6 tháng Singapore

**Bối cảnh:** Nhân viên cư trú thuế tại VN (183+ ngày) có thu nhập từ cả VN và Singapore.

**Nghĩa vụ tại VN:**
- PIT tại VN: đánh thuế trên thu nhập toàn cầu
- FTC: nếu đã nộp thuế tại Singapore → được khấu trừ số đã nộp vào PIT VN
- Giới hạn FTC: số khấu trừ không vượt PIT VN tính trên khoản thu nhập từ Singapore

**Hồ sơ cần thiết:**
- Chứng từ nộp thuế Singapore (tax payment certificate)
- Phân bổ thu nhập theo số ngày làm việc ở từng nước

---

## G. Checklist PIT Advanced

**Đối với Expats:**
- [ ] Xác định tư cách cư trú: đếm ngày có mặt tại VN theo cả 2 tiêu chí
- [ ] Nếu cư trú: cần tổng hợp thu nhập toàn cầu; yêu cầu cung cấp slip lương nước ngoài
- [ ] HĐ lao động quy định net hay gross? → cần gross-up nếu net
- [ ] Danh mục phúc lợi: phân loại rõ miễn thuế vs. chịu thuế
- [ ] Nhà ở: công ty ký HĐ thuê trực tiếp hay trả tiền cho nhân viên?

**Đối với Equity Compensation:**
- [ ] Loại equity: stock option, RSU, ESPP hay phantom stock?
- [ ] Thời điểm tính thuế: grant, vest hay exercise?
- [ ] Phân bổ thu nhập xuyên biên giới (nếu nhân viên làm nhiều nước trong vesting period)
- [ ] Phân loại thu nhập: tiền lương hay đầu tư vốn? → cần xác nhận với CQT nếu giá trị lớn

**Đối với Quyết toán năm:**
- [ ] Liệt kê tất cả nguồn thu nhập của cá nhân (kể cả freelance, cho thuê tài sản, cổ tức)
- [ ] Kiểm tra giảm trừ người phụ thuộc còn hợp lệ không
- [ ] Cá nhân nào ủy quyền cho DN → có đủ điều kiện ủy quyền không?
- [ ] Cá nhân nước ngoài sắp rời VN: đã quyết toán chưa?
