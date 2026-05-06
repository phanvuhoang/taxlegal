---
name: SKILL-TEMPLATE-GUIDE
version: 1.0.0
description: >
  Hướng dẫn tạo skill mới cho TaxLegal AI — format chuẩn, các section bắt buộc,
  tips để viết skill hiệu quả. Tham khảo trước khi tạo skill mới.
category: guide
tags: [guide, template, how-to]
applicable_bots: []
editable: true
---

# Hướng dẫn Tạo Skill mới — TaxLegal AI

## Skill là gì?

Skill là một file Markdown (.md) chứa kiến thức chuyên sâu được **inject vào system prompt của bot** khi chạy pipeline. Bot sẽ sử dụng nội dung skill như "sách tham chiếu" khi phân tích và viết tư vấn.

## Format chuẩn

### Frontmatter (YAML, bắt buộc)

```yaml
---
name: tên-skill-lowercase-gach-ngang   # unique ID, không dấu, không khoảng trắng
version: 1.0.0                          # semantic versioning
description: >
  Mô tả ngắn: skill dùng cho gì, ai dùng, trong tình huống nào (2-3 câu)
category: tax|legal|advisory|compliance|guide  # chọn 1
tags: [tag1, tag2, tag3]               # keywords giúp tìm kiếm
applicable_bots: [partner, ja, sa]     # bot nào dùng skill này. [] = tất cả
editable: true                         # luôn để true
---
```

### Body (Markdown)

```markdown
# Skill: [Tên đầy đủ]

## Căn cứ pháp lý (nếu là tax/legal skill)
Bảng tóm tắt văn bản pháp luật liên quan.

## [Nội dung chính — chia sections rõ ràng]

## Các trường hợp thực tế / Ví dụ
Ít nhất 1-2 case study thực tế.

## Checklist
- [ ] Các bước kiểm tra quan trọng
```

## Các loại Skill phù hợp

### 1. Computation Skills (Tính toán)
Mục tiêu: giúp bot tính đúng số thuế, áp đúng thuế suất.

Bắt buộc có:
- Bảng thuế suất với nguồn trích dẫn (số văn bản cụ thể)
- Công thức tính thuế từng bước
- Điều kiện áp dụng (khi nào dùng, khi nào không)
- Ví dụ số cụ thể

### 2. Advisory Skills (Tư vấn chiến lược)
Mục tiêu: giúp bot tư vấn chiến lược, lập kế hoạch thuế.

Bắt buộc có:
- Framework phân tích (bước 1, 2, 3...)
- Cơ hội tối ưu hóa hợp pháp
- Rủi ro cần tránh
- Anti-patterns (những gì KHÔNG làm)

### 3. Compliance Skills (Tuân thủ)
Mục tiêu: giúp bot kiểm tra tuân thủ, phát hiện vi phạm.

Bắt buộc có:
- Checklist các nghĩa vụ
- Deadline kê khai, nộp thuế
- Mức phạt vi phạm
- Thủ tục xử lý khi vi phạm

### 4. Writing/Format Skills (Viết bài)
Mục tiêu: hướng dẫn bot viết đúng format, đúng văn phong.

Bắt buộc có:
- Cấu trúc bài viết (outline)
- Yêu cầu về ngôn ngữ, văn phong
- Template/mẫu cụ thể
- Anti-patterns về văn phong

## Tips viết Skill hiệu quả

### DO ✅
- **Cụ thể**: Luôn ghi rõ số văn bản, điều, khoản (VD: "Điều 9 Khoản 2 TT78/2014" thay vì "theo quy định")
- **Có số liệu**: Thuế suất, mức phạt, deadline cụ thể
- **Có ví dụ**: Ít nhất 1 case study thực tế với số cụ thể
- **Dùng bảng**: Thông tin so sánh, thuế suất → dùng bảng Markdown
- **Checklist**: Kết thúc bằng checklist ngắn gọn
- **Cập nhật ngày**: Ghi rõ "cập nhật đến [năm]" để biết khi nào cần review
- **Phân biệt còn/hết hiệu lực**: Dùng ⚠️ cho văn bản hết hiệu lực

### DON'T ❌
- Viết quá dài (>3000 từ) — bot có giới hạn context
- Trùng lặp nội dung với skill khác — link thay vì copy
- Dùng thuật ngữ mơ hồ ("theo quy định", "có thể", "thường là")
- Bỏ qua exceptions và edge cases
- Quên ghi nguồn cho số liệu/tỷ lệ

## Taxonomy Skills theo openaccountants framework

Tham khảo từ openaccountants.com — mỗi loại thuế nên có các skills:

| Role | Mục đích |
|------|---------|
| **Intake** | Thu thập thông tin, xác định phạm vi áp dụng |
| **Computation** | Tính toán thuế theo từng bước |
| **Return** | Lập tờ khai, điền mẫu |
| **Compliance** | Kiểm tra tuân thủ, checklist |
| **Advisory** | Lập kế hoạch, tối ưu hóa hợp pháp |
| **Writing** | Format và văn phong bài viết tư vấn |

## Ví dụ: Cách đặt tên Skill

```
vietnam-cit         → CIT computation + rules
vietnam-cit-return  → Hướng dẫn lập tờ khai TNDN
vietnam-cit-advisory → CIT planning và tối ưu hóa
vietnam-cit-compliance → Checklist tuân thủ CIT

vietnam-vat         → VAT rules
vietnam-vat-return  → Tờ khai GTGT
vietnam-vat-advisory → VAT planning
```

## Ghi nhớ về Bots

| Bot | Phù hợp với skill loại |
|-----|----------------------|
| **Partner** | Advisory, strategy, high-level review |
| **JA (Junior Associate)** | Research, computation, detailed analysis |
| **SA (Senior Associate)** | Compliance, quality check, adversarial review |
| **Intake** | Intake, onboarding, fact gathering |

## Quy trình cập nhật Skill

1. Khi có văn bản pháp luật mới → mở skill liên quan → cập nhật section bị ảnh hưởng
2. Tăng version (VD: 1.0.0 → 1.1.0)
3. Ghi chú ở đầu file: "Cập nhật ngày DD/MM/YYYY — thêm quy định X"
4. Kiểm tra xem Bot Variant nào đang dùng skill này → test lại
