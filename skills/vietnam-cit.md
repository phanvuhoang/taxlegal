---
name: vietnam-cit
version: 1.0.0
description: >
  Skill chuyên sâu về Thuế Thu nhập doanh nghiệp (TNDN/CIT) Việt Nam.
  Bao gồm căn cứ pháp lý, thu nhập tính thuế, chi phí được trừ, ưu đãi thuế, chuyển lỗ.
  Dùng cho Partner Bot và JA Bot khi phân tích vấn đề CIT.
category: tax
tags: [cit, tndn, corporate-tax, vietnam, transfer-pricing, tax-incentives]
applicable_bots: [partner, ja, sa]
---

# Skill: Thuế Thu nhập Doanh nghiệp (CIT) — Việt Nam

## Khung pháp lý hiện hành

| Văn bản | Số hiệu | Nội dung chính |
|---------|---------|----------------|
| Luật TNDN | 14/2008/QH12 (sửa 32/2013, 71/2014) | Luật gốc |
| Nghị định hướng dẫn | 218/2013/NĐ-CP (sửa 12/2015, 91/2014) | Hướng dẫn tổng quát |
| Thông tư hướng dẫn | 78/2014/TT-BTC (sửa 96/2015, 151/2014, 25/2018) | Hướng dẫn chi tiết |
| Thuế tối thiểu toàn cầu | Nghị quyết 107/2023/QH15 + TT05/2024/TT-BTC | Áp dụng từ 2024 |
| Giá chuyển nhượng | NĐ 132/2020/NĐ-CP + TT45/2021/TT-BTC | Giao dịch liên kết |

## Thuế suất

| Đối tượng | Thuế suất |
|-----------|-----------|
| DN thông thường | **20%** |
| Hoạt động tìm kiếm, thăm dò, khai thác dầu khí | 32–50% |
| DN trong KCN, KKT (ưu đãi) | 10% (15 hoặc 17 năm đầu) |
| DN công nghệ cao, phần mềm | 10% (cả đời dự án hoặc 15 năm) |
| Thuế tối thiểu toàn cầu (GMT) | 15% QDMTT cho MNE ≥750M EUR |

## Thu nhập chịu thuế

**Thu nhập chịu thuế = Thu nhập tính thuế - Thu nhập được miễn**

**Thu nhập tính thuế = Doanh thu - Chi phí được trừ + Thu nhập khác**

### Doanh thu
- Tổng giá trị hàng hóa/DV đã bán (không bao gồm VAT)
- Thời điểm ghi nhận: khi chuyển giao rủi ro và lợi ích, hoặc hoàn thành DV

### Thu nhập được miễn
- Thu nhập từ hoạt động nông nghiệp (một số trường hợp)
- Thu nhập từ góp vốn, liên doanh đã nộp thuế tại nguồn
- Thu nhập từ chênh lệch tỷ giá khi đánh giá lại (chưa thực hiện)
- Thu nhập từ tài sản nhà nước giao (quỹ KH&CN)

## Chi phí được trừ — Điều kiện

**3 điều kiện đồng thời (Điều 9, TT78/2014 sửa bởi TT96/2015):**

1. **Thực tế phát sinh** — liên quan đến hoạt động SXKD
2. **Có đủ hóa đơn, chứng từ hợp pháp** theo quy định
3. **Có chứng từ thanh toán không dùng tiền mặt** đối với giao dịch từ **20 triệu đồng trở lên**

### Chi phí KHÔNG được trừ phổ biến

| Chi phí | Lý do không được trừ |
|---------|---------------------|
| Chi không có hóa đơn VAT (≥200K/lần) | Không có chứng từ hợp pháp |
| Chi tiền mặt ≥20 triệu | Vi phạm điều kiện thanh toán |
| Tiền phạt vi phạm hành chính, hình sự | Quy định loại trừ |
| Chi vượt mức khống chế | Quảng cáo, khuyến mại >15% tổng chi phí được trừ |
| Lương của chủ DNTN không đăng ký với CQT | Thiếu hồ sơ |
| Khấu hao TSCĐ không đúng quy định | Vi phạm TT45/2013/TT-BTC |
| Chi không liên quan đến SXKD | Không đáp ứng điều kiện 1 |
| Lãi vay vượt 30% EBITDA (giao dịch liên kết) | NĐ 132/2020 — thin cap rule |

### Chi phí đặc biệt — Lưu ý

**Chi phí lãi vay (giao dịch liên kết — NĐ 132/2020):**
- Tổng chi phí lãi vay sau khi trừ lãi tiền gửi và cho vay bị giới hạn ở mức **30% EBITDA**
- Phần vượt quá được chuyển sang tối đa 5 năm tiếp theo
- Không áp dụng cho tổ chức tín dụng, công ty bảo hiểm, cho vay ODA/ưu đãi nhà nước

**Chi phí R&D:**
- Được tính vào chi phí được trừ
- Doanh nghiệp có thể lập **Quỹ phát triển KH&CN** trích tối đa 10% thu nhập tính thuế
- Quỹ phải sử dụng trong 5 năm, nếu không dùng hết phải nộp thuế + lãi

**Chi phí quảng cáo, khuyến mại, tiếp khách:**
- Bị khống chế ≤ **15% tổng chi phí được trừ** (trừ chi phí hàng mẫu)
- Ngoại trừ: DN hoạt động thương mại được tính thêm giá vốn hàng bán

## Ưu đãi thuế TNDN

### Điều kiện được hưởng ưu đãi

| Tiêu chí | Thuế suất ưu đãi | Thời gian miễn/giảm |
|----------|-----------------|---------------------|
| Dự án đầu tư mới vùng KT-XH khó khăn (Phụ lục I) | 17% | Miễn 2 năm, giảm 50% 4 năm |
| Dự án đầu tư mới vùng KT-XH đặc biệt khó khăn (Phụ lục II) | 10% | Miễn 4 năm, giảm 50% 9 năm |
| KCN (trừ KCN nằm ở đô thị loại 1) | 17% | Miễn 2 năm, giảm 50% 4 năm |
| KKT, KCX, KCN kỹ thuật cao | 10% | Miễn 4 năm, giảm 50% 9 năm |
| Công nghệ cao, phần mềm, R&D | 10% | Miễn 4 năm, giảm 50% 9 năm |
| DN KH&CN | 10% trong 5 năm đầu, 15% tiếp | Miễn 4 năm, giảm 50% 6 năm |

**Lưu ý quan trọng:**
- Ưu đãi tính từ năm đầu tiên có **thu nhập chịu thuế** (không tính từ năm đầu hoạt động)
- Năm đầu tiên có thu nhập chịu thuế nhưng hoạt động dưới 12 tháng → chọn bắt đầu từ năm đó hay năm sau
- Dự án đầu tư mở rộng (không phải đầu tư mới) được ưu đãi khác

### Chuyển lỗ
- Chuyển liên tục sang tối đa **5 năm** tiếp theo
- **KHÔNG** được chuyển ngược (carry back)
- Lỗ từ hoạt động chuyển nhượng BĐS, dự án đầu tư, chuyển nhượng dự án đầu tư: chuyển trực tiếp vào thu nhập từ hoạt động đó trong 5 năm sau

## Kê khai và nộp thuế

| Tờ khai | Hạn nộp | Nơi nộp |
|---------|---------|---------|
| Tạm nộp quý (ước tính) | Ngày 30 tháng đầu quý sau | CQT quản lý trực tiếp |
| Tổng hợp năm (QT) | **Ngày cuối tháng 3** năm sau | CQT quản lý trực tiếp |
| Quyết toán bổ sung | 10 ngày kể từ ngày phát hiện | CQT |

**Tạm nộp TNDN năm 2024 trở đi:**
- Tổng số thuế tạm nộp 3 quý đầu phải ≥ **75% số thuế phải nộp cả năm** (sửa từ Luật Quản lý thuế 38/2019 + NĐ 126/2020)

## Checklist thực hành

- [ ] Kiểm tra điều kiện 3 của chi phí: thực tế, hóa đơn, chứng từ không tiền mặt
- [ ] Rà soát chi vượt khống chế (quảng cáo, lãi vay liên kết)
- [ ] Xác nhận ưu đãi thuế còn thời hạn không
- [ ] Kiểm tra lỗ chưa chuyển và hạn 5 năm
- [ ] Giao dịch liên kết: có Mẫu 01/TKQ-TNDN chưa?
- [ ] Tạm nộp ≥75% quý 1-3?
