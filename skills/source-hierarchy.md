---
name: source-hierarchy
version: 1.1.0
description: "Hệ thống phân cấp nguồn pháp lý VN — Law hierarchy (Luật→NĐ→TT→CV), DB-first retrieval order, citation rules"
category: process
tags: [source-hierarchy, legal-research, db-first, citation, retrieval]
applicable_bots: [ja-default, ja-advisory, ja-compliance, ja-fct, ja-tp, ja-pit, ja-vat, ja-cit, ja-sst, ja-intl-tax, sa-default, sa-advisory, sa-compliance]
editable: true
---

# Source Hierarchy — Hệ Thống Nguồn Pháp Lý Việt Nam

## Mục Đích
Skill này định nghĩa thứ tự ưu tiên nguồn pháp lý trong nghiên cứu thuế VN, quy tắc DB-first retrieval, và chuẩn trích dẫn.

---

## 1. Phân Cấp Văn Bản Pháp Luật Việt Nam

### Hệ Thống Phân Cấp (Cao → Thấp)

```
Tier 1 — Văn bản do Quốc hội ban hành (hiệu lực pháp lý cao nhất)
├── Hiến pháp
├── Bộ luật (Bộ Luật Dân sự, Bộ Luật Hình sự, ...)
└── Luật (Luật VAT, Luật CIT, Luật PIT, Luật Quản lý Thuế, ...)

Tier 2 — Văn bản do Chính phủ / Chủ tịch nước ban hành
├── Lệnh (Lệnh của Chủ tịch nước — promulgate Luật)
├── Nghị quyết Chính phủ
├── Nghị định (NĐ) — hướng dẫn thi hành Luật
└── Quyết định của Thủ tướng Chính phủ

Tier 3 — Văn bản do Bộ / cơ quan ngang Bộ ban hành
├── Thông tư (TT) của Bộ Tài chính — hướng dẫn chi tiết NĐ
├── Thông tư liên tịch (TTLT) — nhiều Bộ ban hành chung
└── Quyết định của Bộ trưởng

Tier 4 — Văn bản hướng dẫn hành chính (không phải VBQPPL)
├── Công văn (CV) của Tổng Cục Thuế / Cục Thuế — giải thích cho trường hợp cụ thể
├── Công văn của Bộ Tài chính
└── Công văn của Cục Hải quan

Tier 5 — Phán quyết / Giải thích tư pháp
└── Bản án tòa hành chính (rất hiếm, không phải precedent binding)
```

### Nguyên Tắc Áp Dụng

1. **Văn bản cấp cao hơn có hiệu lực cao hơn**: Thông tư không được trái Nghị định; Nghị định không được trái Luật
2. **Văn bản mới hơn thay thế văn bản cũ hơn** (cùng cấp): ngày hiệu lực, không phải ngày ban hành
3. **Văn bản chuyên ngành ưu tiên hơn văn bản chung** (trong phạm vi áp dụng)
4. **Công văn**: phản ánh quan điểm CQT nhưng không phải VBQPPL — có giá trị tham khảo cao, đặc biệt khi facts tương tự

---

## 2. DB-First Retrieval Order — Thứ Tự Truy Vấn Nguồn

### Quy Tắc Bắt Buộc (ENFORCED)

Mọi JA/SA phải thực hiện theo thứ tự sau. **KHÔNG ĐƯỢC BỎ QUA bước DB nội bộ.**

```
STEP 1: Truy vấn DB taxlegal (nội bộ)
├── Tìm memo/precedent đã có cho tình huống tương tự
├── Tìm công văn/văn bản đã được lưu trữ
└── Nếu tìm được → ưu tiên sử dụng + cập nhật nếu luật đã thay đổi

STEP 2: Truy vấn DB dbvntax (cơ sở dữ liệu văn bản pháp luật thuế VN)
├── Tìm Luật, NĐ, TT, Công văn theo keyword + loại thuế + thời kỳ
└── Kết quả từ đây là nguồn chính thức — PHẢI trích dẫn

STEP 3: Truy vấn DB legalai (nếu có)
└── Văn bản pháp lý tổng hợp bổ sung

STEP 4: Web search (Perplexity Sonar / CrawlKit) — CHỈ KHI STEP 1-3 không đủ
├── Tìm văn bản mới nhất chưa vào DB
├── Tìm công văn gần đây / thông tư mới ban hành
└── PHẢI ghi rõ: "Nguồn: web search — chưa xác minh trong DB chính thức"

STEP 5: Nếu không tìm được nguồn đủ tin cậy
└── BÁO CÁO: "Insufficient Source Coverage" — không được suy đoán
```

### Insufficient Source Coverage Protocol

Khi không tìm được đủ nguồn pháp lý:

```
BÁO CÁO: INSUFFICIENT SOURCE COVERAGE

Vấn đề nghiên cứu: [...]
Nguồn đã tra cứu:
  ✓ DB taxlegal (nội bộ): [kết quả / không tìm được]
  ✓ DB dbvntax: [kết quả / không tìm được]
  ✓ Web search: [kết quả / không tìm được]

Lý do chưa đủ cơ sở:
  - [vùng xám pháp lý]
  - [văn bản mâu thuẫn nhau]
  - [chưa có hướng dẫn chính thức]

Đề xuất:
  - Tra cứu công văn của CQT địa phương
  - Xin ruling (văn bản xác nhận trước) từ Cục Thuế
  - Tham vấn chuyên gia về vùng xám này
```

---

## 3. Citation Rules — Chuẩn Trích Dẫn

### 3.1 Trích Dẫn Văn Bản Quy Phạm Pháp Luật

**Format chuẩn**:
```
[Loại văn bản] [Số]/[Năm]/[Cơ quan ban hành], [Tên văn bản], Điều [X], Khoản [Y], Điểm [Z]
```

**Ví dụ**:
- Điều 9, Khoản 1 Luật Thuế GTGT số 13/2008/QH12 sửa đổi bởi Luật 31/2013/QH13
- Điều 7, Khoản 2, Điểm b TT 219/2013/TT-BTC ngày 31/12/2013 của Bộ Tài chính
- NĐ 132/2020/NĐ-CP ngày 5/11/2020 của Chính phủ về quản lý thuế đối với giao dịch liên kết

### 3.2 Trích Dẫn Công Văn

**Format chuẩn**:
```
Công văn số [XXXX]/[Cơ quan]-[Phòng/Ban] ngày [DD/MM/YYYY] của [Tổng Cục Thuế/Cục Thuế...] về [chủ đề]
```

**Ví dụ**:
- Công văn số 3815/TCT-CS ngày 21/10/2020 của Tổng Cục Thuế về chính sách thuế GTGT
- Công văn số 1234/CT-TTHT ngày 15/03/2023 của Cục Thuế TP.HCM về thuế TNCN đối với RSU

### 3.3 Trích Dẫn Điều Ước Quốc Tế (DTA)

```
Hiệp định tránh đánh thuế hai lần giữa Việt Nam và [Tên nước] (ký ngày [DD/MM/YYYY], có hiệu lực từ [DD/MM/YYYY]), Điều [X] — [Tên điều]
```

**Ví dụ**:
- Hiệp định tránh đánh thuế hai lần Việt Nam — Singapore (có hiệu lực từ 01/01/1996), Điều 12 — Tiền bản quyền

### 3.4 Trích Dẫn Khi Dùng Nguồn Web / Unofficial

```
⚠️ [Nguồn: web search / CrawlKit — chưa xác minh trong hệ thống văn bản chính thức]
Thông tin: [...]
Nguồn tham khảo: [URL / tên cổng thông tin]
Khuyến nghị: Xác nhận lại từ cổng văn bản quy phạm pháp luật chính thức (vbpl.vn / thuvienphapluat.vn)
```

---

## 4. Xử Lý Văn Bản Mâu Thuẫn

### 4.1 Khi Có Mâu Thuẫn Giữa Các Văn Bản

**Bước 1**: Xác định cấp bậc — áp văn bản cấp cao hơn
**Bước 2**: Nếu cùng cấp — áp văn bản mới hơn (kiểm tra ngày hiệu lực)
**Bước 3**: Nếu cùng cấp và cùng thời kỳ — văn bản chuyên ngành ưu tiên hơn văn bản chung
**Bước 4**: Nếu vẫn không giải quyết được → báo cáo mâu thuẫn + đề xuất xin ruling

### 4.2 Khi Luật Thay Đổi Giữa Năm

- Xác định ngày hiệu lực của văn bản mới
- Áp dụng theo nguyên tắc: "luật mới áp dụng từ ngày có hiệu lực"
- Giao dịch/nghĩa vụ phát sinh trước ngày đó → áp luật cũ
- Luôn nêu rõ trong memo: "Quy định áp dụng tại thời điểm [ngày]"

---

## 5. Checklist Trước Khi Đưa Ra Kết Luận

```
SOURCE QUALITY GATE
[ ] Đã tra cứu DB nội bộ (Step 1)
[ ] Đã tra cứu dbvntax (Step 2)
[ ] Văn bản pháp lý trích dẫn còn hiệu lực tại thời điểm phân tích
[ ] Không có văn bản mới hơn thay thế/sửa đổi văn bản đang dùng
[ ] Công văn trích dẫn có facts tương đồng (không áp sai ngữ cảnh)
[ ] Nếu dùng nguồn web → đã gắn cảnh báo ⚠️
[ ] Không có mâu thuẫn nội bộ giữa các nguồn đã dùng
[ ] Nếu vùng xám → đã phân loại mức độ không chắc chắn rõ ràng
```
