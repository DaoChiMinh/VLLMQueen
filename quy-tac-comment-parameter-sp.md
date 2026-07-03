# QUY TẮC COMMENT THAM SỐ STORED PROCEDURE
## Phục vụ AI Assistant tra cứu báo cáo ERP

**Phiên bản:** 1.0 — Áp dụng cho các SP nhóm báo cáo (CP_APP*)

---

## 1. Ngữ pháp chuẩn

Mỗi tham số khai báo trên **một dòng riêng**, comment bằng `--` đặt **cùng dòng**, theo cấu trúc:

```
-- [SYS] <Mô tả (format nếu có)>. [tra Bảng(khóa; tìm: cột,cột; lọc: đk; phụ thuộc: cột=@ThamSố)]. [Mặc định=X (chú thích)]
```

Trong đó phần trong `< >` là bắt buộc, phần trong `[ ]` là tùy chọn. Các phần ngăn nhau bằng dấu chấm + khoảng trắng `. `

---

## 2. Giải thích từng thành phần

### 2.1. `[SYS]` — Tham số hệ thống *(tùy chọn, nếu có phải đứng đầu)*

Đánh dấu tham số do **ứng dụng tự truyền** từ phiên đăng nhập hoặc cấu hình (user name, chế độ tải, mã đơn vị cơ sở theo phiên...). AI **không điền** và **không hỏi** người dùng về tham số này.

Tham số `[SYS]` không cần khai `Mặc định=`.

```sql
,@M_User_Name NVARCHAR(100) = 'ABC'  -- [SYS] User đăng nhập, app tự truyền
```

### 2.2. `<Mô tả (format nếu có)>` — BẮT BUỘC

Mô tả ngắn gọn ý nghĩa tham số bằng ngôn ngữ tự nhiên. Nếu dữ liệu có định dạng đặc biệt, ghi trong ngoặc đơn ngay sau mô tả:

- Ngày tháng: `(yyyyMMdd)`
- Danh sách nhiều giá trị: `(phân cách dấu phẩy)`
- Enum: liệt kê `giá_trị=ý_nghĩa` ngay trong mô tả, sau dấu hai chấm

```sql
,@M_Ngay_ct1 SMALLDATETIME       -- Ngày chứng từ bắt đầu (yyyyMMdd)
,@M_Loai NVARCHAR(10) = '1'      -- Loại báo cáo: 1=tổng hợp, 2=chi tiết, 3=so sánh. Mặc định='1'
```

### 2.3. `tra Bảng(...)` — Tra danh mục *(tùy chọn, chỉ với tham số mã)*

Khai báo cách chuyển từ **mô tả bằng lời** của người dùng thành **mã** truyền vào SP. Cú pháp đầy đủ:

```
tra Bảng(khóa; tìm: cột1,cột2; lọc: điều_kiện; phụ thuộc: cột=@ThamSốKhác)
```

| Thành phần | Bắt buộc? | Ý nghĩa |
|---|---|---|
| `Bảng` | Có | Tên bảng danh mục |
| `khóa` | Có | Cột chứa giá trị mã thực sự truyền vào tham số |
| `tìm:` | Có | Các cột được phép dò khi người dùng mô tả bằng lời (tên, địa chỉ, MST...). Cột đầu tiên là cột ưu tiên hiển thị |
| `lọc:` | Không | Điều kiện **tĩnh**, luôn áp khi tra (VD: `Status='1'` chỉ lấy bản ghi đang hoạt động) |
| `phụ thuộc:` | Không | Điều kiện **động** theo giá trị tham số khác trong cùng lần gọi (xem mục 2.5) |

```sql
,@M_Ma_KH NVARCHAR(50) = ''  -- Mã khách hàng. tra DMKH(Ma_KH; tìm: Ten_KH, Dia_Chi, Ma_So_Thue; lọc: Status='1'). Mặc định='' (tất cả)
```

Nghĩa là: khi người dùng nói "khách hàng Hòa Phát" hoặc "khách ở Cầu Giấy", hệ thống dò trong Ten_KH, Dia_Chi, Ma_So_Thue (chỉ các bản ghi Status='1') để tìm ra Ma_KH. Nếu khớp nhiều dòng, hệ thống hỏi lại người dùng kèm danh sách — không tự chọn.

### 2.4. `Mặc định=X (chú thích)` — Hành vi khi người dùng không nhắc đến

Đây là phần quyết định AI **tự điền hay hỏi lại**:

| Trường hợp | AI xử lý |
|---|---|
| **Có** `Mặc định=X` | Người dùng không nhắc đến → tự điền X, không hỏi |
| **Không có** `Mặc định=` | Tham số **bắt buộc** → thiếu thông tin thì AI hỏi lại người dùng, không tự đoán |

Phần `(chú thích)` sau giá trị là ghi chú tự do giúp người đọc và AI hiểu ý nghĩa của giá trị mặc định:

```sql
,@M_Ma_DV NVARCHAR(50) = ''   -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi). Mặc định='' (tất cả)
,@M_Ma_Dvcs NVARCHAR(50) = '01'  -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
,@M_Ngay_ct1 SMALLDATETIME    -- Ngày bắt đầu (yyyyMMdd)     <-- KHÔNG có Mặc định = BẮT BUỘC, AI sẽ hỏi nếu thiếu
```

**LƯU Ý QUAN TRỌNG:** Quên viết `Mặc định=` đồng nghĩa khai báo tham số là bắt buộc — AI sẽ hỏi người dùng. Khi review SP, tự hỏi một câu: *"tham số này tự điền mặc định mà không hỏi người dùng thì có ổn không?"*

### 2.5. `phụ thuộc:` — Ràng buộc liên tham số

Dùng khi giá trị hợp lệ của tham số này **phụ thuộc vào tham số khác** (nhóm vật tư → vật tư, đơn vị → kho...):

```sql
,@M_Ma_Nhom_VT NVARCHAR(50) = ''  -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
,@M_Ma_VT NVARCHAR(50) = ''       -- Mã vật tư. tra DMVT(Ma_VT; tìm: Ten_VT; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
```

Hệ thống dùng ràng buộc này theo 3 cách:

1. **Thu hẹp khi tra:** đã biết nhóm → chỉ dò vật tư trong nhóm đó
2. **Suy ngược:** người dùng chỉ nói tên vật tư → tra ra mã vật tư, đọc luôn được mã nhóm từ cùng dòng → tự điền tham số nhóm
3. **Phát hiện mâu thuẫn:** vật tư không thuộc nhóm đã chọn → hỏi lại người dùng thay vì chạy ra kết quả rỗng

Chuỗi nhiều cấp (ĐVCS → đơn vị → kho): mỗi tham số chỉ khai phụ thuộc **cấp liền trên**:

```sql
,@M_Ma_DV NVARCHAR(50) = ''   -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
,@M_Ma_Kho NVARCHAR(50) = ''  -- Mã kho. tra DMKHO(Ma_Kho; tìm: Ten_Kho; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
```

Trường hợp phụ thuộc phức tạp (qua bảng trung gian, nhiều-nhiều): cú pháp không tải được — mô tả bằng lời trong phần mô tả, xử lý đặc thù trong code.

---

## 3. Khối META cấp SP (đặt ngay sau dòng PROCEDURE)

```sql
/*===META===
MoTa: <1-2 câu SP làm gì, theo ngôn ngữ người dùng cuối>
TuKhoa: <các từ người dùng hay hỏi, cách nhau dấu phẩy, gồm cả từ đồng nghĩa>
BangNguon: <các bảng SP đọc, kèm chú thích ngắn trong ngoặc>
ViDu: <"câu hỏi tự nhiên" -> tham số tương ứng>
===END META===*/
```

---

## 4. Ví dụ mẫu hoàn chỉnh

```sql
ALTER PROCEDURE [dbo].[CP_APPNBBE_TonKhoVT]
/*===META===
MoTa: Báo cáo tồn kho vật tư theo kho và nhóm vật tư tại một thời điểm
TuKhoa: tồn kho, tồn, hàng tồn, kiểm kê, số lượng còn lại, inventory
BangNguon: TONKHO (số dư tồn kho), DMVT (danh mục vật tư), DMNVT (nhóm vật tư), DMKHO (danh mục kho)
ViDu: "Tồn kho xi măng tại kho Hà Nội cuối tháng 6" -> @M_Ngay_ct='20260630', @M_Ma_Nhom_VT='XM', @M_Ma_Kho='KHN'
===END META===*/
	@M_Load NVARCHAR(50) = '1'          -- [SYS] Chế độ tải: 1=tải mới, 0=làm mới cache
	,@M_Ngay_ct SMALLDATETIME           -- Ngày chốt tồn kho (yyyyMMdd)
	,@M_Ma_Dvcs NVARCHAR(50) = '01'     -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
	,@M_Ma_DV NVARCHAR(50) = ''         -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
	,@M_Ma_Kho NVARCHAR(500) = ''       -- DS mã kho (phân cách dấu phẩy). tra DMKHO(Ma_Kho; tìm: Ten_Kho; lọc: Status='1'; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
	,@M_Ma_Nhom_VT NVARCHAR(50) = ''    -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
	,@M_Ma_VT NVARCHAR(500) = ''        -- DS mã vật tư (phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT, Ma_Vach; lọc: Status='1'; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
	,@M_Loai NVARCHAR(10) = '1'         -- Loại báo cáo: 1=tổng hợp theo kho, 2=chi tiết từng vật tư. Mặc định='1'
	,@M_User_Name NVARCHAR(100) = 'ABC' -- [SYS] User đăng nhập, app tự truyền, dùng phân quyền
AS
BEGIN
	SET NOCOUNT ON;
	...
END
```

**Đọc thử vài dòng theo góc nhìn AI:**

- `@M_Ngay_ct`: không có `Mặc định=` → người dùng hỏi "tồn kho xi măng" không nói ngày → AI hỏi lại "Anh muốn xem tồn tại thời điểm nào?"
- `@M_Ma_Kho`: người dùng nói "kho ở Long Biên" → dò Ten_Kho không thấy nhưng nếu Ten_Kho chứa địa danh thì khớp; đã biết @M_Ma_DV thì chỉ dò kho của đơn vị đó
- `@M_Ma_VT`: người dùng nói "xi măng Hà Tiên" → tra DMVT ra mã, đồng thời đọc được Ma_Nhom_VT → tự điền ngược @M_Ma_Nhom_VT

---

## 5. Checklist khi viết/sửa SP

- [ ] Có khối `/*===META===` đủ MoTa, TuKhoa, BangNguon, ViDu
- [ ] Mỗi tham số một dòng, comment `--` cùng dòng
- [ ] Tham số hệ thống gắn `[SYS]` ở đầu comment
- [ ] Tham số ngày/danh sách ghi rõ format trong ngoặc đơn
- [ ] Tham số mã danh mục có `tra Bảng(khóa; tìm: ...)` — nhớ khai đủ các cột người dùng có thể mô tả (tên, địa chỉ, MST...)
- [ ] Tham số có ràng buộc với tham số khác → khai `phụ thuộc:`
- [ ] Soát từng tham số: *"tự điền mặc định không hỏi có ổn không?"* → Ổn thì viết `Mặc định=X`, không ổn thì BỎ TRỐNG (= bắt buộc, AI sẽ hỏi)
- [ ] `Mặc định=` phản ánh ĐÚNG hành vi thật trong thân SP (kiểm tra WHERE trước khi ghi `Mặc định='' (tất cả)`)

---

## 6. Từ khóa máy đọc — viết đúng chính tả

| Từ khóa | Vị trí | Ghi chú |
|---|---|---|
| `[SYS]` | Đầu comment | Viết hoa, trong ngoặc vuông |
| `tra` | Sau mô tả | Chữ thường |
| `tìm:` | Trong tra | Có dấu, có hai chấm |
| `lọc:` | Trong tra | Có dấu, có hai chấm |
| `phụ thuộc:` | Trong tra | Có dấu, có hai chấm |
| `Mặc định=` | Cuối comment | Viết hoa chữ M, có dấu bằng |

Các thành phần trong `tra(...)` ngăn nhau bằng dấu chấm phẩy `;`. Các phần lớn của comment ngăn nhau bằng dấu chấm + khoảng trắng `. `
