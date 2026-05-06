---
name: vietnam-transfer-pricing
version: 1.0.0
description: >
  Skill chuyên sâu về Giá chuyển nhượng (Transfer Pricing) tại Việt Nam theo NĐ132/2020/NĐ-CP
  và TT45/2021/TT-BTC. Bao gồm xác định bên liên kết, các phương pháp định giá, hồ sơ
  giá chuyển nhượng (Local File, Master File, CbCR), và thin cap rule.
category: tax
tags: [transfer-pricing, chuyen-gia, related-party, arm-length, vietnam]
applicable_bots: [partner, ja, sa]
editable: true
---

# Skill: Giá chuyển nhượng (Transfer Pricing) — Việt Nam

## Căn cứ pháp lý

| Văn bản | Số hiệu | Hiệu lực |
|---------|---------|---------|
| Nghị định | **NĐ132/2020/NĐ-CP** | Từ 20/12/2020 (thay NĐ20/2017) |
| Thông tư | **TT45/2021/TT-BTC** | Từ 03/8/2021 |
| Luật TNDN | 14/2008/QH12 sửa đổi | Cơ sở pháp lý |

## Xác định Bên liên kết (Điều 5, NĐ132/2020)

**Các trường hợp bên liên kết:**

1. Cùng góp ≥25% vốn điều lệ/vốn cổ phần có quyền biểu quyết
2. Một bên trực tiếp/gián tiếp sở hữu ≥25% của bên kia
3. Cùng do một bên thứ ba sở hữu ≥25%
4. Bên kiểm soát thành viên HĐQT/BKS/Ban lãnh đạo
5. Các bên cùng bảo lãnh cho nhau hoặc có vay từ một bên chiếm ≥25% vốn chủ sở hữu
6. Các bên thực hiện giao dịch chiếm ≥50% doanh thu/mua hàng
7. Mối quan hệ gia đình, vợ/chồng, cha mẹ, con cái... trong kinh doanh

## Các phương pháp định giá giao dịch liên kết

| Phương pháp | Viết tắt | Áp dụng khi |
|------------|---------|-------------|
| So sánh giá thị trường | **CUP** | Có giao dịch tương đương trên thị trường |
| Giá bán trừ lợi nhuận | **RPM** | Phân phối/bán lại không qua chế biến |
| Giá vốn cộng lãi | **CPM** | Sản xuất, gia công |
| Biên lợi nhuận giao dịch thuần | **TNMM** | Phổ biến nhất — so sánh biên lợi nhuận |
| Phân bổ lợi nhuận | **PSM** | Giao dịch phức tạp, có tài sản vô hình độc đáo |

**Thứ tự ưu tiên:** CUP → RPM/CPM → TNMM → PSM

## Hồ sơ giá chuyển nhượng (TP Documentation)

### Mẫu 01/TKQ-TNDN (bắt buộc nộp cùng tờ khai TNDN)

Tất cả DN có giao dịch liên kết phải nộp Mẫu 01/TKQ-TNDN kèm tờ khai TNDN năm, trừ khi được miễn.

**Trường hợp được miễn nộp Mẫu 01:**
- Doanh thu <200 tỷ VND VÀ chỉ giao dịch với bên liên kết trong VN (cùng áp thuế suất)
- Người nộp thuế đã được APA (thỏa thuận trước giá chuyển nhượng)

### Hồ sơ Local File (Hồ sơ quốc gia)

**Bắt buộc khi:** Tổng doanh thu ≥200 tỷ VND HOẶC giao dịch liên kết >20 tỷ (mỗi loại)

Nội dung gồm:
1. Thông tin chung về DN và giao dịch liên kết
2. Mô tả hoạt động kinh doanh, chuỗi giá trị
3. Phân tích chức năng, tài sản, rủi ro (FAR analysis)
4. Phân tích tương đương — so sánh với bên độc lập
5. Kết quả và điều chỉnh (nếu cần)

### Hồ sơ Master File (Hồ sơ tập đoàn)

**Bắt buộc khi:** DN là thành viên của MNE có **tổng doanh thu hợp nhất toàn cầu ≥18.000 tỷ VND** (tương đương ~750 triệu EUR)

### Country-by-Country Report (CbCR — Báo cáo lợi nhuận liên quốc gia)

**Bắt buộc khi:** DN là công ty mẹ tối cao của MNE tại VN, tổng doanh thu hợp nhất ≥18.000 tỷ
- Hoặc: DN VN được chỉ định thay mặt nhóm nộp CbCR tại VN

## Thin Capitalization Rule (Giới hạn lãi vay)

**Quy định tại Điều 16, NĐ132/2020:**

- Tổng chi phí lãi vay phát sinh trong kỳ (sau khi trừ lãi tiền gửi và cho vay) được giới hạn ở mức **30% EBITDA**
- Phần vượt quá: chuyển sang tối đa **5 năm tiếp theo**
- **Không áp dụng** cho: tổ chức tín dụng, công ty bảo hiểm, vay ODA, vay ưu đãi nhà nước

**Công thức:**

```
EBITDA = EBIT + Khấu hao + Phân bổ
Chi phí lãi vay được trừ = min(Chi phí lãi vay ròng, 30% × EBITDA)
```

## APA — Thỏa thuận trước về giá chuyển nhượng

- DN có thể đăng ký APA với TCT để được xác nhận phương pháp TP trước
- Thời hạn APA: tối đa 3 năm, gia hạn 2 năm
- Miễn phạt và không bị điều chỉnh TP trong thời hạn APA nếu thực hiện đúng

## Checklist Transfer Pricing

- [ ] Xác định tất cả bên liên kết theo Điều 5 NĐ132?
- [ ] Liệt kê tất cả giao dịch liên kết (loại, giá trị)?
- [ ] Phải nộp Mẫu 01/TKQ-TNDN kèm tờ khai?
- [ ] Có phải lập Local File không (>200 tỷ doanh thu)?
- [ ] Có phải lập Master File không (>18.000 tỷ hợp nhất)?
- [ ] Chi phí lãi vay liên kết ≤30% EBITDA?
- [ ] Phần lãi vay vượt từ năm trước còn trong 5 năm?
- [ ] Có thể cân nhắc APA không?
