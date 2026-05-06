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

# Skill: Thuế Nhà thầu nước ngoài (FCT) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Thông tư FCT | 103/2014/TT-BTC | Quy định chính về thuế nhà thầu |
| Thông tư sửa đổi | 60/2012/TT-BTC (tiền thân) | Thay thế bởi TT103 |
| Luật quản lý thuế | 38/2019/QH14 | Thủ tục hành chính thuế |
| Luật thuế GTGT | 13/2008/QH12 (sửa 31/2013, 71/2014) | Cơ sở VAT |
| Luật thuế TNDN | 14/2008/QH12 (sửa 32/2013, 71/2014) | Cơ sở CIT |

## Đối tượng chịu thuế nhà thầu

**FCT áp dụng khi đồng thời:**
1. Bên trả tiền là tổ chức/cá nhân Việt Nam hoặc tổ chức/cá nhân nước ngoài hoạt động tại Việt Nam
2. Bên nhận tiền là tổ chức nước ngoài không có tư cách pháp nhân Việt Nam, hoặc cá nhân nước ngoài không cư trú tại Việt Nam
3. Thu nhập phát sinh từ hoạt động kinh doanh tại Việt Nam (dịch vụ cung cấp tại VN, hoặc dịch vụ tiêu dùng tại VN)

**Các trường hợp KHÔNG chịu FCT (Điều 2, TT103):**
- Tổ chức nước ngoài có cơ sở thường trú tại VN (đã đăng ký nộp thuế trực tiếp)
- Cá nhân nước ngoài cư trú tại VN (chịu PIT)
- Hàng hóa nhập khẩu thuần túy (không kèm dịch vụ tại VN)
- Dịch vụ cung cấp và tiêu dùng hoàn toàn ngoài lãnh thổ VN

## Mức thuế suất FCT

### Thuế GTGT (VAT) theo FCT

| Loại hoạt động | Tỷ lệ % trên doanh thu |
|---------------|----------------------|
| Dịch vụ, cho thuê máy móc thiết bị, bảo hiểm, thuê tàu bay | **5%** |
| Xây dựng, lắp đặt (có bao thầu vật tư) | **3%** |
| Xây dựng, lắp đặt (không bao thầu vật tư) | **5%** |
| Vận tải, dịch vụ gắn với hàng hóa | **3%** |
| Chuyển nhượng chứng khoán, tái bảo hiểm ra nước ngoài | **0%** (miễn) |
| Hàng hóa sản xuất tại VN | **Áp dụng VAT thông thường** |

### Thuế TNDN (CIT) theo FCT

| Loại thu nhập | Tỷ lệ % trên doanh thu |
|--------------|----------------------|
| Dịch vụ (mặc định) | **5%** |
| Dịch vụ quản lý nhà hàng, khách sạn, casino | **10%** |
| Tiền bản quyền | **10%** |
| Cho thuê tài sản, cho thuê tàu bay, động cơ tàu bay, phụ tùng | **5%** |
| Xây dựng, lắp đặt | **2%** |
| Vận tải | **2%** |
| Chuyển nhượng chứng khoán | **0.1% trên giá chuyển nhượng** |
| Lãi cho vay | **5%** |
| Tiền bảo lãnh | **5%** |
| Hoạt động tài chính khác | **10%** |

**Mức mặc định: VAT 5% + CIT 5% = 10% trên doanh thu** nếu không xác định được phân loại.

## Ba phương pháp nộp thuế FCT

### Phương pháp 1: Khấu trừ trực tiếp (Bên VN khấu trừ và nộp thay)
- **Điều kiện**: Nhà thầu nước ngoài không đáp ứng điều kiện đăng ký trực tiếp
- **Quy trình**: Bên Việt Nam khấu trừ ngay khi trả tiền, kê khai và nộp thay trong 10 ngày kể từ ngày phát sinh
- **Ưu điểm**: Đơn giản nhất cho nhà thầu nước ngoài
- **Mẫu tờ khai**: Mẫu 01/NTNN

### Phương pháp 2: Trực tiếp (Nhà thầu nước ngoài tự khai nộp)
- **Điều kiện** (Điều 8, TT103):
  1. Có cơ sở thường trú tại VN hoặc là đối tượng cư trú tại VN
  2. Thời gian kinh doanh tại VN ≥ 183 ngày
  3. Áp dụng chế độ kế toán VN và sử dụng hóa đơn VN
- **Nộp thuế**: Theo quy định CIT và VAT thông thường

### Phương pháp 3: Hỗn hợp (Hybrid)
- **Điều kiện** (Điều 9, TT103):
  1. Có cơ sở thường trú hoặc là đối tượng cư trú
  2. Thời gian hoạt động tại VN ≥ 183 ngày
  3. KHÔNG áp dụng chế độ kế toán VN đầy đủ
- **Nộp VAT**: Trực tiếp (khai và nộp theo phương pháp trực tiếp trên doanh thu)
- **Nộp CIT**: Theo tỷ lệ % trên doanh thu (như Phương pháp 1)

## Hiệp định tránh đánh thuế hai lần (DTA) — Ưu tiên áp dụng

**Nguyên tắc**: Nếu tồn tại DTA giữa VN và nước của nhà thầu, DTA có thể giảm/miễn thuế FCT.

**Quy trình áp dụng DTA:**
1. Xác định nhà thầu có phải đối tượng cư trú của nước ký DTA không
2. Kiểm tra nhà thầu có đáp ứng điều kiện **beneficial ownership** không
3. Xác định thu nhập thuộc điều khoản nào của DTA (lợi nhuận kinh doanh, tiền bản quyền, lãi vay…)
4. Kiểm tra nhà thầu có cơ sở thường trú (PE) tại VN không
5. Nộp hồ sơ đề nghị áp dụng DTA (Mẫu 01/HTQT) cho CQT trong 15 ngày trước ngày thanh toán

**Lưu ý chứng nhận cư trú**: Giấy chứng nhận cư trú (Certificate of Residence) phải được cấp bởi CQT nước ngoài, còn hiệu lực, và được hợp pháp hóa lãnh sự.

## Đăng ký và chứng nhận nhà thầu

| Thủ tục | Thời hạn | Cơ quan |
|---------|---------|---------|
| Đăng ký MST (nếu PP2/PP3) | Trước ngày phát sinh nghĩa vụ thuế | CQT địa phương |
| Khai thuế FCT (PP1) | 10 ngày kể từ ngày trả tiền | CQT quản lý bên VN |
| Khai quyết toán năm (PP2/PP3) | 90 ngày sau khi kết thúc hợp đồng | CQT |

## Lịch tuân thủ FCT

| Sự kiện | Hạn chót |
|---------|---------|
| Khấu trừ khi trả tiền (PP1) | Ngay khi phát sinh |
| Kê khai nộp thay (PP1) | 10 ngày kể từ ngày trả tiền |
| Khai VAT trực tiếp (PP3) | Tháng 10/hàng tháng hoặc ngày 30/quý |
| Quyết toán kết thúc hợp đồng | 45 ngày kể từ khi kết thúc hợp đồng |

## Nguyên tắc mặc định thận trọng (Conservative Defaults)

| Tình huống | Mặc định |
|-----------|---------|
| Không xác định được loại dịch vụ | Áp dụng CIT 10% (mức cao nhất của dịch vụ thông thường) |
| Không có DTA rõ ràng hoặc còn nghi ngờ | Áp dụng thuế suất nội địa đầy đủ |
| Hợp đồng gộp (vật tư + dịch vụ không tách biệt) | Áp dụng toàn bộ theo tỷ lệ dịch vụ |
| Nhà thầu không cung cấp chứng nhận cư trú | Không áp dụng DTA — khấu trừ theo nội địa |
| Thời điểm trả tiền không rõ | Khai và nộp ngay khi phát hiện |

**Quy tắc vàng**: Khi không chắc chắn → **chọn mức khấu trừ cao hơn**. Chi phí hoàn thuế thấp hơn chi phí phạt nộp thiếu.

## Checklist thực hành FCT

- [ ] Xác định nhà thầu có đối tượng chịu FCT không (Điều 2, TT103)
- [ ] Phân loại phương pháp nộp thuế (PP1/PP2/PP3)
- [ ] Kiểm tra DTA áp dụng — yêu cầu chứng nhận cư trú nếu cần
- [ ] Phân loại đúng loại thu nhập → xác định tỷ lệ VAT + CIT
- [ ] Tách hợp đồng thành phần vật tư và dịch vụ nếu có thể
- [ ] Khai và nộp trong 10 ngày (PP1)
- [ ] Lưu hồ sơ: hợp đồng, chứng từ thanh toán, tờ khai, biên lai nộp thuế
