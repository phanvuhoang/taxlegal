---
name: vietnam-intl-tax
version: 1.0.0
description: >
  Skill về Thuế quốc tế Việt Nam — quy định đối với nhà đầu tư nước ngoài, cơ sở thường trú,
  thuế đối với thu nhập từ nước ngoài, thuế nhà thầu, tín dụng thuế nước ngoài,
  và các vấn đề xuyên biên giới phổ biến.
category: tax
tags: [international-tax, cross-border, PE, foreign-investor, FTC, CFC, BEPS, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Thuế Quốc tế — Việt Nam (International Tax)

## Tổng quan

Thuế quốc tế Việt Nam điều chỉnh hai chiều:
1. **Inbound:** Nhà đầu tư/doanh nghiệp nước ngoài hoạt động tại VN → TNDN, FCT, PE
2. **Outbound:** Doanh nghiệp VN có thu nhập từ nước ngoài → FTC, CFC (đang phát triển)

Nguồn pháp lý chính: Luật TNDN (số 14/2008, sửa nhiều lần); Thông tư 103/2014/TT-BTC (FCT); Thông tư 78/2014, 96/2015 (CIT); các Hiệp định tránh đánh thuế hai lần (DTA) từng nước.

---

## A. Cơ sở thường trú (PE — Permanent Establishment)

### Định nghĩa PE theo Luật TNDN Việt Nam

Theo Điều 2, Luật TNDN 14/2008 (sửa đổi), tổ chức nước ngoài có cơ sở thường trú tại VN nếu có:
- Nơi quản lý, chi nhánh, văn phòng, nhà máy, xưởng sản xuất, kho hàng
- Công trình xây dựng, lắp đặt, thăm dò, khai thác tài nguyên
- Đại lý tại VN có thẩm quyền ký kết hợp đồng thay mặt
- Đại diện tại VN thực hiện cung cấp dịch vụ (kể cả dịch vụ tư vấn) trong thời gian **tổng cộng ≥90 ngày trong 12 tháng liên tục**

### Định nghĩa PE theo Hiệp định DTA

Hầu hết DTA Việt Nam ký theo mẫu OECD — ngưỡng PE thường dài hơn:

| Loại PE | Ngưỡng thời gian thông thường | Ghi chú |
|---------|------------------------------|---------|
| PE nơi kinh doanh cố định | Không có ngưỡng thời gian | Tồn tại là đủ |
| PE xây dựng (Construction PE) | >6 tháng (OECD model) hoặc >183 ngày | Tùy từng DTA cụ thể |
| PE dịch vụ (Service PE) | >183 ngày trong 12 tháng | Theo DTA mới; DTA cũ có thể khác |
| PE đại lý phụ thuộc | Không có ngưỡng — phụ thuộc vào quyền ký HĐ | |

> **Nguyên tắc áp dụng:** DTA được ưu tiên áp dụng so với Luật nội địa. Nếu DTA có ngưỡng PE cao hơn (ví dụ 183 ngày), doanh nghiệp nước ngoài được hưởng ngưỡng đó.

### Hậu quả khi có PE tại Việt Nam

| Hậu quả | Mô tả |
|---------|-------|
| Phải kê khai TNDN tại VN | Tính trên thu nhập phát sinh từ hoạt động của PE |
| Phương pháp tính thuế | Thường áp dụng phương pháp tỷ lệ (% doanh thu VN × tỷ lệ lợi nhuận giả định) theo TT103 |
| Phải đăng ký thuế | Xin MST tại cơ quan thuế địa phương |
| VAT nhà thầu (FCT-VAT) | Áp dụng song song nếu phát sinh doanh thu dịch vụ tại VN |

**Phương pháp tính TNDN cho PE theo TT103:**
```
TNDN phải nộp = Doanh thu phát sinh tại VN × Tỷ lệ lợi nhuận tính thuế × Thuế suất TNDN (20%)
```
Tỷ lệ lợi nhuận tính thuế theo TT103: thương mại 1%, dịch vụ 5%, xây dựng lắp đặt 2%, vận tải 2%, hoạt động khác 2%.

### Red Flags — Rủi ro PE thường bị bỏ qua

| Tình huống | Rủi ro PE |
|-----------|----------|
| Văn phòng đại diện (VPĐD) thực hiện đàm phán HĐ thay mặt công ty mẹ | VPĐD chuyển thành PE — VPĐD chỉ được thực hiện hoạt động xúc tiến, không được ký HĐ |
| Nhân viên cư trú tại VN có thẩm quyền ký HĐ ràng buộc công ty nước ngoài | → Đại lý phụ thuộc → PE |
| Chuyên gia nước ngoài làm việc tại VN >90 ngày cho khách hàng VN | → Service PE (nếu DTA không áp dụng hoặc ngưỡng thấp hơn) |
| Dự án xây dựng/lắp đặt vượt ngưỡng thời gian | → Construction PE |
| Công ty con VN kinh doanh toàn bộ cho công ty mẹ nước ngoài | → Rủi ro PE ẩn qua subsidiary |

---

## B. Thuế đối với Thu nhập từ Nước ngoài (Outbound)

### Doanh nghiệp VN có thu nhập từ đầu tư/hoạt động ở nước ngoài

Theo Điều 2, Luật TNDN: Thu nhập của DN VN từ mọi nguồn, kể cả thu nhập từ nước ngoài, đều phải kê khai vào TNDN tại VN.

**Các loại thu nhập từ nước ngoài phổ biến:**
- Lợi nhuận từ công ty con/liên doanh ở nước ngoài (khi chia cổ tức)
- Thu nhập từ chuyển nhượng vốn/cổ phần tại nước ngoài
- Tiền bản quyền nhận từ nước ngoài
- Thu nhập từ cho thuê tài sản ở nước ngoài
- Lãi tiền gửi/tiền cho vay tại ngân hàng nước ngoài

### Tín dụng thuế nước ngoài (Foreign Tax Credit — FTC)

**Căn cứ pháp lý:** Điều 22, Luật TNDN; Điều 8, NĐ 218/2013/NĐ-CP; Điều 24, TT 78/2014/TT-BTC.

**Nguyên tắc FTC:**
1. Doanh nghiệp VN được **khấu trừ** số thuế thu nhập đã nộp ở nước ngoài vào số TNDN phải nộp tại VN
2. Số thuế được khấu trừ **không vượt quá** số TNDN VN tính trên khoản thu nhập đó

**Điều kiện FTC:**
- Có chứng từ nộp thuế hợp pháp tại nước ngoài (đã được nộp thực tế, không phải thuế nước ngoài được miễn/giảm)
- Được kê khai trong tờ khai TNDN VN (Phụ lục I-3 hoặc tương đương)
- Thực hiện trong kỳ tính thuế phát sinh thu nhập

**Ví dụ tính FTC:**
```
Thu nhập từ cổ tức công ty con Singapore: 1.000.000 USD
Thuế đã nộp tại Singapore: 50.000 USD (5%)
TNDN VN trên khoản thu nhập này: 1.000.000 × 20% = 200.000 USD
FTC được khấu trừ: min(50.000, 200.000) = 50.000 USD
TNDN phải nộp tại VN: 200.000 - 50.000 = 150.000 USD
```

**Lưu ý:** Nếu thuế nước ngoài được miễn theo treaty hoặc ưu đãi đầu tư → phần được miễn không được tính vào FTC.

---

## C. BEPS và Pillar Two / GloBE Rules

### Tổng quan Pillar Two

Pillar Two (Global Anti-Base Erosion — GloBE) là cơ chế thuế tối thiểu toàn cầu 15% do OECD/G20 phát triển. Áp dụng cho tập đoàn đa quốc gia (MNE) có doanh thu hợp nhất **≥ 750 triệu EUR** trong 2 trong 4 năm gần nhất.

### Việt Nam và Pillar Two

**Trạng thái hiện tại:**
- Việt Nam đã thông qua Nghị quyết về áp dụng thuế tối thiểu toàn cầu (Nghị quyết 107/2023/QH15)
- Hiệu lực từ ngày **01/01/2024**
- Áp dụng hai cơ chế: **QDMTT** (Qualified Domestic Minimum Top-up Tax) và **IIR** (Income Inclusion Rule) theo giai đoạn

**QDMTT — Thuế bổ sung tối thiểu nội địa:**
- Khi lợi nhuận của MNE tại VN chịu thuế hiệu dụng (ETR) < 15% → Việt Nam thu thêm phần chênh lệch
- Công thức: Top-up Tax = (15% − ETR) × Excess Profit
- Excess Profit = GloBE Income − Substance-Based Income Exclusion (SBIE)

**SBIE (Loại trừ thu nhập dựa trên hoạt động thực chất):**
- 5% × Giá trị tài sản hữu hình + 5% × Chi phí nhân sự (giai đoạn đầu áp dụng; giảm dần)

**Đối tượng áp dụng tại Việt Nam:**
- MNE có doanh thu hợp nhất ≥ 750 triệu EUR/năm
- Có ít nhất 1 pháp nhân/cơ sở thường trú tại VN

**⚠️ Lưu ý quan trọng:** Các hướng dẫn cụ thể (Nghị định, Thông tư) về QDMTT vẫn đang trong quá trình ban hành. **Xác nhận văn bản mới nhất trước khi tư vấn.** Đây là lĩnh vực đang thay đổi nhanh.

**Tác động thực tế:**
- DN FDI hưởng ưu đãi TNDN (thuế suất 10%, 15%) có ETR < 15% → bị thu top-up tax
- Ưu đãi TNDN VN không bị mất nhưng lợi ích thực tế bị giảm đáng kể
- Cần rà soát lại cấu trúc đầu tư, phân bổ lợi nhuận giữa các jurisdiction

---

## D. Thuế khấu lưu tại nguồn (Withholding Tax / FCT)

### Bảng tóm tắt FCT theo TT103/2014

| Loại thu nhập | FCT CIT | FCT VAT | Tổng FCT | Ghi chú |
|--------------|---------|---------|----------|---------|
| Lãi vay trả nước ngoài | 5% | 0% | 5% | Lãi vay thông thường |
| Tiền bản quyền | 10% | 0% | 10% | Tính trên doanh thu bản quyền |
| Phí dịch vụ kỹ thuật | 5% | 5% | 10% | Khấu trừ + nộp thay |
| Phí quản lý | 5% | 5% | 10% | |
| Phí tư vấn (DV thuần) | 5% | 5% | 10% | Nếu DV thực hiện tại VN |
| Cổ tức (pháp nhân nhận) | 0% | 0% | 0% | Miễn theo Luật TNDN |
| Cổ tức (cá nhân nhận) | 5% PIT | 0% | 5% | PIT, không phải CIT |
| Chuyển nhượng vốn (pháp nhân) | 20% | 0% | 20% | Trên lãi chuyển nhượng |
| Chuyển nhượng vốn (cá nhân) | 20% hoặc 0,1% | 0% | | 20% trên lãi hoặc 0,1% trên giá chuyển nhượng |

### Giảm FCT theo DTA

Khi có DTA áp dụng, mức FCT có thể được giảm:

| Loại thu nhập | Mức FCT thông thường | Mức DTA thông thường |
|--------------|---------------------|---------------------|
| Cổ tức (cho DN) | 0% (nội địa) | 5–15% (từ nước ngoài về VN) |
| Lãi vay | 5% | 0–10% tùy DTA |
| Tiền bản quyền | 10% | 5–15% tùy DTA |

**Điều kiện hưởng DTA rate:** Người nhận phải là beneficial owner và cư trú thuế tại nước ký DTA.

### Phương pháp kê khai FCT

**Phương pháp 1 — Khấu trừ (DN VN nộp thay):**
- Áp dụng khi: nhà thầu nước ngoài không đăng ký kê khai thuế tại VN
- DN VN tính, khấu trừ và nộp thay FCT khi thanh toán cho nhà thầu nước ngoài

**Phương pháp 2 — Trực tiếp (Nhà thầu NN kê khai):**
- Áp dụng khi: nhà thầu nước ngoài đăng ký thuế và kê khai trực tiếp tại VN
- Thường áp dụng khi nhà thầu có dự án dài hạn, có PE

---

## E. Chuyển nhượng vốn xuyên biên giới

### Chuyển nhượng vốn trực tiếp (Direct Transfer)

Nhà đầu tư nước ngoài chuyển nhượng phần vốn trong DN VN:
- **Pháp nhân nước ngoài:** Chịu TNDN 20% trên lãi chuyển nhượng (giá bán − giá vốn − chi phí liên quan)
- **Cá nhân không cư trú:** 20% trên lãi hoặc 0,1% trên giá bán (tùy lựa chọn)
- Kê khai: bên mua (thường là DN VN) có trách nhiệm khấu trừ và nộp thay nếu bên bán là tổ chức/cá nhân nước ngoài

### Chuyển nhượng vốn gián tiếp (Indirect Transfer)

**Tình huống:** Công ty A (Singapore) sở hữu Công ty B (Singapore) → Công ty B sở hữu 100% Công ty C (VN). Công ty A bán toàn bộ cổ phần Công ty B cho Công ty D (Hàn Quốc).

**Vấn đề:** Thực chất là chuyển nhượng tài sản tại VN (qua Công ty B) nhưng giao dịch xảy ra tại Singapore.

**Quan điểm Việt Nam:**
- Theo Điều 36, Luật Đầu tư và Điều 39, Luật Quản lý Thuế: Việt Nam có quyền đánh thuế nếu tài sản cơ bản là ở VN và giao dịch nhằm mục đích chuyển giao lợi ích kinh tế từ VN
- Thực thi còn hạn chế nhưng đang được CQT tăng cường chú ý

**Hồ sơ liên quan:**
- Tờ khai chuyển nhượng vốn (Mẫu 05/TNDN hoặc FCT tương đương)
- Thông báo chuyển nhượng gửi CQT nơi DN VN đăng ký
- Phân bổ giá mua (purchase price allocation) để xác định phần giá trị từ tài sản VN

**Rủi ro:** Nếu không kê khai indirect transfer → bị phạt vi phạm pháp luật thuế, có thể phát sinh nghĩa vụ TNDN lớn.

---

## F. Beneficial Ownership

### Khái niệm và tầm quan trọng

"Beneficial owner" (người thụ hưởng thực sự) là điều kiện để được áp dụng mức thuế DTA. Người nhận thu nhập (danh nghĩa) khác với người thực sự hưởng lợi → không được hưởng DTA rate.

**Ví dụ treaty shopping:**
- Công ty mẹ (Mỹ, không có DTA tốt với VN) → lập công ty trung gian tại Singapore (có DTA tốt với VN) → đầu tư vào VN
- Công ty Singapore chỉ là conduit, thực chất toàn bộ thu nhập chuyển về Mỹ
- → Công ty Singapore không phải beneficial owner → không được hưởng DTA VN-Singapore

**Kiểm tra beneficial ownership:**
- Công ty có hoạt động kinh doanh thực chất tại nước ký DTA không?
- Có kiểm soát thực sự thu nhập hay phải chuyển tiếp cho bên khác?
- Có nhân sự, văn phòng, tài sản thực tế không?

**Quan điểm CQT VN:** Đang tham chiếu OECD Commentary 2014+ và bắt đầu áp dụng Principal Purpose Test (PPT) theo MLI (Multilateral Instrument). Các DN có cấu trúc đầu tư qua nước trung gian cần chuẩn bị tài liệu chứng minh substance.

---

## G. Các vấn đề Cross-border phổ biến

### 1. SaaS và dịch vụ kỹ thuật số xuyên biên giới

**Câu hỏi:** DN VN mua phần mềm SaaS từ công ty Mỹ → có phải nộp FCT không?

**Phân tích:**
- Nếu phân loại là "tiền bản quyền" (royalty) → FCT 10% CIT
- Nếu phân loại là "phí dịch vụ" (service fee) → FCT 5% CIT + 5% VAT
- Thực tế: CQT VN thường phân loại SaaS và phần mềm truy cập online là royalty → 10%
- Nếu có DTA VN-Mỹ: **Không có** (Mỹ chưa ký DTA với VN) → áp dụng FCT đầy đủ

**Khuyến nghị:** Xem xét cơ cấu hợp đồng để phân loại đúng; kiểm tra DTA nếu vendor ở nước khác.

### 2. Nhân sự đa quốc gia và Equity Compensation

**Tình huống:** Nhân viên VN nhận stock options từ công ty mẹ nước ngoài.

**Vấn đề thuế phát sinh:**
- PIT tại VN khi exercise (xem chi tiết tại `pit-advanced.md`)
- Phân bổ thu nhập theo thời gian phục vụ tại VN (vesting period)
- Công ty mẹ nước ngoài có PE risk tại VN qua việc bồi thường nhân viên?

### 3. Holding Structure và Tái cơ cấu

**Cấu trúc thường gặp:**
- Singapore Holdco → Vietnam Opco: thường được chọn vì DTA VN-Singapore, hệ thống pháp lý minh bạch
- Repatriation qua cổ tức: miễn thuế TNDN tại VN; có thể chịu withholding tax tại Singapore khi nhận lại
- Giảm vốn thay vì cổ tức: cần phân tích thuế cẩn thận — một phần có thể bị xem là chuyển nhượng vốn

### 4. Chiến lược Repatriation

| Phương thức | Thuế tại VN | Thuế tại nước nhận | Ghi chú |
|------------|------------|-------------------|---------|
| Cổ tức (pháp nhân) | 0% | Tùy DTA | Phổ biến nhất |
| Giảm vốn | Phần vượt vốn góp → chuyển nhượng vốn 20% | Tùy | Phức tạp hơn |
| Thu hồi khoản vay | Không chịu thuế (hoàn vốn gốc) | Không | Phải có hợp đồng vay hợp lệ |
| Lãi vay | FCT 5% (CIT) tại VN | Tùy DTA | Cần arm's length |

---

## Checklist International Tax

**Bước 1 — Xác định tư cách và cơ cấu:**
- [ ] Các bên là pháp nhân hay cá nhân? Cư trú thuế ở đâu?
- [ ] Có DTA giữa VN và nước của bên đối tác không?
- [ ] Beneficial ownership test — bên hưởng DTA có phải beneficial owner không?

**Bước 2 — PE Analysis:**
- [ ] Bên nước ngoài có hoạt động tại VN không? (nhân viên, văn phòng, dự án)
- [ ] Thời gian hoạt động → vượt ngưỡng PE chưa?
- [ ] VPĐD có thực hiện đàm phán/ký HĐ không?

**Bước 3 — FCT và Withholding:**
- [ ] Loại thu nhập → phân loại theo TT103 (royalty, service, interest, dividend?)
- [ ] FCT rate đúng chưa? Có DTA reduction không?
- [ ] Phương pháp kê khai FCT: khấu trừ hay trực tiếp?

**Bước 4 — Outbound Tax (nếu DN VN có thu nhập nước ngoài):**
- [ ] Thu nhập nước ngoài đã được kê khai vào TNDN VN chưa?
- [ ] FTC claim: có chứng từ nộp thuế nước ngoài hợp lệ không?
- [ ] Tính FTC không vượt TNDN VN trên khoản thu nhập đó?

**Bước 5 — BEPS/Pillar Two:**
- [ ] Tập đoàn có doanh thu ≥ 750 triệu EUR không?
- [ ] ETR tại VN < 15% không?
- [ ] Đã tính QDMTT top-up obligation chưa?

**Bước 6 — Chuyển nhượng vốn:**
- [ ] Giao dịch có yếu tố indirect transfer không?
- [ ] Đã thông báo CQT về giao dịch chuyển nhượng chưa?
- [ ] Purchase price allocation đã xác định phần tài sản VN chưa?
