---
name: compliance-checklist
version: 1.0.0
description: >
  Skill hướng dẫn thực hiện quy trình Compliance Review — kiểm tra tuân thủ thuế
  theo từng bước, từ data request đến filing-ready approval gate.
  Dùng cho JA-Compliance, SA-Compliance, và mọi pipeline compliance.
category: compliance
tags: [compliance, review, checklist, filing, reconciliation, data-request, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Compliance Review — Quy trình và Checklist

## Tổng quan quy trình Compliance Review

```
[Tiếp nhận yêu cầu]
       ↓
[Data Request — Thu thập tài liệu]
       ↓
[Kiểm tra & Đối soát — Reconciliation]
       ↓
[Phát hiện vấn đề → Escalation nếu cần]
       ↓
[Filing-Ready Gate — 7 điểm kiểm tra]
       ↓
[Nộp tờ khai & Lưu hồ sơ]
```

---

## A. Data Request — Yêu cầu Tài liệu

### VAT Compliance (Hàng tháng / Hàng quý)

**Hóa đơn và bảng kê:**
- [ ] Bảng kê hóa đơn đầu vào (Mẫu 01-2/BK-HGTGT) — tất cả các kỳ trong kỳ review
- [ ] Bảng kê hóa đơn đầu ra (Mẫu 01-1/BK-HGTGT) — tất cả các kỳ
- [ ] Tờ khai VAT đã nộp (Mẫu 01/GTGT) — bản có xác nhận của CQT hoặc nộp online

**Chứng từ thanh toán:**
- [ ] Chứng từ thanh toán không dùng tiền mặt cho tất cả HĐ đầu vào có giá trị ≥20 triệu đồng/lần
- [ ] Sao kê ngân hàng tương ứng (để đối chiếu)

**Sổ sách kế toán:**
- [ ] Sổ cái TK 133 (thuế GTGT đầu vào) và TK 3331 (thuế GTGT đầu ra)
- [ ] Sổ chi tiết theo từng tháng/quý

**Hợp đồng và tài liệu bổ sung:**
- [ ] Hợp đồng với nhà thầu nước ngoài (nếu phát sinh FCT-VAT)
- [ ] Tờ khai FCT (nếu có) — Mẫu 01/NTNN
- [ ] Quyết định điều chỉnh, bổ sung (nếu có)

**Danh mục hàng hóa/dịch vụ đặc thù:**
- [ ] Danh sách hàng hóa/dịch vụ đang áp thuế 0%, 5%, 8% — cần xác minh đúng thuế suất
- [ ] Tài liệu xuất khẩu (nếu áp VAT 0%): HĐ xuất khẩu, tờ khai HQ, chứng từ TT ngoại tệ

---

### CIT Compliance (Hàng quý và Năm)

**Báo cáo tài chính:**
- [ ] BCTC năm (đã kiểm toán nếu doanh thu ≥ 3 tỷ hoặc là DN FDI)
- [ ] BCTC quý (nội bộ) — để đối chiếu với tạm nộp CIT hàng quý

**Tờ khai thuế:**
- [ ] Tờ khai TNDN quyết toán năm (Mẫu 03/TNDN) + các phụ lục đính kèm
- [ ] Tờ khai tạm nộp hàng quý (Mẫu 01A/TNDN hoặc 01B/TNDN) — 4 quý

**Tài sản cố định và khấu hao:**
- [ ] Danh sách TSCĐ (sổ TSCĐ) tính đến cuối năm
- [ ] Bảng trích khấu hao theo TT45/2013 (hoặc TT ngành nghề đặc thù)
- [ ] Biên bản thanh lý, nhượng bán TSCĐ (nếu có phát sinh)

**Chi phí được trừ:**
- [ ] Bảng tính chi phí không được trừ (tự lập) — theo từng khoản mục
- [ ] Hợp đồng + hóa đơn cho chi phí có giá trị ≥20 triệu đồng
- [ ] Chứng từ thanh toán không tiền mặt cho chi phí ≥20 triệu
- [ ] Hợp đồng lao động + quy chế lương thưởng + bảng lương thực tế chi trả
- [ ] Phiếu chi, ủy nhiệm chi, lệnh chi cho từng khoản chi phí lớn

**Ưu đãi thuế (nếu có):**
- [ ] Giấy chứng nhận đăng ký đầu tư + điều chỉnh (xác định điều kiện ưu đãi)
- [ ] Tài liệu xác nhận điều kiện ưu đãi (số lao động, vùng ưu đãi, lĩnh vực ưu đãi)
- [ ] Bảng tính ưu đãi TNDN (miễn, giảm, thuế suất ưu đãi)

**Giao dịch liên kết:**
- [ ] Mẫu 01 GCN-QLT (Thông tin giao dịch liên kết) — nếu có giao dịch liên kết
- [ ] Hồ sơ xác định giá thị trường (TP Documentation) nếu tổng giao dịch liên kết > ngưỡng
- [ ] Danh sách các bên liên kết và giá trị giao dịch theo từng loại

---

### PIT / Payroll Compliance (Hàng tháng / Hàng quý / Quyết toán năm)

**Bảng lương và hợp đồng:**
- [ ] Bảng lương chi tiết từng tháng (tất cả nhân viên, kể cả thử việc)
- [ ] Các khoản phụ cấp, thưởng, phúc lợi bằng hiện vật — danh sách và giá trị
- [ ] Hợp đồng lao động tất cả nhân viên — phân biệt HĐLĐ và HĐ dịch vụ
- [ ] Quyết định bổ nhiệm, thay đổi mức lương (nếu có trong kỳ)

**Người phụ thuộc và giảm trừ:**
- [ ] Danh sách người phụ thuộc đã đăng ký (kèm MST người phụ thuộc)
- [ ] Hồ sơ đăng ký người phụ thuộc (nếu có thay đổi trong kỳ)

**Tờ khai và chứng từ nộp:**
- [ ] Tờ khai khấu trừ TNCN hàng tháng/quý (Mẫu 05/KK-TNCN)
- [ ] Tờ khai quyết toán TNCN năm (Mẫu 05/QTT-TNCN) + phụ lục
- [ ] Chứng từ nộp tiền TNCN vào NSNN (biên lai điện tử)

**BHXH, BHYT, BHTN:**
- [ ] Thông báo đóng BHXH từ cơ quan BHXH (xác nhận số phải đóng)
- [ ] Chứng từ nộp BHXH, BHYT, BHTN hàng tháng
- [ ] Danh sách lao động đăng ký BHXH — đối chiếu với bảng lương

**Cá nhân nước ngoài (nếu có):**
- [ ] Hộ chiếu + visa + giấy phép lao động
- [ ] Hợp đồng lao động (bản tiếng Anh/tiếng Việt)
- [ ] Xác nhận ngày đến/rời VN (để xác định tư cách cư trú)
- [ ] Tài liệu thu nhập toàn cầu (nếu cư trú thuế tại VN)

---

## B. Reconciliation Checklist — Đối soát Chéo

### VAT Reconciliation

| Nội dung đối soát | Nguồn A | Nguồn B | Kết quả |
|-----------------|---------|---------|---------|
| Doanh thu kê khai VAT | Tờ khai 01/GTGT (tổng doanh thu chịu thuế) | Sổ kế toán TK 511 + 512 | Phải khớp (trừ doanh thu không chịu VAT) |
| Thuế đầu ra | Cột "Thuế GTGT" trên tờ khai | TK 3331 (bên Có) | Phải khớp |
| Thuế đầu vào | Cột khấu trừ trên tờ khai | TK 133 (bên Nợ) | Phải khớp |
| Số thuế còn được khấu trừ kỳ sau | Dòng cuối tờ khai | Số dư TK 133 cuối kỳ | Phải khớp |
| Số thuế đã nộp | Chứng từ nộp tiền | Sổ theo dõi nghĩa vụ thuế | Phải khớp |

**Điểm đối soát bổ sung:**
- Hóa đơn đầu ra: tổng giá trị trên hóa đơn = doanh thu kê khai?
- Hóa đơn đầu vào: có hóa đơn nào kỳ trước chưa kê khai, kỳ này mới kê khai không? → Kiểm tra điều kiện kỳ khai thuế liền kề
- Đối chiếu hóa đơn điện tử với dữ liệu CQT (hệ thống HDDT của Tổng cục Thuế)

### CIT Reconciliation

| Nội dung | Kế toán | Tờ khai | Chênh lệch | Giải thích |
|----------|---------|---------|-----------|-----------|
| Doanh thu | TK 511 + 515 + 711 | Phần B, Mẫu 03/TNDN | | Cần giải thích từng khoản chênh |
| Chi phí | TK 6xx + 8xx | Phần C, Mẫu 03/TNDN | | Chi phí không được trừ → điều chỉnh tăng |
| Lợi nhuận trước thuế | BCTC | | | Điều chỉnh tăng/giảm = chênh lệch |
| Thu nhập chịu thuế | | Phần D, Mẫu 03/TNDN | | Sau các điều chỉnh và ưu đãi |
| Thuế phải nộp | | | | Phải ≥ 80% số quyết toán (nếu không → phạt) |

**Điều chỉnh tăng thu nhập chịu thuế thường gặp:**
- Chi phí không có HĐ, HĐ không hợp lệ
- Chi phí lương không thực tế chi trả (kê khai cao hơn chi trả)
- Khấu hao TSCĐ vượt mức theo TT45
- Chi phí tiếp khách không đúng 10% tổng chi phí được trừ
- Chi phí lãi vay vượt 30% EBITDA (thin cap rule cho giao dịch liên kết)

### PIT Reconciliation

| Nội dung | Bảng lương | Tờ khai | Kết quả |
|----------|-----------|---------|---------|
| Tổng lương, thưởng, phụ cấp | Bảng lương tổng hợp | Mẫu 05/KK-TNCN (Cột Thu nhập chịu thuế) | Phải khớp (trừ các khoản miễn) |
| Tổng TNCN đã khấu trừ | Bảng lương (cột khấu trừ) | Mẫu 05/KK-TNCN | Phải khớp |
| Tổng TNCN đã nộp | | Chứng từ nộp tiền | Phải = tổng khấu trừ |

**Công nợ thuế đối chiếu sổ kế toán:**
- Số dư TK 3335 (TNCN phải nộp) cuối kỳ = TNCN đã khấu trừ − TNCN đã nộp → phải ≈ 0 hoặc đúng với kỳ nộp tiếp theo

---

## C. Filing-Ready Approval Gate — 7 Điểm Kiểm tra

Trước khi ký duyệt để nộp tờ khai, thực hiện kiểm tra đầy đủ 7 điểm:

### Điểm 1: Hóa đơn đầu vào đã đối chiếu với sổ sách

- [ ] Tổng số HĐ đầu vào trên bảng kê = số HĐ đã nhập sổ kế toán?
- [ ] Không có HĐ kỳ này chưa được kê khai (sót HĐ)?
- [ ] HĐ nào bị CQT thông báo là không hợp lệ/rủi ro → đã loại khỏi khấu trừ?

### Điểm 2: Thanh toán không tiền mặt cho HĐ ≥20 triệu

- [ ] Đã rà soát toàn bộ HĐ đầu vào ≥20 triệu/lần?
- [ ] Mỗi HĐ có ít nhất 1 chứng từ thanh toán ngân hàng tương ứng?
- [ ] Chứng từ thanh toán khớp về số tiền, tên người bán, số HĐ?

### Điểm 3: Các khoản điều chỉnh CIT có đủ lý do

- [ ] Mỗi khoản điều chỉnh tăng/giảm thu nhập chịu thuế đã có ghi chú rõ lý do và căn cứ pháp lý?
- [ ] Chi phí không được trừ đã được tổng hợp đầy đủ?
- [ ] Ưu đãi thuế được áp dụng đúng điều kiện?

### Điểm 4: CIT tạm nộp không thấp hơn 80% số quyết toán

Theo Điều 55, Luật Quản lý Thuế 38/2019: Nếu CIT tạm nộp 4 quý thấp hơn 80% số phải nộp theo quyết toán → bị phạt chậm nộp trên phần chênh lệch vượt 20%.

- [ ] Tổng CIT tạm nộp 4 quý ≥ 80% × CIT quyết toán năm?
- [ ] Nếu chưa đủ → cần nộp bổ sung trước 31/1 năm sau?

### Điểm 5: Không có lỗi số học trên tờ khai

- [ ] Chạy lại tất cả công thức tính trên tờ khai (tổng, tích)?
- [ ] Số liệu mang sang từ kỳ trước (số dư khấu trừ, lỗ kết chuyển) đúng không?
- [ ] Số thuế phải nộp = Số phải nộp theo tính toán − Số đã tạm nộp?

### Điểm 6: Người có thẩm quyền đã ký xác nhận

- [ ] Tờ khai đã có chữ ký của người đại diện pháp lý hoặc người được ủy quyền?
- [ ] Trường hợp ủy quyền: có văn bản ủy quyền hợp lệ không?
- [ ] Nếu nộp điện tử: đã ký điện tử bằng chữ ký số của DN?

### Điểm 7: Backup files an toàn trước khi nộp

- [ ] File tờ khai (XML/PDF) đã được lưu vào hệ thống lưu trữ nội bộ?
- [ ] Hồ sơ tài liệu kèm theo đã được scan và lưu kỹ thuật số?
- [ ] Version cuối cùng có được đánh dấu rõ "FINAL - ready to file"?

---

## D. Common Compliance Red Flags

### Red Flags về Hóa đơn và Chứng từ

| Red Flag | Mô tả | Hậu quả |
|---------|-------|---------|
| HĐ đầu vào không có chứng từ TT ngân hàng | HĐ ≥20 triệu mà thanh toán tiền mặt | Không được khấu trừ VAT; chi phí CIT không được trừ |
| HĐ ngày lập vs ngày TT lệch nhiều | Ký HĐ tháng 3 nhưng TT tháng 11 năm sau | CQT có thể cho rằng giao dịch không thực tế |
| HĐ từ DN bỏ trốn / mất tích | Bên bán không còn hoạt động | Bị loại toàn bộ khấu trừ + truy thu |
| Bảng kê đầu vào > Số HĐ thực có | Kê khai HĐ chưa nhận được | Vi phạm pháp luật về kê khai sai |

### Red Flags về Lương và TNCN

| Red Flag | Mô tả | Hậu quả |
|---------|-------|---------|
| Lương kê khai thấp hơn thực tế | Trả lương cao nhưng kê khai thấp để giảm TNCN | Truy thu TNCN, xử phạt, hình sự nếu nghiêm trọng |
| Không cộng tất cả khoản thu nhập | Bỏ sót thưởng, phụ cấp, benefits bằng hiện vật | Kê khai thiếu thu nhập chịu thuế |
| BHXH không khớp bảng lương | Lương BHXH < lương thực tế trong HĐ | Truy thu BHXH; CQT cũng dùng để so sánh |
| Người phụ thuộc không đủ điều kiện | Khai người phụ thuộc đã tự nuôi sống được | Bị loại giảm trừ, truy thu TNCN |

### Red Flags về CIT

| Red Flag | Mô tả | Hậu quả |
|---------|-------|---------|
| Chi phí lương chi trả thực tế < kê khai | Không có chứng từ chi trả đầy đủ | Chi phí không được trừ phần không chi trả thực tế |
| Không kê khai giao dịch liên kết | Phát sinh mua/bán với bên liên kết nhưng không lập Mẫu 01 GCN-QLT | Phạt vi phạm + bị ấn định giá chuyển nhượng |
| Quyết toán CIT vs tạm nộp chênh lớn | CIT quyết toán cao hơn nhiều so với tạm nộp mà không giải thích | Phạt chậm nộp + dễ bị chọn kiểm tra |
| Kết chuyển lỗ sai | Kết chuyển lỗ quá 5 năm hoặc vào thu nhập ưu đãi | Truy thu CIT trên phần lỗ kết chuyển sai |

### Red Flags về Cổ tức

| Red Flag | Mô tả | Hậu quả |
|---------|-------|---------|
| Cổ tức trả cho cá nhân không kê khai TNCN | Chia cổ tức bằng tiền mặt hoặc chuyển khoản nhưng không khấu trừ 5% TNCN | Truy thu TNCN 5% + phạt |
| Cổ tức từ lợi nhuận chưa quyết toán thuế | Chia cổ tức trong khi CIT năm chưa quyết toán | Rủi ro điều chỉnh lại khi quyết toán |

---

## E. Escalation to Advisory

### Khi nào Compliance Review cần Escalate lên Advisory?

| Tình huống | Hành động |
|-----------|----------|
| Phát hiện thuế suất áp dụng sai nhiều kỳ | Dừng lại — không tự sửa; escalate để xác định chiến lược voluntary disclosure vs. giải trình |
| Chi phí lớn bị nghi ngờ không được trừ nhưng chưa có hướng dẫn rõ ràng | Escalate để có Advisory memo trước khi quyết toán |
| Giao dịch liên kết có giá trị lớn, không có TP study | Escalate để đánh giá rủi ro transfer pricing |
| DN bị thông báo kiểm tra thuế | Đình chỉ mọi điều chỉnh tự nguyện; escalate ngay |
| Phát hiện lỗi kê khai các năm trước có thể bị phát hiện | Escalate để quyết định voluntary amendment vs. chờ kiểm tra |
| Giao dịch mới phát sinh chưa có văn bản hướng dẫn | Escalate để có Advisory trước khi kê khai |

### Gói Thông tin khi Escalate

Khi chuyển vấn đề từ Compliance sang Advisory, chuẩn bị:
1. Mô tả ngắn gọn: giao dịch/tình huống phát sinh
2. Số liệu định lượng: giá trị phát sinh, số kỳ ảnh hưởng, ước tính rủi ro thuế
3. Tài liệu đính kèm: HĐ, hóa đơn, tờ khai liên quan
4. Deadline: cần tư vấn trước ngày nào? (hạn nộp tờ khai?)
5. Câu hỏi cụ thể cần Advisory trả lời

---

## F. Timeline Chuẩn cho Compliance Review

| Loại thuế | Kỳ kê khai | Hạn nộp | Buffer cần thiết |
|---------|-----------|---------|-----------------|
| VAT tháng | Tháng | Ngày 20 tháng sau | Bắt đầu chuẩn bị từ ngày 10–12 |
| VAT quý | Quý | Ngày 30 tháng đầu quý sau | Bắt đầu từ ngày 15 tháng cuối quý |
| CIT tạm nộp quý | Quý | Ngày 30 tháng đầu quý sau | Song song với VAT quý |
| TNCN tháng/quý | Tháng hoặc Quý | Ngày 20 tháng sau / Ngày 30 tháng đầu quý sau | 5–7 ngày làm việc trước hạn |
| CIT quyết toán năm | Năm | 31/3 năm sau (có thể gia hạn) | Bắt đầu từ 15/1 năm sau |
| TNCN quyết toán năm | Năm | 30/4 năm sau | Bắt đầu từ 1/3 năm sau |
