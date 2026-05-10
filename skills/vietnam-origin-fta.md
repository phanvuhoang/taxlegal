---
name: vietnam-origin-fta
version: 1.0.0
description: >
  Skill về xuất xứ hàng hóa và ưu đãi FTA tại Việt Nam: các tiêu chí xác định xuất xứ
  (WO, CTC, RVC), các loại C/O và FTA chủ yếu, quy tắc cộng gộp, rủi ro gian lận xuất xứ,
  và tối ưu hóa thuế nhập khẩu qua FTA.
category: customs
tags: [customs, origin, xuat-xu, co, fta, atiga, evfta, cptpp, rcep, vietnam, rules-of-origin]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Xuất Xứ Hàng Hóa & Ưu Đãi FTA

> **Căn cứ:** Luật Quản lý ngoại thương 04/2017/QH14, NĐ 31/2018/NĐ-CP, TT 38/2018/TT-BCT và các phụ lục FTA

---

## Phần 1 — Ba Tiêu Chí Xác Định Xuất Xứ

### 1.1 WO — Wholly Obtained (Hàng thuần túy)

Hàng hóa được sản xuất **hoàn toàn** tại một nước, không dùng nguyên liệu từ nước khác.

**Ví dụ:** Tôm đánh bắt tại vùng biển VN → WO tại VN (hưởng FTA xuất khẩu sang EU).

### 1.2 CTC — Change in Tariff Classification (Chuyển đổi mã HS)

Nguyên liệu đầu vào từ nhiều nước, nhưng sau khi sản xuất tại VN → hàng thành phẩm có **mã HS khác** ở cấp chương (CC), nhóm (CTH), hoặc phân nhóm (CTSH).

**Ví dụ:** Vải nhập từ Trung Quốc (HS 5208) → May thành áo tại VN (HS 6109) → Chuyển đổi nhóm (CTH) → đủ xuất xứ ATIGA.

### 1.3 RVC — Regional Value Content (Hàm lượng giá trị khu vực)

Tỷ lệ % giá trị được tạo ra tại nước/khu vực FTA.

```
Phương pháp trực tiếp (Build-up):
RVC = (Giá trị nguyên liệu có xuất xứ) ÷ (Giá FOB thành phẩm) × 100%

Phương pháp gián tiếp (Build-down):
RVC = (Giá FOB − Giá trị nguyên liệu không có xuất xứ) ÷ Giá FOB × 100%
```

**Ngưỡng RVC phổ biến:**
- ATIGA: 40% (ASEAN nội khối)
- VJEPA: 40%
- EVFTA: 40–45% tùy mặt hàng
- CPTPP: 40–50% tùy mặt hàng

---

## Phần 2 — Các Loại C/O và FTA Tương Ứng

| C/O | FTA | Đối tác chủ yếu | Yêu cầu xuất xứ |
|-----|-----|----------------|----------------|
| Form D | ATIGA | ASEAN 10 nước | RVC ≥ 40% hoặc CTH |
| Form AK | AKFTA | ASEAN + Hàn Quốc | RVC ≥ 40% hoặc CTH |
| Form AJ | AJCEP | ASEAN + Nhật Bản | RVC ≥ 40% hoặc CTC |
| Form AI | AIFTA | ASEAN + Ấn Độ | Tùy sản phẩm |
| Form VJ | VJEPA | Nhật Bản | RVC ≥ 40% hoặc CTC |
| Form VK | VKFTA | Hàn Quốc | RVC ≥ 40% hoặc CTC |
| Form EUR.1 | EVFTA | EU | Tùy sản phẩm (phức tạp hơn) |
| REX (Registered Exporter) | EVFTA (tự chứng nhận) | EU | Sau khi đăng ký REX |
| Form UKVFTA | UKVFTA | Anh | Tương tự EVFTA |
| Form CPTPP | CPTPP | Nhật, Canada, Úc, Mexico, Chile... | Tùy Phụ lục CPTPP |
| Form RCEP | RCEP | ASEAN + TQ, Nhật, Hàn, Úc, NZ | RVC ≥ 40% hoặc CTH |

---

## Phần 3 — Quy Tắc Cộng Gộp (Accumulation/Cumulation)

**Cộng gộp** cho phép nguyên liệu từ nhiều nước trong cùng FTA được tính vào xuất xứ.

**Ví dụ ATIGA:** VN nhập vải từ Thái Lan (cũng là thành viên ASEAN) để may áo xuất sang Singapore → Vải Thái Lan được coi như nguyên liệu ASEAN → Cộng gộp vào RVC → Dễ đạt 40% hơn.

> **Quan trọng:** Không phải FTA nào cũng có cộng gộp song phương. EVFTA có cộng gộp hạn chế. Cần kiểm tra quy tắc xuất xứ cụ thể từng FTA.

---

## Phần 4 — Tổng Quan Tối Ưu Hóa FTA

### Quy trình chọn FTA tốt nhất để nhập khẩu vào VN

```
1. Xác định nước xuất xứ hàng hóa
2. Liệt kê các FTA giữa VN và nước đó
3. Tra thuế suất từng FTA cho HS Code → Chọn FTA có thuế thấp nhất
4. Kiểm tra điều kiện C/O của FTA đó (RVC? CTC? WO?)
5. Xin C/O từ cơ quan có thẩm quyền nước xuất khẩu
6. Khai báo C/O khi nhập khẩu vào VN
```

**Ví dụ:** Nhập hàng từ Nhật — có thể chọn giữa AJCEP (ASEAN-Nhật) hoặc VJEPA (VN-Nhật song phương). Thuế suất có thể khác nhau → **tra cứu cả hai và chọn thấp hơn**.

---

## Phần 5 — Rủi Ro Gian Lận Xuất Xứ

### Gian lận xuất xứ phổ biến

| Hình thức | Mô tả | Hệ quả |
|----------|-------|--------|
| Làm giả C/O | Cấp C/O cho hàng không đủ điều kiện xuất xứ | Phạt hành chính + hình sự |
| Chuyển tải trá hình (Transshipment) | Hàng TQ đi qua VN, dán nhãn Made in Vietnam | VN bị điều tra, áp thuế trả đũa (anti-dumping) |
| Gia công tối thiểu (Minimal processing) | Chỉ dán nhãn, đóng gói → không tạo xuất xứ | Từ chối ưu đãi FTA, truy thu |
| Khai sai giá trị nguyên liệu | Khai thấp nguyên liệu không xuất xứ để đạt RVC | Truy thu + phạt |

### Gian lận xuất xứ với VN và rủi ro thương mại quốc tế

VN đã bị Mỹ và EU điều tra về gian lận xuất xứ hàng hóa TQ chuyển tải qua VN. **Hậu quả:**
- Doanh nghiệp có thể bị đưa vào danh sách cấm xuất khẩu vào Mỹ
- Hàng VN bị áp thuế chống bán phá giá bổ sung

> **Khuyến nghị:** Luôn đảm bảo hàng thực sự có xuất xứ VN trước khi cấp C/O. Không ký xác nhận xuất xứ nếu không đủ điều kiện.

---

## Phần 6 — Checklist C/O Hợp Lệ

- [ ] C/O được cấp bởi **cơ quan có thẩm quyền** (Phòng Thương mại, Bộ Công thương nước xuất khẩu)
- [ ] C/O điền đầy đủ: tên người xuất, tên người nhập, mô tả hàng, HS Code, trị giá, nước xuất xứ
- [ ] Tiêu chí xuất xứ được đánh dấu rõ (WO / RVC xx% / CTC...)
- [ ] **Số C/O khớp** với Commercial Invoice và Bill of Lading
- [ ] **Ngày cấp C/O** trước hoặc trùng ngày xếp hàng lên tàu (không được cấp sau)
- [ ] Chữ ký và con dấu của cơ quan cấp còn nguyên vẹn
- [ ] **Form đúng loại** (Form D cho ATIGA, Form VK cho VKFTA...)
- [ ] Nộp trong thời hạn (thường 1 năm từ ngày cấp)
