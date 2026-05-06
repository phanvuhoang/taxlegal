---
name: vietnam-invoices
version: 1.0.0
description: >
  Vietnam e-Invoice system — Decree 123/2020, Circular 78/2021, mandatory fields,
  cancellation procedures, invalid invoice consequences, and conservative defaults.
category: tax
tags: [invoice, e-invoice, hoa-don-dien-tu, decree-123, circular-78, vat-invoice, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Hóa đơn Điện tử (e-Invoice) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Nghị định hóa đơn điện tử | 123/2020/NĐ-CP | Quy định chính về hóa đơn và chứng từ |
| Thông tư hướng dẫn | 78/2021/TT-BTC | Hướng dẫn triển khai NĐ123 |
| Thông tư sửa đổi | 68/2019/TT-BTC (đã thay bởi TT78) | Lịch sử |
| Nghị định cũ | 51/2010/NĐ-CP + 04/2014/NĐ-CP | Chế độ hóa đơn cũ (đã hết hiệu lực) |
| Quyết định phê duyệt | 206/QĐ-BTC | Danh sách đơn vị cung cấp dịch vụ HĐĐT |

## Lộ trình áp dụng hóa đơn điện tử bắt buộc

| Giai đoạn | Đối tượng | Thời điểm bắt buộc |
|----------|----------|-------------------|
| Giai đoạn 1 | 6 tỉnh/thành phố thí điểm (HN, HCM, Hải Phòng, Phú Thọ, Quảng Ninh, Bình Định) | 01/07/2022 |
| Giai đoạn 2 | Toàn bộ doanh nghiệp, hộ kinh doanh, cá nhân kinh doanh | 01/07/2022 (chậm nhất) |
| Hộ kinh doanh nhỏ | Hộ/cá nhân kinh doanh không đăng ký | 01/07/2025 |

**Lưu ý**: Từ **01/07/2022**, hầu hết doanh nghiệp bắt buộc dùng HĐĐT. Hóa đơn giấy tự in/đặt in không còn giá trị trừ một số trường hợp đặc biệt (vùng sâu vùng xa, mất điện, sự cố kỹ thuật).

## Phân loại hóa đơn điện tử

### 1. Hóa đơn điện tử có mã của CQT (Authenticated e-Invoice)
- **Áp dụng**: Hộ kinh doanh; doanh nghiệp mới thành lập chưa đủ điều kiện; doanh nghiệp kinh doanh trong lĩnh vực rủi ro cao; DN áp dụng theo yêu cầu của CQT
- **Đặc điểm**: Phải gửi lên cổng của CQT để lấy **mã xác thực** trước khi gửi cho người mua
- **Thời gian cấp mã**: Ngay lập tức (real-time) hoặc trong 1–3 phút

### 2. Hóa đơn điện tử không có mã CQT (Non-authenticated e-Invoice)
- **Áp dụng**: Doanh nghiệp đáp ứng điều kiện (doanh thu lớn, tuân thủ tốt, có hệ thống kế toán)
- **Đặc điểm**: Ký số và gửi trực tiếp cho người mua, đồng thời gửi dữ liệu lên cổng CQT theo lịch (ngày 1 và 15 hàng tháng, hoặc liên tục)

## 10 Thông tin bắt buộc trên hóa đơn điện tử

Theo Điều 10, NĐ 123/2020:

| STT | Thông tin | Ghi chú |
|-----|-----------|---------|
| 1 | Tên loại hóa đơn | Hóa đơn GTGT / Hóa đơn bán hàng |
| 2 | Ký hiệu mẫu số và ký hiệu hóa đơn | Theo định dạng quy định |
| 3 | Tên, địa chỉ, MST của người bán | Phải khớp với đăng ký kinh doanh |
| 4 | Tên, địa chỉ, MST của người mua (nếu có) | Bắt buộc với tổ chức; tùy chọn với cá nhân |
| 5 | Tên hàng hóa, dịch vụ | Mô tả đủ để xác định |
| 6 | Đơn vị tính, số lượng, đơn giá | Không áp dụng cho một số loại DV |
| 7 | Thành tiền chưa có VAT | |
| 8 | Thuế suất VAT và tiền thuế VAT | Ghi rõ % và số tiền |
| 9 | Tổng tiền thanh toán đã có VAT | |
| 10 | Chữ ký điện tử của người bán | Chữ ký số theo quy định |

**Thông tin bổ sung (nếu có)**: Chữ ký điện tử của người mua (tổ chức), thời điểm lập hóa đơn, địa chỉ giao hàng, hình thức thanh toán.

## Thời điểm lập hóa đơn

| Loại giao dịch | Thời điểm lập hóa đơn |
|---------------|----------------------|
| Bán hàng hóa | Thời điểm chuyển giao quyền sở hữu/quyền sử dụng cho người mua |
| Cung cấp dịch vụ | Thời điểm hoàn thành dịch vụ hoặc thu tiền (nếu thu trước) |
| Xây dựng, lắp đặt | Nghiệm thu, bàn giao từng hạng mục/công trình |
| Giao hàng nhiều lần | Lập theo từng lần giao hàng |

**Quy tắc 24 giờ**: Hóa đơn phải lập **trong vòng 24 giờ** kể từ thời điểm phát sinh nghĩa vụ.
Trường hợp đặc biệt (dịch vụ thường xuyên): có thể lập theo tuần, tháng nhưng không quá 7 ngày sau kỳ cung cấp.

## Hủy, điều chỉnh hóa đơn điện tử

### Hủy hóa đơn
- **Khi nào**: Hóa đơn đã lập nhưng chưa gửi cho người mua, hoặc gửi nhưng người mua chưa nhận
- **Thủ tục**: Lập biên bản thỏa thuận hủy, thực hiện hủy trên hệ thống, thông báo CQT (nếu đã gửi dữ liệu)

### Điều chỉnh hóa đơn
- **Khi nào**: Hóa đơn đã giao cho người mua có sai sót
- **Phương pháp 1**: Lập hóa đơn điều chỉnh (tăng/giảm) → cả hai bên lưu giữ cả hai hóa đơn
- **Phương pháp 2**: Thỏa thuận hủy hóa đơn cũ + lập hóa đơn mới thay thế

### Sai sót về MST, tên, địa chỉ người mua
- Thông báo theo Mẫu 04/SS-HĐĐT để CQT điều chỉnh dữ liệu
- Không cần lập hóa đơn điều chỉnh nếu chỉ sai các thông tin này

## Hậu quả hóa đơn không hợp lệ

**CẤM khấu trừ VAT đầu vào** khi hóa đơn:
- Thiếu bất kỳ thông tin bắt buộc nào trong 10 trường thông tin
- MST người bán không tồn tại/đã bị thu hồi
- Hóa đơn đã bị hủy nhưng vẫn sử dụng
- Hóa đơn giả mạo, gian lận
- Không có chữ ký số hợp lệ
- Hóa đơn của giao dịch không có thực

**CẤM trừ chi phí CIT** khi hóa đơn không hợp lệ theo các tiêu chí trên.

**Xử phạt vi phạm hành chính (NĐ 125/2020):**

| Vi phạm | Mức phạt |
|---------|---------|
| Lập hóa đơn không đúng quy định | VND 4–8 triệu |
| Không lập hóa đơn khi bán hàng | VND 10–20 triệu |
| Sử dụng hóa đơn bất hợp pháp | VND 20–50 triệu + truy thu thuế |
| Trốn thuế qua hóa đơn khống | Hình sự nếu số thuế trốn lớn |

## Kiểm tra tính hợp lệ của hóa đơn

**Cổng kiểm tra**: https://hoadondientu.gdt.gov.vn

Kiểm tra được: tình trạng hóa đơn (hợp lệ/đã hủy/không tồn tại), MST người bán.

## Hóa đơn giấy tự in/đặt in (Legacy)

Hóa đơn giấy **không còn hiệu lực** từ 01/07/2022. Trường hợp ngoại lệ còn được dùng:
- Địa bàn có điều kiện khó khăn theo quyết định của Bộ Tài chính
- Sự cố kỹ thuật, thiên tai — dùng tạm thời theo Mẫu 01/HĐG

## Nguyên tắc mặc định thận trọng (Conservative Defaults)

| Tình huống | Mặc định |
|-----------|---------|
| Hóa đơn thiếu bất kỳ trường bắt buộc nào | Từ chối khấu trừ VAT và CIT |
| MST người bán chưa xác minh được | Tạm giữ lại, xác minh trước khi kê khai |
| Hóa đơn lập sau 24h từ thời điểm phát sinh | Ghi nhận rủi ro, đề nghị điều chỉnh |
| Hóa đơn giấy nhận được từ 01/07/2022 | Chỉ chấp nhận nếu có bằng chứng ngoại lệ hợp pháp |
| Hóa đơn điều chỉnh nhưng thiếu hóa đơn gốc | Không khấu trừ cho đến khi có đủ bộ hồ sơ |

## Checklist thực hành hóa đơn điện tử

- [ ] Kiểm tra 10 thông tin bắt buộc đủ và chính xác
- [ ] Xác minh MST người bán qua cổng hoadondientu.gdt.gov.vn
- [ ] Kiểm tra trạng thái hóa đơn (chưa hủy, còn hiệu lực)
- [ ] Xác nhận chữ ký số hợp lệ và còn hiệu lực
- [ ] Hóa đơn lập đúng thời điểm (trong 24h)
- [ ] Lưu trữ hóa đơn điện tử theo quy định (10 năm)
- [ ] Đối chiếu dữ liệu hóa đơn với tờ khai VAT hàng tháng
