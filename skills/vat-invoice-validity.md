---
name: vat-invoice-validity
version: 1.0.0
description: >
  Skill kiểm tra tính hợp lệ của hóa đơn GTGT và hóa đơn điện tử tại Việt Nam. Bao gồm
  các trường bắt buộc, lỗi phổ biến, cách tra cứu mã xác thực GDT, xử lý hóa đơn sai
  sót và hóa đơn ảo, thư viện supplier pattern để phân loại nhanh.
category: tax
tags: [vat, gtgt, hoa-don-dien-tu, invoice, e-invoice, validity, supplier-pattern, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Kiểm Tra Hóa Đơn GTGT & Hóa Đơn Điện Tử

> **Căn cứ:** NĐ 123/2020/NĐ-CP, TT 78/2021/TT-BTC, Luật Thuế GTGT 13/2008/QH12

---

## Phần 1 — Các Trường Bắt Buộc Trên HĐĐT

| Trường | Bắt buộc? | Ghi chú |
|--------|-----------|---------|
| Ký hiệu, số hóa đơn | ✅ | Số duy nhất theo hệ thống |
| Ngày lập hóa đơn | ✅ | DD/MM/YYYY |
| Tên, địa chỉ, MST **bên bán** | ✅ | MST 10 chữ số |
| Tên, địa chỉ, MST **bên mua** | ✅ (B2B) | Để khấu trừ đầu vào phải có MST bên mua |
| Tên hàng hóa/dịch vụ | ✅ | Mô tả rõ ràng, không chung chung |
| Đơn vị tính, số lượng, đơn giá | ✅ | Đủ chi tiết để kiểm tra |
| Thành tiền (chưa thuế) | ✅ | |
| Thuế suất GTGT | ✅ | 0%, 5%, 10%, hoặc "không chịu thuế" |
| Tiền thuế GTGT | ✅ (nếu có thuế) | |
| Tổng tiền thanh toán | ✅ | |
| Mã xác thực của Tổng cục Thuế | ✅ | Dạng QR hoặc mã ký tự |
| Chữ ký số bên bán | ✅ | |

---

## Phần 2 — Tra Cứu Hóa Đơn Điện Tử

### Kênh tra cứu

| Kênh | URL | Thông tin cần |
|------|-----|---------------|
| Cổng GDT | **hoadondientu.gdt.gov.vn** | Số hóa đơn, ngày, MST bên bán |
| Ứng dụng eTax | app eTax Mobile | Quét QR code trên hóa đơn |
| API hóa đơn (doanh nghiệp) | GDT API | Tích hợp phần mềm kế toán |

### Quy trình kiểm tra

```
1. Nhập MST bên bán + Số hóa đơn + Ngày lập
   ↓
2. Kết quả hợp lệ: "Hóa đơn đã được GDT xác thực"
   → Được khấu trừ đầu vào (nếu đáp ứng đủ 4 điều kiện)
   ↓
3. Kết quả không hợp lệ: "Không tìm thấy" hoặc "Hóa đơn đã hủy"
   → KHÔNG được khấu trừ; liên hệ nhà cung cấp để lấy hóa đơn thay thế
```

---

## Phần 3 — Lỗi Phổ Biến Trên Hóa Đơn

### 3.1 Lỗi làm mất quyền khấu trừ

| Lỗi | Mức độ | Xử lý |
|-----|--------|-------|
| Sai MST bên mua | **Nghiêm trọng** | Yêu cầu bên bán lập hóa đơn điều chỉnh/thay thế |
| Không có mã xác thực GDT | **Nghiêm trọng** | Hóa đơn chưa hợp lệ → không khấu trừ |
| Sai tên/địa chỉ bên mua | **Nghiêm trọng** | Hóa đơn điều chỉnh hoặc thay thế |
| Mô tả HH/DV quá chung chung ("dịch vụ tư vấn") | **Trung bình** | Kèm hợp đồng, bảng kê chi tiết |
| Ngày lập sai (trước/sau thực tế cung cấp) | **Trung bình** | Hóa đơn điều chỉnh |
| Chữ số thuế tính sai | **Trung bình** | Hóa đơn điều chỉnh |

### 3.2 Lỗi không làm mất quyền khấu trừ (nhưng cần điều chỉnh)

| Lỗi | Xử lý |
|-----|-------|
| Lỗi chính tả trong tên sản phẩm | Lập biên bản điều chỉnh hoặc hóa đơn thay thế |
| Thiếu đơn vị tính | Bổ sung bằng biên bản |
| Thứ tự dòng sai | Không ảnh hưởng nếu tổng đúng |

---

## Phần 4 — Hóa Đơn Điều Chỉnh vs Hóa Đơn Thay Thế

| | Hóa đơn điều chỉnh | Hóa đơn thay thế |
|-|-------------------|-----------------|
| Khi nào dùng | Sai một số trường (số tiền, ngày, mô tả) | Khi cần hủy hoàn toàn hóa đơn gốc |
| Số hóa đơn | Số mới; ghi rõ "điều chỉnh cho HĐ số..." | Số mới; HĐ gốc bị hủy |
| Kế toán | Ghi bổ sung phần chênh lệch | Hủy ghi nhận HĐ gốc, ghi nhận HĐ mới |
| Kê khai | Điều chỉnh kỳ phát hiện sai sót | Kỳ phát hiện sai sót |

---

## Phần 5 — Thư Viện Supplier Pattern

Phân loại nhanh theo tên đối tác (không phân biệt hoa thường):

### Ngân hàng — Miễn thuế (EXCLUDE phí ngân hàng)

| Pattern | Xử lý | Lý do |
|---------|-------|-------|
| VIETCOMBANK, VCB, NGÂN HÀNG NGOẠI THƯƠNG | EXCLUDE phí | Dịch vụ tài chính — miễn GTGT |
| BIDV, NGÂN HÀNG ĐẦU TƯ | EXCLUDE phí | Miễn GTGT |
| VIETINBANK, NGÂN HÀNG CÔNG THƯƠNG | EXCLUDE phí | Miễn GTGT |
| AGRIBANK, NGÂN HÀNG NÔNG NGHIỆP | EXCLUDE phí | Miễn GTGT |
| TECHCOMBANK, TCB | EXCLUDE phí | Miễn GTGT |
| VPBANK, MB BANK, ACB, SACOMBANK, TPBANK | EXCLUDE phí | Miễn GTGT |
| PHÍ DỊCH VỤ, LÃI SUẤT, INTEREST, FEE | EXCLUDE | Phí ngân hàng/lãi — miễn |

### Tiện ích — Chịu thuế

| Pattern | Thuế suất | Ghi chú |
|---------|-----------|---------|
| EVN, TẬP ĐOÀN ĐIỆN LỰC, ĐIỆN LỰC, CÔNG TY ĐIỆN LỰC | Input 10% | Điện — tiêu chuẩn |
| SAWACO, HAWACO, CẤP NƯỚC | Input 5% | Nước sạch — giảm 5% |
| VIETTEL TELECOM, VNPT, MOBIFONE, VIETNAMOBILE | Input 10% | Viễn thông — tiêu chuẩn |

### Vận tải & Logistics

| Pattern | Xử lý |
|---------|-------|
| VIETNAM AIRLINES, VIETJET AIR, BAMBOO AIRWAYS | 0% quốc tế / 10% nội địa — kiểm tra lộ trình |
| GRAB VIETNAM, BE TAXI | Input 10% |
| GIAO HÀNG TIẾT KIỆM (GHTK), GIAO HÀNG NHANH (GHN), VIETTEL POST | Input 10% |
| J&T EXPRESS VIETNAM, NINJA VAN VIETNAM | Input 10% |

### Phần mềm & Cloud — Việt Nam

| Pattern | Xử lý |
|---------|-------|
| MISA, FAST ACCOUNTING | Input 10% |
| VIETTEL CLOUD, VNPT CLOUD | Input 10% |

### Phần mềm & Cloud — Quốc tế (⚠️ FCT)

| Pattern | Xử lý |
|---------|-------|
| GOOGLE (Workspace, Ads, Cloud) | FLAG FCT — không khấu trừ mặc định |
| MICROSOFT (365, Azure) | Kiểm tra: nếu từ Microsoft VN → 10%; Ireland → FCT |
| META, FACEBOOK ADS | FLAG FCT |
| AWS, ZOOM, SLACK, NOTION, OPENAI | FLAG FCT |

### Chính phủ & Bảo hiểm — EXCLUDE

| Pattern | Xử lý |
|---------|-------|
| TỔNG CỤC THUẾ, CỤC THUẾ | EXCLUDE — thanh toán thuế |
| BHXH, BẢO HIỂM XÃ HỘI | EXCLUDE — bảo hiểm |
| HẢI QUAN, CUSTOMS | EXCLUDE — thuế hải quan |
| BHTN, BẢO HIỂM THẤT NGHIỆP | EXCLUDE |

### Chuyển khoản nội bộ & Không phải GTGT — EXCLUDE

| Pattern | Xử lý |
|---------|-------|
| CHUYỂN KHOẢN NỘI BỘ, INTERNAL | EXCLUDE |
| LƯƠNG, TIỀN LƯƠNG, SALARY | EXCLUDE |
| VAY VỐN, TRẢ NỢ, LOAN | EXCLUDE |
| CỔ TỨC, DIVIDEND | EXCLUDE |
| VNPAY (phí), MOMO (phí), ZALOPAY (phí) | EXCLUDE — phí ví điện tử |

---

## Phần 6 — Hóa Đơn Ảo (Fake Invoice)

### Dấu hiệu nhận biết hóa đơn ảo

| Dấu hiệu | Rủi ro |
|---------|-------|
| Không tra cứu được trên hoadondientu.gdt.gov.vn | **RẤT CAO** |
| MST bên bán không tồn tại hoặc đã bị thu hồi | RẤT CAO |
| Ngày lập hóa đơn trước khi doanh nghiệp thành lập | RẤT CAO |
| Giá cao bất thường so với thị trường | CAO |
| Mô tả HH/DV mập mờ không thể xác minh | TRUNG BÌNH |
| Thanh toán tiền mặt cho giao dịch > 20 triệu | TRUNG BÌNH |

### Hậu quả sử dụng hóa đơn ảo

- **Hành chính:** Không được khấu trừ đầu vào; bị truy thu thuế + lãi
- **Hình sự:** Sử dụng hóa đơn ảo có thể bị truy cứu hình sự (Điều 203-205 BLHS)
- **Bên mua:** Rủi ro liên đới nếu biết hoặc phải biết là hóa đơn ảo

> **Quy tắc:** Nếu có bất kỳ nghi ngờ nào → **KHÔNG khấu trừ** và **flag ngay** cho người có thẩm quyền.
