---
name: vat-return-review
version: 1.0.0
description: >
  Skill hướng dẫn rà soát và lập tờ khai thuế GTGT (Mẫu 01/GTGT) tại Việt Nam: phân tích
  từng dòng từ [26]–[42], working paper template, 4 đầu ra bắt buộc, kiểm tra chéo, và
  onboarding khi thiếu tài liệu. Chuẩn hóa theo quy trình openaccountants-tax.
category: tax
tags: [vat, gtgt, tax-return, tờ-khai, form-01-gtgt, working-paper, review, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Rà Soát Tờ Khai Thuế GTGT (01/GTGT)

> **Căn cứ:** TT 219/2013/TT-BTC, TT 80/2021/TT-BTC, NĐ 123/2020/NĐ-CP

---

## Phần 1 — Sơ Đồ Tờ Khai 01/GTGT

### Map các dòng quan trọng

| Dòng | Nội dung | Công thức |
|------|---------|-----------|
| **[26]** | Doanh thu chịu thuế 10% (net) | Nhập từ sổ cái |
| **[27]** | Thuế đầu ra 10% | [26] × 10% |
| **[28]** | Doanh thu chịu thuế 5% (net) | Nhập từ sổ cái |
| **[29]** | Thuế đầu ra 5% | [28] × 5% |
| **[30]** | Doanh thu xuất khẩu 0% | Nhập từ sổ cái |
| **[31]** | Doanh thu không chịu thuế | Nhập từ sổ cái |
| **[32]** | **Tổng thuế đầu ra** | [27] + [29] |
| **[33]** | Tổng thuế GTGT đầu vào phát sinh | Nhập từ bảng kê |
| **[34]** | Đầu vào không được khấu trừ | Phân tích từng hóa đơn |
| **[35]** | **Đầu vào được khấu trừ** | [33] − [34] |
| **[40]** | Số thuế phải nộp ([32] > [35]) | [32] − [35] (nếu dương) |
| **[41]** | Số thuế còn được khấu trừ | [35] − [32] (nếu dương) |
| **[42]** | **Thuế phải nộp kỳ này** | [40] − Số còn khấu trừ kỳ trước |

---

## Phần 2 — Quy Trình Rà Soát (4 Bước)

### Bước 1: Thu thập và kiểm tra đầu vào

**Thông tin tối thiểu cần có:**
- [ ] Phương pháp tính thuế (khấu trừ / trực tiếp) + MST
- [ ] Sao kê ngân hàng kỳ kê khai (CSV, PDF, hoặc text)
- [ ] Bảng kê hóa đơn đầu vào (nếu có)
- [ ] Hóa đơn đầu ra đã phát hành

**Thông tin tối ưu thêm:**
- [ ] Số dư thuế còn được khấu trừ kỳ trước (carried forward)
- [ ] Tờ khai hải quan (nếu có xuất khẩu)
- [ ] Xác nhận thanh toán ngoại tệ (nếu zero-rate)

### Bước 2: Phân loại giao dịch (dùng Supplier Pattern Library)

Áp dụng pattern matching từ `vat-invoice-validity.md`:
- EXCLUDE: ngân hàng (phí), chính phủ (thuế), bảo hiểm, nội bộ
- Input 10%: điện, viễn thông, vận tải nội địa, hàng hóa/DV thông thường
- Input 5%: nước sạch, phân bón, sách, thiết bị y tế
- FLAG FCT: nhà cung cấp quốc tế
- Tier 2 — hỏi thêm: xuất khẩu chưa xác nhận, hàng hóa đặc thù

### Bước 3: Tính toán và kiểm tra chéo

**Kiểm tra chéo bắt buộc:**
- [ ] [27] = [26] × 10% (không có sai số > 1.000 đ)
- [ ] [29] = [28] × 5% (không có sai số)
- [ ] [32] = [27] + [29]
- [ ] [35] = [33] − [34] (không âm)
- [ ] [40] hoặc [41] = |[32] − [35]| (một trong hai, không cả hai)
- [ ] [42] = [40] − Số còn khấu trừ kỳ trước (nếu [40] > 0)
- [ ] Tổng [26] + [28] + [30] + [31] khớp với doanh thu sổ cái

### Bước 4: Lập 4 đầu ra bắt buộc

---

## Phần 3 — 4 Đầu Ra Bắt Buộc

Mọi tờ khai GTGT phải có đủ 4 tài liệu sau:

### 1. Working Paper (Bảng Tính Thuế)

```
VIETNAM VAT WORKING PAPER — BẢNG TÍNH THUẾ GTGT
Kỳ khai thuế: ____/____    MST: ____________

A. THUẾ ĐẦU RA (OUTPUT VAT)
  A1. Doanh thu chịu thuế 10% (net)     ___________
  A2. Thuế đầu ra 10% (A1 × 10%)        ___________
  A3. Doanh thu chịu thuế 5% (net)      ___________
  A4. Thuế đầu ra 5% (A3 × 5%)          ___________
  A5. Xuất khẩu 0% (net)                ___________
  A6. Doanh thu không chịu thuế (net)   ___________
  A7. Tổng thuế đầu ra (A2 + A4)        ___________

B. THUẾ ĐẦU VÀO (INPUT VAT)
  B1. Mua hàng chịu thuế 10% (net)      ___________
  B2. Thuế đầu vào 10% (B1 × 10%)       ___________
  B3. Mua hàng chịu thuế 5% (net)       ___________
  B4. Thuế đầu vào 5% (B3 × 5%)         ___________
  B5. Thuế nhập khẩu đã nộp             ___________
  B6. Tổng thuế đầu vào (B2+B4+B5)      ___________
  B7. Thuế đầu vào không được khấu trừ  ___________
  B8. Thuế đầu vào được khấu trừ (B6−B7) ___________

C. THUẾ PHẢI NỘP
  C1. Chênh lệch thuế (A7 − B8)         ___________
  C2. Thuế còn khấu trừ kỳ trước        ___________
  C3. Thuế GTGT phải nộp (C1 − C2)      ___________
  C4. Hoặc: Thuế còn được khấu trừ      ___________
```

### 2. Reviewer Brief

Tóm tắt ngắn gọn (1 trang) cho partner/reviewer:
- Kỳ kê khai, doanh nghiệp, MST, phương pháp
- Số thuế đầu ra, đầu vào, số phải nộp/còn khấu trừ
- Các điểm lưu ý và flag cần reviewer xem xét
- Danh sách Tier 2 items chưa giải quyết

### 3. Action List

Danh sách việc cần làm trước khi nộp tờ khai:
- [ ] Xác nhận hóa đơn điện tử cho tất cả đầu vào > 20 triệu
- [ ] Lấy tờ khai hải quan cho khoản xuất khẩu (nếu có)
- [ ] Xác nhận FCT với nhà cung cấp quốc tế (nếu có)
- [ ] Giải quyết các Tier 2 items (flagged items)
- [ ] Ký duyệt tờ khai trước deadline

### 4. Review Checklist

```
REVIEWER FLAGS — phải tích trước khi ký nộp:
  [ ] Hóa đơn điện tử xác nhận cho TẤT CẢ đầu vào?
  [ ] Thanh toán ngân hàng cho giao dịch > 20 triệu?
  [ ] Bằng chứng xuất khẩu (tờ khai hải quan) đủ cho 0% items?
  [ ] FCT status xác nhận cho nhà cung cấp quốc tế?
  [ ] Tỷ lệ phân bổ đầu vào tính đúng (nếu có miễn thuế)?
  [ ] Số còn khấu trừ kỳ trước khớp với kỳ trước?
  [ ] [32], [35], [42] tính đúng và nhất quán?
  [ ] Không có flag đỏ chưa giải quyết?
```

---

## Phần 4 — Onboarding Thiếu Tài Liệu

Nếu khách hàng chỉ cung cấp sao kê ngân hàng:

```
ONBOARDING — Câu hỏi tối thiểu:
1. MST (Mã số thuế — 10 chữ số)?
2. Phương pháp: khấu trừ (deduction) hay trực tiếp (direct)?
3. Kỳ kê khai: theo tháng hay theo quý?
4. Doanh thu năm trước (để xác định tần suất kê khai)?
5. Có doanh thu xuất khẩu (0%) không?
   → Nếu có: thanh toán USD/EUR? Hợp đồng với đối tác nước ngoài?
6. Có thanh toán cho nhà cung cấp quốc tế (Google, MS, AWS...) không?
7. Số thuế còn được khấu trừ kỳ trước?
8. Có doanh thu không chịu thuế (miễn thuế) không?
```

**Quy trình xử lý khi thiếu hóa đơn:**
1. Phân loại toàn bộ giao dịch ngân hàng theo Supplier Pattern Library
2. Áp dụng conservative defaults (unknowns → 10%; không HĐĐT → 0% đầu vào)
3. Flag tất cả Tier 2 items (FCT, export, 5% items chưa xác nhận)
4. Tạo Working Paper với cột FLAG rõ ràng
5. Action List gửi cho khách hàng để giải quyết flags

---

## Phần 5 — Deadlines & Phạt

| Kỳ kê khai | Đối tượng | Deadline |
|-----------|----------|---------|
| Hàng tháng | Doanh thu năm trước > 50 tỷ | **20 ngày đầu tháng sau** |
| Hàng quý | Doanh thu năm trước ≤ 50 tỷ | **30 ngày đầu tháng sau quý** |
| Quyết toán năm | Tất cả DN | **31/3 năm sau** |

| Vi phạm | Phạt |
|---------|------|
| Nộp tờ khai chậm | 2.000.000 – 25.000.000 đ |
| Nộp thuế chậm | 0.03%/ngày × số ngày chậm × số tiền |
| Khai sai dẫn đến thiếu thuế | 20% × số thuế khai thiếu |
| Trốn thuế, gian lận | 1× – 3× số thuế |
