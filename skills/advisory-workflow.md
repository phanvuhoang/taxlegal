---
name: advisory-workflow
version: 1.0.0
description: >
  Skill hướng dẫn quy trình làm Advisory — từ tiếp nhận vấn đề đến phát hành memo tư vấn.
  Bao gồm: chuẩn hóa sự kiện, thứ tự nghiên cứu pháp lý, cấu trúc lập luận,
  xử lý rủi ro và bất định, kiểm duyệt memo, và bàn giao cho khách hàng.
category: advisory
tags: [advisory, workflow, process, legal-research, memo, quality, review, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Advisory Workflow — Quy trình Tư vấn Thuế

## Tổng quan quy trình Advisory

```
[Tiếp nhận & Intake]
       ↓
[Chuẩn hóa Sự kiện — Fact Normalization]
       ↓
[Xác định Vấn đề Pháp lý — Issue Spotting]
       ↓
[Nghiên cứu Pháp lý — Legal Research]
       ↓
[Soạn thảo Memo — Drafting]
       ↓
[SA Review]
       ↓
[Partner Review & Sign-off]
       ↓
[Bàn giao Khách hàng — Delivery]
       ↓
[Lưu hồ sơ — Archiving]
```

---

## A. Tiếp nhận và Chuẩn hóa Sự kiện (Intake & Fact Normalization)

### Câu hỏi Tiếp nhận Bắt buộc

Trước khi bắt đầu nghiên cứu pháp lý, phải làm rõ 7 câu hỏi sau:

**1. Ai là các bên?**
- Tên pháp nhân đầy đủ, quốc tịch, hình thức tổ chức (TNHH, cổ phần, chi nhánh, VPĐD...)
- Cá nhân hay pháp nhân? Cư trú thuế ở đâu? (VN hay nước ngoài)
- Có quan hệ liên kết giữa các bên không?

**2. Giao dịch là gì?**
- Mô tả chính xác bản chất giao dịch: bán hàng hóa, cung cấp dịch vụ, chuyển nhượng vốn, cho vay, trả cổ tức, cấp phép IP, thuê tài sản...
- Địa điểm thực hiện: tại VN hay nước ngoài?
- Một lần hay định kỳ?

**3. Khi nào giao dịch phát sinh?**
- Ngày ký hợp đồng
- Ngày thực hiện / ngày phát sinh nghĩa vụ thuế
- Ngày thanh toán
- ⚠️ Quan trọng: Quy định pháp luật áp dụng tại thời điểm nào? (văn bản có thể đã thay đổi)

**4. Giá trị là bao nhiêu?**
- Giá trị hợp đồng / giao dịch
- Đồng tiền thanh toán (VND hay ngoại tệ?)
- Lãi/lỗ dự kiến (nếu là chuyển nhượng)

**5. Đã có văn bản nào liên quan chưa?**
- Hợp đồng (dự thảo hay đã ký?)
- Công văn, email trao đổi với CQT
- Biên bản họp, thỏa thuận nội bộ
- Ý kiến tư vấn trước đây (nếu có)

**6. Có yếu tố nước ngoài không?**
- Một bên là tổ chức/cá nhân nước ngoài?
- Có Hiệp định tránh đánh thuế (DTA) áp dụng không?
- Có PE risk không?
- Có FCT / FTC phát sinh không?

**7. Thời hạn và yêu cầu đặc biệt?**
- Cần tư vấn trước ngày nào?
- Định dạng yêu cầu: memo đầy đủ / email tóm tắt / verbal briefing?
- Mức độ chi tiết: standard / deep?
- Ngôn ngữ: tiếng Việt / tiếng Anh / song ngữ?

### Completeness Matrix

Sử dụng bảng này để xác định thông tin còn thiếu:

| Hạng mục thông tin | Trạng thái | Nguồn bổ sung |
|-------------------|-----------|---------------|
| Tên và tư cách pháp nhân các bên | ☐ Đã có / ☐ Cần bổ sung | |
| Bản chất giao dịch | ☐ Đã có / ☐ Cần bổ sung | |
| Thời điểm giao dịch | ☐ Đã có / ☐ Cần bổ sung | |
| Giá trị giao dịch | ☐ Đã có / ☐ Cần bổ sung | |
| Hợp đồng/văn bản | ☐ Đã có / ☐ Cần bổ sung | |
| Yếu tố nước ngoài | ☐ Đã xác định / ☐ Cần xác nhận | |
| Deadline trả lời | ☐ Đã có / ☐ Cần xác nhận | |

**Quy tắc:** Nếu >2 ô "Cần bổ sung" trong completeness matrix → gửi yêu cầu bổ sung thông tin trước khi nghiên cứu. Không bắt đầu research khi dữ liệu đầu vào không đủ.

---

## B. Xác định Vấn đề Pháp lý (Issue Spotting)

### Phương pháp Issue Spotting

Sau khi chuẩn hóa sự kiện, liệt kê tất cả các vấn đề thuế có thể phát sinh:

**Bước 1:** Xác định loại giao dịch → loại thuế nào có thể phát sinh?

| Loại giao dịch | Thuế có thể phát sinh |
|---------------|----------------------|
| Mua bán hàng hóa | VAT, TTĐB (nếu là hàng đặc biệt), CIT (doanh thu/chi phí) |
| Cung cấp dịch vụ | VAT, CIT, FCT (nếu nhà thầu nước ngoài) |
| Chuyển nhượng vốn | TNDN (20% trên lãi), PIT (nếu cá nhân) |
| Trả cổ tức | PIT 5% (cá nhân), TNDN 0% (pháp nhân) |
| Cho vay | FCT 5% CIT (lãi vay trả nước ngoài), PIT (lãi vay nhận bởi cá nhân) |
| Thuê tài sản | VAT, CIT, PIT (nếu cá nhân cho thuê: 5%) |
| Cấp phép IP/bản quyền | FCT 10% (tiền bản quyền trả nước ngoài) |

**Bước 2:** Với từng loại thuế, đặt câu hỏi:
- Đối tượng chịu thuế? (Subject to tax?)
- Căn cứ tính thuế? (Tax base?)
- Thuế suất? (Rate?)
- Ai kê khai, ai nộp? (Who declares?)
- Hạn kê khai, nộp? (When?)
- Có miễn/giảm/ưu đãi không? (Any exemption?)

**Bước 3:** Sắp xếp vấn đề theo thứ tự ưu tiên:
1. Vấn đề có tác động tài chính lớn nhất
2. Vấn đề có deadline sớm nhất
3. Vấn đề "grey area" cần phân tích sâu

---

## C. Thứ tự Nghiên cứu Pháp lý (Legal Research Order)

### Hệ thống phân cấp nguồn pháp lý Việt Nam

```
[Cấp 1] Luật, Bộ luật — Quốc hội ban hành
         ↓ (chi tiết hóa)
[Cấp 2] Nghị định — Chính phủ
         ↓ (hướng dẫn cụ thể)
[Cấp 3] Thông tư — Bộ Tài chính / Tổng cục Thuế
         ↓ (giải thích, áp dụng cụ thể)
[Cấp 4] Công văn — Tổng cục Thuế / Cục Thuế
         ↓ (tham khảo, không phải quy phạm)
[Cấp 5] Án lệ / Bản án tòa án (nếu có)
         ↓ (tham khảo)
[Cấp 6] Học thuật, Thông lệ quốc tế, OECD Commentary
```

### Thứ tự Research trong thực hành

**Bước 1:** Xác định quy định khung (Luật)
- Luật nào điều chỉnh loại thuế này? Phiên bản hiệu lực tại thời điểm giao dịch?
- Điều khoản nào trực tiếp áp dụng?

**Bước 2:** Tìm Nghị định hướng dẫn
- Nghị định nào hướng dẫn Luật đó?
- Có sửa đổi bổ sung nào không?

**Bước 3:** Xác định Thông tư chi tiết
- Thông tư nào của Bộ Tài chính / Tổng cục Thuế hướng dẫn cụ thể?
- Có Thông tư sửa đổi, bổ sung, thay thế không?

**Bước 4:** Tìm Công văn hướng dẫn tình huống tương tự
- Có Công văn nào xử lý tình huống tương tự không?
- Công văn của Tổng cục Thuế có giá trị cao hơn Cục thuế địa phương

**Bước 5:** Xem xét thực tiễn và án lệ
- Có bản án hành chính liên quan không?
- Thực tiễn kiểm tra thuế tại VN xử lý thế nào?

### Kiểm tra Hiệu lực văn bản

Trước khi trích dẫn bất kỳ văn bản nào, xác nhận:
- [ ] Văn bản còn hiệu lực hay đã bị thay thế/sửa đổi/bãi bỏ?
- [ ] Nếu đã sửa đổi: điều khoản cụ thể trích dẫn có bị sửa không?
- [ ] Ngày hiệu lực so với thời điểm giao dịch?

> **Lệnh:** Không bao giờ trích dẫn văn bản đã bị thay thế mà không ghi rõ. Nếu không chắc → ghi "(cần xác minh hiệu lực)".

---

## D. Cấu trúc Lập luận (Argument Structure — IRAC)

### Áp dụng IRAC cho từng vấn đề

**I — Issue (Vấn đề):**
- Nêu câu hỏi pháp lý cụ thể, rõ ràng
- Ví dụ: "Liệu khoản phí dịch vụ tư vấn chiến lược trả cho công ty mẹ tại Hồng Kông có bị FCT 5% CIT theo TT103/2014 không?"

**R — Rule (Quy định):**
- Trích dẫn đầy đủ quy định áp dụng (điều, khoản, điểm)
- Nêu nguyên tắc tổng quát trước, sau đó ngoại lệ và điều kiện

**A — Application (Áp dụng):**
- Đưa sự kiện vào quy định: từng yếu tố của quy định khớp với sự kiện như thế nào?
- Phân tích điểm nào rõ ràng, điểm nào "grey area"

**C — Conclusion (Kết luận):**
- Kết luận dứt khoát (theo mức độ chắc chắn của pháp lý)
- Ước lượng rủi ro nếu có bất định

### Ước lượng Rủi ro Thuế

| Mức rủi ro | Mô tả | Cách trình bày trong memo |
|-----------|-------|--------------------------|
| **Thấp** | Có văn bản hướng dẫn rõ ràng, thực tiễn nhất quán | "Theo [văn bản X], khoản X không chịu thuế..." |
| **Trung bình** | Có căn cứ pháp lý nhưng có thể diễn giải nhiều cách | "Chúng tôi cho rằng... mặc dù CQT có thể lập luận..." |
| **Cao** | Grey area, không có hướng dẫn rõ, thực tiễn không nhất quán | "Không có hướng dẫn chính thức; rủi ro bị CQT ấn định là đáng kể. Khuyến nghị xin Ruling" |
| **Rất cao** | Rõ ràng phát sinh nghĩa vụ thuế nhưng chưa được kê khai | Nêu rõ nghĩa vụ + khuyến nghị tự nguyện điều chỉnh |

### Xử lý Grey Area — Trình bày 2 chiều

Khi có tranh chấp diễn giải, trình bày đủ 2 lập trường:

```markdown
**Lập luận ủng hộ lợi ích của khách hàng:**
[Trích dẫn căn cứ + phân tích tại sao khoản X không chịu thuế]

**Lập luận có thể được CQT sử dụng:**
[CQT có thể lập luận rằng... dựa trên [văn bản Y]...]

**Đánh giá rủi ro:**
[Ước lượng xác suất bị CQT bác: Thấp / Trung bình / Cao]
[Giá trị rủi ro tài chính: X triệu đồng + phạt + lãi]

**Khuyến nghị:**
[Hành động cụ thể + lý do]
```

---

## E. Xử lý Bất định (Uncertainty Handling)

### Các loại bất định và cách xử lý

**Bất định về quy định pháp luật:**
- Chưa có hướng dẫn chính thức cho tình huống cụ thể
- Văn bản pháp luật mâu thuẫn nhau
- Xử lý: Ghi rõ "Chưa có hướng dẫn chính thức về vấn đề này tại thời điểm soạn thảo"; đề xuất xin Ruling (tham vấn CQT); trình bày lập luận theo tinh thần tốt nhất

**Bất định về sự kiện:**
- Thông tin khách hàng cung cấp chưa đủ hoặc chưa được xác minh
- Xử lý: Nêu rõ giả định đã sử dụng; đề nghị khách hàng xác nhận trước khi kết luận có hiệu lực

**Bất định về hiệu lực văn bản:**
- Không chắc văn bản còn hiệu lực hay đã bị thay thế
- Xử lý: Ghi chú "(cần xác minh hiệu lực tại thời điểm áp dụng)"; không trích dẫn như căn cứ chắc chắn

### Lệnh Cấm Tuyệt đối

> **KHÔNG ĐƯỢC:**
> - Tự sáng tạo quy định pháp luật không tồn tại
> - Trích dẫn số văn bản sai hoặc điều khoản không đúng
> - Kết luận dứt khoát khi pháp lý rõ ràng chưa có căn cứ
> - Bỏ qua rủi ro để memo trông có lợi hơn cho khách hàng
>
> **KHI KHÔNG ĐỦ NGUỒN:** Trả lời "Insufficient source coverage" và ghi rõ lý do — đừng fabricate.

---

## F. Review Checklist (SA và Partner)

### SA Review — Kiểm tra Pháp lý

**Trích dẫn và Căn cứ:**
- [ ] Mỗi kết luận pháp lý có ít nhất 1 văn bản quy phạm cụ thể?
- [ ] Số văn bản, điều, khoản, điểm được trích dẫn đầy đủ?
- [ ] Tất cả văn bản được trích dẫn còn hiệu lực?
- [ ] Không có văn bản nào đã bị thay thế mà không được ghi chú?

**Logic và Nhất quán:**
- [ ] Logic phân tích IRAC nhất quán cho từng vấn đề?
- [ ] Không có mâu thuẫn giữa các kết luận trong cùng memo?
- [ ] Giả định được nêu rõ ràng?
- [ ] Kết luận phù hợp với phân tích (không bị nhảy cóc)?

**Rủi ro và Đầy đủ:**
- [ ] Tất cả rủi ro quan trọng đã được nêu?
- [ ] Không có vấn đề nào bị bỏ sót trong issue spotting?
- [ ] Uncertainty được xử lý đúng (không kết luận vượt quá căn cứ)?

**Số liệu và Tính toán (nếu có):**
- [ ] Tính toán số thuế đúng (công thức, thuế suất)?
- [ ] Đơn vị nhất quán (triệu đồng, USD...)?
- [ ] Ví dụ tính toán được kiểm tra độc lập?

### Partner Review — Kiểm tra Chất lượng Tổng thể

**Phù hợp với khách hàng:**
- [ ] Tone và văn phong phù hợp với loại khách hàng (tập đoàn lớn / SME / cá nhân)?
- [ ] Ngôn ngữ có quá kỹ thuật hoặc quá đơn giản?
- [ ] Khách hàng có đủ thông tin để ra quyết định không?

**Executive Summary:**
- [ ] Có đủ 3 yếu tố: Vấn đề + Kết luận + Khuyến nghị hành động ngay?
- [ ] Người ra quyết định đọc Summary xong có hiểu ngay không?
- [ ] Không có thông tin kỹ thuật không cần thiết trong Summary?

**Khuyến nghị:**
- [ ] Khuyến nghị có khả thi và thực tế trong hoàn cảnh của khách hàng?
- [ ] Timeline của khuyến nghị hành động có cụ thể (ngày, tuần)?
- [ ] Có phân loại: hành động cần làm ngay / trung hạn / dài hạn?

**Escalation:**
- [ ] Cần Managing Partner sign-off không? (memo ≥5 tỷ rủi ro, hoặc cấu trúc giao dịch M&A, hoặc vấn đề criminal tax risk)
- [ ] Cần xác nhận thêm từ CQT (xin Ruling) không?
- [ ] Cần tư vấn chuyên ngành khác (luật sư, kiểm toán) không?

---

## G. Bàn giao (Delivery Standards)

### Yêu cầu Định dạng

| Yếu tố | Yêu cầu |
|--------|---------|
| Định dạng file | PDF (bản phát hành chính thức); Word (nếu khách hàng yêu cầu edit) |
| Letterhead | Có logo, địa chỉ công ty, thông tin liên lạc của người tư vấn |
| Font và layout | Nhất quán với template chuẩn của hãng |
| Đánh số trang | Có số trang; có mục lục nếu memo >10 trang |
| Tham chiếu | Mã hồ sơ + ngày phát hành + số phiên bản |

### Thông tin Bắt buộc trên Memo

```
TIÊU ĐỀ: TƯ VẤN THUẾ — [Chủ đề]
KÍNH GỬI: [Tên khách hàng / Chức danh]
NGÀY: [DD/MM/YYYY]
THAM CHIẾU: [Mã hồ sơ] / Phiên bản [X.X]
BÍ MẬT: Văn bản này chỉ dành cho khách hàng được đề cập và không được chia sẻ cho bên thứ ba
         mà không có sự đồng ý bằng văn bản của [Tên hãng tư vấn]
```

### Disclaimer Bắt buộc (cuối memo)

> Tư vấn này được cung cấp dựa trên thông tin và tài liệu do Khách hàng cung cấp, cũng như các văn bản pháp luật hiện hành tại thời điểm phát hành. Tư vấn có thể thay đổi khi có quy định pháp luật mới hoặc khi có thêm thông tin từ phía Khách hàng. Tư vấn này không thay thế cho ý kiến pháp lý chính thức và Khách hàng nên xác nhận với cơ quan thuế có thẩm quyền trước khi thực hiện. [Tên hãng tư vấn] không chịu trách nhiệm về bất kỳ quyết định kinh doanh nào được đưa ra dựa trên tư vấn này mà không có sự xác nhận bổ sung.

### Lưu trữ Hồ sơ

| Nội dung | Thời gian lưu | Vị trí |
|---------|--------------|--------|
| Memo phát hành (PDF final) | 10 năm | Hệ thống lưu trữ nội bộ |
| Draft các phiên bản | 5 năm | Hệ thống lưu trữ nội bộ |
| Tài liệu khách hàng cung cấp | 10 năm (theo Luật Kế toán) | Hệ thống lưu trữ nội bộ |
| Email trao đổi liên quan | 5 năm | Email archive |
| Ghi chú nghiên cứu pháp lý | 5 năm | Hệ thống lưu trữ nội bộ |

---

## H. Phân loại Advisory theo Độ phức tạp

| Loại | Đặc điểm | Thời gian chuẩn | Người phụ trách |
|------|---------|----------------|----------------|
| **Standard** | 1–2 vấn đề, có văn bản hướng dẫn rõ | 1–2 ngày | JA + SA review |
| **Complex** | 3+ vấn đề hoặc có grey area đáng kể | 3–5 ngày | JA + SA + Partner review |
| **Deep** | Cơ cấu giao dịch, M&A, restructuring | 1–3 tuần | SA/Partner lead + JA support |
| **Urgent** | Cần trong <24 giờ | Ưu tiên tối đa | SA lead; Partner sign-off nhanh |

> **Lưu ý Urgent Advisory:** Không giảm chất lượng review vì deadline. Nếu không đủ thời gian để review đầy đủ → phát hành "Preliminary Advice" với ghi chú rõ là sơ bộ, cần xác nhận thêm.
