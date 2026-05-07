# SKILL TEMPLATE GUIDE — TaxLegal AI

> Tài liệu hướng dẫn nội bộ. Không phải skill. Không inject vào system prompt.

---

## Overview

Hướng dẫn tạo skill mới cho hệ thống TaxLegal AI. Skills được inject **toàn bộ** vào system prompt dưới section `## SKILLS ACTIVATED` trong mỗi pipeline step.

Mỗi skill là một file `.md` gồm hai phần:
1. **YAML frontmatter** (`---` ... `---`): metadata để hệ thống phân loại, gán bot, và lọc skill
2. **Markdown body**: nội dung kỹ thuật được inject vào prompt

Chất lượng của skill quyết định trực tiếp chất lượng đầu ra của AI. Một skill tốt = AI đưa ra vị trí thuế chính xác, có trích dẫn, và nhất quán.

---

## Skill Taxonomy (từ kiến trúc openaccountants)

Mỗi skill thuộc một trong 5 category chức năng:

| # | Category | Mục đích | Ví dụ |
|---|---------|---------|-------|
| 1 | **Intake** | Checklist làm rõ thông tin, template thu thập dữ liệu đầu vào | Intake checklist cho FCT khi chưa rõ loại dịch vụ |
| 2 | **Computation** | Bảng thuế suất, công thức tính toán, kiểm tra ngưỡng | Tính giá tính TTĐB, tính IQR transfer pricing |
| 3 | **Decision Support** | Phân tích kịch bản, cờ rủi ro, mặc định thận trọng | Quyết định áp dụng DTA hay không |
| 4 | **Return Assembly** | Checklist kê khai, lịch deadline, mapping mẫu tờ khai | Checklist quyết toán CIT năm |
| 5 | **Advisory Memo** | Template phân tích đầu ra có cấu trúc | Memo phân tích rủi ro TP cho khách hàng FDI |

Một file skill có thể bao gồm nhiều category (ví dụ: vietnam-fct.md bao gồm cả Computation + Decision Support + Return Assembly).

---

## Frontmatter Fields

Tất cả các trường YAML frontmatter hợp lệ:

| Trường | Kiểu | Bắt buộc | Mô tả | Ví dụ |
|--------|------|---------|-------|-------|
| `name` | string | ✅ | Slug duy nhất, viết thường, dùng dấu gạch nối | `vietnam-fct` |
| `version` | semver | ✅ | Phiên bản skill | `1.0.0` |
| `description` | string | ✅ | Mô tả một dòng (hoặc block `>`) | `Vietnam FCT — withholding tax on payments to foreign entities` |
| `category` | enum | ✅ | `tax` \| `legal` \| `compliance` \| `advisory` | `tax` |
| `tags` | list | ✅ | Từ khóa viết thường để tìm kiếm | `[fct, withholding-tax, vietnam]` |
| `applicable_bots` | list | ✅ | Bot roles được dùng skill này | `[partner, ja, sa]` |
| `editable` | boolean | ❌ | Cho phép admin chỉnh sửa qua UI | `true` |

### Bot Roles

| Role | Viết tắt | Mô tả |
|------|---------|-------|
| `intake` | Intake Bot | Thu thập thông tin từ khách hàng |
| `partner` | Partner Bot | Phân tích pháp lý chuyên sâu, ra vị trí thuế |
| `sa` | Senior Associate Bot | Nghiên cứu, phân tích, dự thảo memo |
| `ja` | Junior Associate Bot | Tra cứu căn cứ pháp lý, tính toán đơn giản |

### Ví dụ frontmatter đầy đủ

```yaml
---
name: vietnam-fct
version: 1.0.0
description: >
  Vietnam Foreign Contractor Tax (FCT) — withholding tax on payments to foreign entities.
  Covers Circular 103/2014/TT-BTC, taxable subjects, VAT + CIT rates, three payment methods,
  DTA override, and conservative defaults for uncertain cases.
category: tax
tags: [fct, withholding-tax, foreign-contractor, vietnam, circular-103]
applicable_bots: [partner, ja, sa]
editable: true
---
```

---

## Conservative Defaults Principle (Nguyên tắc Mặc định Thận trọng)

**Mọi skill phải có section này.** Đây là "hợp đồng 3 trạng thái" của AI:

| Trạng thái | Điều kiện | Hành động của AI |
|-----------|----------|-----------------|
| ✅ **Clean** | Luật rõ ràng + dữ kiện đầy đủ | Đưa ra vị trí dứt khoát, trích dẫn điều khoản cụ thể |
| ⚠️ **Conservative Default** | Luật hoặc dữ kiện không chắc chắn | Chọn phương án **tốn thuế hơn** (bảo vệ khách hàng khỏi rủi ro nộp thiếu) |
| 🚫 **Refuse** | Thiếu dữ kiện cơ bản để phân tích | Yêu cầu làm rõ trước khi đưa ra bất kỳ vị trí nào |

**Lý do**: Chi phí của "phạt nộp thiếu thuế" thường cao hơn chi phí của "nộp thừa thuế". AI phải bảo vệ khách hàng theo hướng an toàn hơn khi không chắc chắn.

**Ví dụ áp dụng trong skill FCT:**
```markdown
| Không xác định được loại dịch vụ | Áp dụng CIT 10% (mức cao nhất) |
| Không có chứng nhận cư trú DTA   | Không áp dụng DTA — khấu trừ nội địa |
```

---

## Citation Discipline (Kỷ luật Trích dẫn)

**Quy tắc vàng**: Mọi vị trí thuế đều phải có trích dẫn. Không có trích dẫn = không có vị trí.

### Cấu trúc trích dẫn bắt buộc

```
1. Nguồn sơ cấp:  [Tên luật/nghị định/thông tư] + [Điều/Khoản/Điểm cụ thể]
2. Nguồn thứ cấp: Công văn hướng dẫn của TCT/BTC (nếu có)
```

### Ví dụ trích dẫn đúng

```markdown
Chi phí lãi vay liên kết không được vượt quá 30% EBITDA 
(Điều 16, Nghị định 132/2020/NĐ-CP).
```

### Ví dụ trích dẫn sai (không chấp nhận)

```markdown
Chi phí lãi vay liên kết bị giới hạn.     ← Không có căn cứ pháp lý
Chi phí lãi vay liên kết không được vượt 30% EBITDA theo quy định.  ← Thiếu số hiệu
```

### Bảng trích dẫn trong skill

Mỗi skill nên có bảng **Khung pháp lý hiện hành** ở đầu:

```markdown
| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Thông tư FCT | 103/2014/TT-BTC | Quy định chính về thuế nhà thầu |
```

---

## Body Structure Template

Cấu trúc chuẩn cho mọi skill (thứ tự section, không bỏ qua):

```markdown
# Skill: [Tên đầy đủ] — Việt Nam

## Khung pháp lý hiện hành
Bảng tham chiếu luật/nghị định/thông tư liên quan, có số hiệu.

## [Tên chủ đề chính 1]
Quy tắc cốt lõi, định nghĩa, điều kiện áp dụng.

## Bảng thuế suất / Công thức tính (nếu có)
Bảng thuế suất đầy đủ + ví dụ tính toán.

## Nguyên tắc Mặc định Thận trọng (Conservative Defaults)
Bảng tình huống → mặc định thận trọng.

## Lịch tuân thủ / Deadline (nếu có)
Bảng deadline kê khai và nộp thuế.

## Checklist thực hành
Danh sách checkbox để JA/SA kiểm tra.
```

### Các section tùy chọn (thêm khi phù hợp)

- `## Ví dụ tính toán` — walkthrough số liệu cụ thể
- `## Trường hợp đặc biệt / Ngoại lệ`
- `## Rủi ro thường gặp`
- `## Quy trình thủ tục` — các bước hành chính

---

## Example: Minimal Skill

Ví dụ skill tối thiểu hợp lệ (dùng FCT làm minh họa):

```markdown
---
name: vietnam-fct-minimal
version: 1.0.0
description: FCT minimal example — withholding on payments to foreign contractors
category: tax
tags: [fct, vietnam]
applicable_bots: [ja]
editable: true
---

# Skill: Thuế Nhà thầu (FCT) — Tóm tắt

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Thông tư FCT | 103/2014/TT-BTC | Quy định chính về thuế nhà thầu |

## Mức thuế suất mặc định

Khi không xác định được phân loại dịch vụ:
- VAT: **5%** trên doanh thu
- CIT: **5%** trên doanh thu

Mức tổng hợp mặc định: **10% trên doanh thu thanh toán**.

## Nguyên tắc Mặc định Thận trọng

| Tình huống | Mặc định |
|-----------|---------|
| Không rõ loại dịch vụ | CIT 10% (mức cao nhất) |
| Không có DTA / chứng nhận cư trú | Áp dụng thuế nội địa đầy đủ |

## Checklist thực hành

- [ ] Xác định phương pháp nộp (PP1/PP2/PP3)
- [ ] Khai và nộp trong 10 ngày kể từ ngày trả tiền (PP1)
```

---

## Linking Skills to BotVariants

### Kiến trúc hệ thống

```
Skill file (.md)
    ↓  gán qua Admin UI hoặc config
BotVariant (e.g. "partner-bot-v2")
    ↓  sử dụng trong
PipelineTemplate Step (e.g. "analysis-step")
    ↓  inject vào
System Prompt → AI nhận được skill content
```

### Quy trình gán skill

1. **Admin → Skills**: Upload hoặc chỉnh sửa file skill `.md`
2. **Admin → BotVariants**: Chọn BotVariant cần gán skill
3. **Assign Skills**: Chọn skill từ danh sách (lọc theo `applicable_bots`)
4. **BotVariant → PipelineTemplate**: Gán BotVariant vào step cụ thể trong pipeline

### Quy tắc gán skill theo bot role

| BotVariant | Skills nên gán |
|-----------|---------------|
| `intake-bot` | Skills category `intake`, checklist thu thập thông tin |
| `ja-bot` | Skills computation, rate tables, deadline calendars |
| `sa-bot` | Skills computation + decision support + return assembly |
| `partner-bot` | Tất cả skills liên quan + advisory memo templates |

### Lưu ý version control

- Mỗi khi cập nhật nội dung skill, tăng version theo semver (`1.0.0` → `1.1.0` cho minor update, `2.0.0` cho breaking change)
- Ghi chú thay đổi trong comment đầu file hoặc CHANGELOG riêng
- Kiểm tra lại các BotVariant đang dùng skill sau mỗi lần cập nhật lớn

---

## Quy trình Review Skill mới

Trước khi deploy skill vào production:

1. **Technical review**: Kiểm tra frontmatter đúng schema, markdown render đúng
2. **Legal review**: Partner review tất cả vị trí thuế và trích dẫn
3. **Conservative defaults**: Xác nhận bảng mặc định thận trọng đầy đủ và đúng hướng
4. **Test prompt**: Chạy thử skill trong môi trường staging với 3–5 câu hỏi điển hình
5. **Deploy**: Gán skill vào BotVariant tương ứng

---

*Tài liệu này được duy trì bởi nhóm TaxLegal AI. Cập nhật lần cuối: 2025.*
