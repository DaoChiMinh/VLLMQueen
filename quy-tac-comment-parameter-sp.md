# QUY TẮC COMMENT STORED PROCEDURE
## Phục vụ AI Assistant tra cứu báo cáo ERP


## 1. Khối META cấp PROCEDURE (đặt ngay sau dòng PROCEDURE)

Một PROCEDURE có thể phục vụ **nhiều báo cáo** khác nhau, phân biệt bởi giá trị của một hoặc nhiều tham số (thường là @M_Load). Mỗi báo cáo khai một khối `BaoCao`:

```sql
/*===META===
BaoCao: <Tên báo cáo> | <tham số định danh>
  TuKhoa: <từ khóa người dùng hay hỏi cho riêng báo cáo này>
  ViDu: <"câu hỏi tự nhiên" -> tham số>

BaoCao: <Tên báo cáo khác> | <tham số định danh>
  TuKhoa: ...
  ViDu: ...
===END META===*/
```

Quy tắc:

- Dòng `BaoCao:` gồm **tên báo cáo** (theo đúng tên nghiệp vụ người dùng biết), dấu `|`, rồi các cặp `@ThamSo='giá trị'` định danh biến thể, cách nhau dấu phẩy nếu nhiều Ví dụ: @M_Load = 1, @M_Kieu = 2
- `TuKhoa`: từ đồng nghĩa, viết tắt, tiếng Anh... người dùng hay dùng khi hỏi ĐÚNG báo cáo này
- `ViDu`: 1-3 ví dụ mapping câu hỏi → tham số, khuyến khích có
- PROCEDURE chỉ có một báo cáo → viết đúng một khối BaoCao (format thống nhất, không có ngoại lệ)
- Mọi biến thể dùng chung trọn bộ tham số của PROCEDURE — thân PROCEDURE tự IF ELSE theo tham số định danh

---

## 2. Ngữ pháp comment tham số

Mỗi tham số khai báo trên **một dòng riêng**, comment bằng `--` đặt **cùng dòng**:

```
-- [SYS|BC] <Mô tả (format nếu có)>. [tra Bảng(khóa; tìm: cột,cột; lọc: đk; phụ thuộc: cột=@ThamSố)]. [Mặc định=X (chú thích)]
```

Phần `< >` bắt buộc, phần `[ ]` tùy chọn. Các phần ngăn nhau bằng dấu chấm + khoảng trắng `. `

### 2.1. Nhãn đầu comment — 3 loại tham số

| Nhãn | Ý nghĩa | Ai điền giá trị |
|---|---|---|
| `[SYS]` | Tham số hệ thống | App tự truyền từ phiên đăng nhập/cấu hình. AI không điền, không hỏi |
| `[BC]` | Tham số định danh báo cáo | Lấy từ khối BaoCao đã match trong META. AI không điền, không hỏi |
| (không nhãn) | Tham số nghiệp vụ | AI điền từ câu hỏi người dùng, theo quy tắc Mặc định= |

Tham số `[SYS]` và `[BC]` không cần khai `Mặc định=`.

```sql
,@M_Load NVARCHAR(50) = '1'          -- [BC] Mã báo cáo, xác định bởi biến thể trong META
,@M_User_Name NVARCHAR(100) = 'ABC'  -- [SYS] User đăng nhập, app tự truyền
```

### 2.2. `<Mô tả (format nếu có)>` — BẮT BUỘC

Mô tả ngắn ý nghĩa tham số. Định dạng đặc biệt ghi trong ngoặc đơn ngay sau mô tả:

- Ngày tháng: `(yyyyMMdd)`
- Danh sách nhiều giá trị: `(phân cách dấu phẩy)`
- Enum: liệt kê `giá_trị=ý_nghĩa` trong mô tả, sau dấu hai chấm

```sql
,@M_Ngay_ct1 SMALLDATETIME       -- Ngày chứng từ bắt đầu (yyyyMMdd)
,@M_Kieu NVARCHAR(10) = '1'      -- Kiểu hiển thị: 1=theo kho, 2=theo vật tư. Mặc định='1'
```

### 2.3. `tra Bảng(...)` — Tra danh mục (chỉ với tham số mã)

Khai báo cách chuyển từ mô tả bằng lời của người dùng thành mã truyền vào SP:

```
tra Bảng(khóa; tìm: cột1,cột2; lọc: điều_kiện; phụ thuộc: cột=@ThamSốKhác)
```

| Thành phần | Bắt buộc? | Ý nghĩa |
|---|---|---|
| `Bảng` | Có | Tên bảng danh mục |
| `khóa` | Có | Cột chứa mã thực sự truyền vào tham số |
| `tìm:` | Có | Các cột được dò khi người dùng mô tả bằng lời (tên, địa chỉ, MST...). Cột đầu là cột ưu tiên hiển thị |
| `lọc:` | Không | Điều kiện TĨNH, luôn áp (VD: Status='1') |
| `phụ thuộc:` | Không | Điều kiện ĐỘNG theo giá trị tham số khác trong cùng lần gọi |

```sql
,@M_Ma_KH NVARCHAR(50) = ''  -- Mã khách hàng. tra DMKH(Ma_KH; tìm: Ten_KH, Dia_Chi, Ma_So_Thue; lọc: Status='1'). Mặc định='' (tất cả)
```

Nghĩa là: người dùng nói "khách Hòa Phát" hay "khách ở Cầu Giấy" → hệ thống dò Ten_KH, Dia_Chi, Ma_So_Thue (chỉ bản ghi Status='1') tìm ra Ma_KH. Khớp nhiều dòng → hỏi lại người dùng kèm danh sách, không tự chọn.

### 2.4. `Mặc định=X (chú thích)` — Hành vi khi người dùng không nhắc đến

| Trường hợp | AI xử lý |
|---|---|
| **Có** `Mặc định=X` | Không nhắc đến → tự điền X, không hỏi |
| **Không có** `Mặc định=` | Tham số **BẮT BUỘC** → thiếu thì AI hỏi lại người dùng, không tự đoán |

Phần `(chú thích)` sau giá trị giúp người đọc và AI hiểu ý nghĩa:

```sql
,@M_Ma_DV NVARCHAR(50) = ''      -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi). Mặc định='' (tất cả)
,@M_Ma_Dvcs NVARCHAR(50) = '01'  -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
,@M_Ngay_ct SMALLDATETIME        -- Ngày chốt tồn (yyyyMMdd)    <-- KHÔNG có Mặc định = BẮT BUỘC
```

**LƯU Ý:** Quên viết `Mặc định=` đồng nghĩa khai báo tham số là bắt buộc — AI sẽ hỏi người dùng. Khi review, tự hỏi: *"tham số này tự điền mặc định không hỏi có ổn không?"*

### 2.5. `phụ thuộc:` — Ràng buộc liên tham số

Dạng khi giá trị hợp lệ của tham số này phụ thuộc tham số khác (nhóm vật tư → vật tư, đơn vị → kho...):

```sql
,@M_Ma_Nhom_VT NVARCHAR(50) = ''  -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
,@M_Ma_VT NVARCHAR(50) = ''       -- Mã vật tư. tra DMVT(Ma_VT; tìm: Ten_VT; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
```

Hệ thống dùng ràng buộc theo 3 cách: (1) thu hẹp phạm vi dò khi đã biết tham số cha, (2) suy ngược — tra ra vật tư thì tự điền được nhóm, (3) phát hiện mâu thuẫn giữa hai tham số → hỏi lại thay vì chạy ra kết quả rỗng.

Chuỗi nhiều cấp: mỗi tham số chỉ khai phụ thuộc **cấp liền trên**:

```sql
,@M_Ma_DV NVARCHAR(50) = ''   -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
,@M_Ma_Kho NVARCHAR(50) = ''  -- Mã kho. tra DMKHO(Ma_Kho; tìm: Ten_Kho; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
```

Phụ thuộc phức tạp (bảng trung gian, nhiều-nhiều): mô tả bằng lời, xử lý đặc thù trong code.

---

## 3. Ví dụ mẫu hoàn chỉnh 
```sql
ALTER PROCEDURE [dbo].[CP_APPNBBE_TonKhoVT]
/*===META===
BaoCao: Bảng kê tồn kho vật tư
  TuKhoa: bảng kê tồn kho, danh sách tồn kho, tồn kho chi tiết, liệt kê tồn
  ViDu: "Bảng kê tồn kho xi măng cuối tháng 6" -> @M_Load='1', @M_Ngay_ct2='20260630', @M_Ma_Nhom_VT='XM'

===END META===*/
	@M_Load NVARCHAR(50) = '1'          -- [SYS] Chế độ tải: 1=tải mới, 0=làm mới cache
	,@M_Ngay_ct1 SMALLDATETIME          -- Ngày bắt đầu kỳ (yyyyMMdd)
	,@M_Ngay_ct2 SMALLDATETIME          -- Ngày kết thúc kỳ / ngày chốt tồn (yyyyMMdd)
	,@M_Ma_Dvcs NVARCHAR(50) = '01'     -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
	,@M_Ma_DV NVARCHAR(50) = ''         -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
	,@M_Ma_Kho NVARCHAR(500) = ''       -- DS mã kho (phân cách dấu phẩy). tra DMKHO(Ma_Kho; tìm: Ten_Kho; lọc: Status='1'; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
	,@M_Ma_Nhom_VT NVARCHAR(50) = ''    -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
	,@M_Ma_VT NVARCHAR(500) = ''        -- DS mã vật tư (phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT, Ma_Vach; lọc: Status='1'; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
	,@M_User_Name NVARCHAR(100) = 'ABC' -- [SYS] User đăng nhập, app tự truyền, dùng phân quyền
AS
BEGIN
	SET NOCOUNT ON;
	-- Dev tự IF ELSE theo @M_Load
	...
END
```
```sql
ALTER PROCEDURE [dbo].[CP_APPNBBE_TonKhoVT]
/*===META===
BaoCao: Bảng kê tồn kho vật tư | @M_Load='1'
  TuKhoa: bảng kê tồn kho, danh sách tồn kho, tồn kho chi tiết, liệt kê tồn
  ViDu: "Bảng kê tồn kho xi măng cuối tháng 6" -> @M_Load='1', @M_Ngay_ct2='20260630', @M_Ma_Nhom_VT='XM'

BaoCao: Tổng hợp tồn kho vật tư | @M_Load='2'
  TuKhoa: tổng hợp tồn kho, tồn kho theo nhóm, tồn kho tổng, tồn theo kho
  ViDu: "Tổng tồn kho từng kho cuối tháng 6" -> @M_Load='2', @M_Ngay_ct2='20260630'

BaoCao: Tổng hợp nhập xuất tồn | @M_Load='3'
  TuKhoa: nhập xuất tồn, NXT, xuất nhập tồn, biến động kho, nhập xuất trong kỳ
  ViDu: "Nhập xuất tồn quý 2" -> @M_Load='3', @M_Ngay_ct1='20260401', @M_Ngay_ct2='20260630'
===END META===*/
	@M_Load NVARCHAR(50) = '1'          -- [BC] Mã báo cáo, xác định bởi biến thể trong META
	,@M_Ngay_ct1 SMALLDATETIME          -- Ngày bắt đầu kỳ (yyyyMMdd)
	,@M_Ngay_ct2 SMALLDATETIME          -- Ngày kết thúc kỳ / ngày chốt tồn (yyyyMMdd)
	,@M_Ma_Dvcs NVARCHAR(50) = '01'     -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
	,@M_Ma_DV NVARCHAR(50) = ''         -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
	,@M_Ma_Kho NVARCHAR(500) = ''       -- DS mã kho (phân cách dấu phẩy). tra DMKHO(Ma_Kho; tìm: Ten_Kho; lọc: Status='1'; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
	,@M_Ma_Nhom_VT NVARCHAR(50) = ''    -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
	,@M_Ma_VT NVARCHAR(500) = ''        -- DS mã vật tư (phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT, Ma_Vach; lọc: Status='1'; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
	,@M_User_Name NVARCHAR(100) = 'ABC' -- [SYS] User đăng nhập, app tự truyền, dùng phân quyền
AS
BEGIN
	SET NOCOUNT ON;
	-- Dev tự IF ELSE theo @M_Load
	...
END
```
```sql
ALTER PROCEDURE [dbo].[CP_APPNBBE_TonKhoVT]
/*===META===
BaoCao: Bảng kê nhập vật tư | @M_Load='1', @M_Kieu='N'
  TuKhoa: bảng kê nhập, nhập kho, phiếu nhập, hàng nhập về
  ViDu: "Bảng kê nhập vật tư tháng 6" -> @M_Load='1', @M_Kieu='N', @M_Ngay_ct1='20260601', @M_Ngay_ct2='20260630'

BaoCao: Bảng kê xuất vật tư | @M_Load='1', @M_Kieu='X'
  TuKhoa: bảng kê xuất, xuất kho, phiếu xuất, hàng xuất đi
  ViDu: "Xuất kho tháng 6 của kho HN" -> @M_Load='1', @M_Kieu='X', @M_Ma_Kho='KHN'

BaoCao: Tổng hợp nhập xuất theo vật tư | @M_Load='2', @M_Kieu=''
  TuKhoa: tổng hợp nhập xuất, NX theo vật tư
  ViDu: "Tổng nhập xuất từng mặt hàng quý 2" -> @M_Load='2', @M_Ngay_ct1='20260401', @M_Ngay_ct2='20260630'
===END META===*/
	@M_Load NVARCHAR(50) = '1'   -- [BC] Mã báo cáo, xác định bởi biến thể trong META
	,@M_Kieu NVARCHAR(10) = ''   -- [BC] Kiểu nhập/xuất, xác định bởi biến thể trong META
	,@M_Ngay_ct1 SMALLDATETIME          -- Ngày bắt đầu kỳ (yyyyMMdd)
	,@M_Ngay_ct2 SMALLDATETIME          -- Ngày kết thúc kỳ / ngày chốt tồn (yyyyMMdd)
	,@M_Ma_Dvcs NVARCHAR(50) = '01'     -- Mã đơn vị cơ sở. tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
	,@M_Ma_DV NVARCHAR(50) = ''         -- Mã đơn vị. tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
	,@M_Ma_Kho NVARCHAR(500) = ''       -- DS mã kho (phân cách dấu phẩy). tra DMKHO(Ma_Kho; tìm: Ten_Kho; lọc: Status='1'; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
	,@M_Ma_Nhom_VT NVARCHAR(50) = ''    -- Mã nhóm vật tư. tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
	,@M_Ma_VT NVARCHAR(500) = ''        -- DS mã vật tư (phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT, Ma_Vach; lọc: Status='1'; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
	,@M_User_Name NVARCHAR(100) = 'ABC' -- [SYS] User đăng nhập, app tự truyền, dùng phân quyền
AS
BEGIN
	SET NOCOUNT ON;
	-- Dev tự IF ELSE theo @M_Load
	...
END
```
**Đọc thử theo góc nhìn AI:**

- Người dùng hỏi "cho xem NXT quý 2" → retrieval match biến thể `Tổng hợp nhập xuất tồn` (nhờ từ khóa "NXT") → @M_Load='3' lấy từ META, AI chỉ còn lo điền ngày + các bộ lọc
- "@M_Ngay_ct2 không có Mặc định=" → hỏi "tồn kho hiện tại" mà không rõ mốc ngày → AI hỏi lại thời điểm chốt
- "xi măng Hà Tiên" → tra DMVT ra mã, đọc cùng dòng được Ma_Nhom_VT → tự điền ngược @M_Ma_Nhom_VT

---

## 4. Checklist khi viết/sửa SP

- [ ] Có khối `/*===META===` với ít nhất một khối `BaoCao` (tên | tham số định danh + TuKhoa + ViDu)
- [ ] PROCEDURE nhiều báo cáo → mỗi báo cáo một khối BaoCao, từ khóa riêng không trộn lẫn
- [ ] Tham số định danh báo cáo (như @M_Load) gắn nhãn `[BC]`
- [ ] Tham số hệ thống gắn nhãn `[SYS]`
- [ ] Mỗi tham số một dòng, comment `--` cùng dòng
- [ ] Tham số ngày/danh sách ghi rõ format trong ngoặc đơn
- [ ] Tham số mã danh mục có `tra Bảng(khóa; tìm: ...)` — khai đủ các cột người dùng có thể mô tả
- [ ] Tham số ràng buộc nhau → khai `phụ thuộc:` (chỉ cấp liền trên)
- [ ] Soát từng tham số nghiệp vụ: *"tự điền mặc định không hỏi có ổn không?"* → Ổn: viết `Mặc định=X`. Không: BỎ TRỐNG (= bắt buộc, AI hỏi)
- [ ] `Mặc định=` phản ánh ĐÚNG hành vi thật trong thân PROCEDURE (kiểm tra WHERE trước khi ghi `Mặc định='' (tất cả)`)

---

## 5. Từ khóa máy đọc — viết đúng chính tả

| Từ khóa | Vị trí | Ghi chú |
|---|---|---|
| `BaoCao:` | Trong META | Viết hoa B, C, có hai chấm. Tên và tham số định danh ngăn bằng dấu `\|` |
| `TuKhoa:` | Trong khối BaoCao | Thụt lề, có hai chấm |
| `ViDu:` | Trong khối BaoCao | Thụt lề, có hai chấm |
| `[SYS]` | Đầu comment tham số | Viết hoa, ngoặc vuông |
| `[BC]` | Đầu comment tham số | Viết hoa, ngoặc vuông |
| `tra` | Sau mô tả | Chữ thường |
| `tìm:` | Trong tra | Có dấu, có hai chấm |
| `lọc:` | Trong tra | Có dấu, có hai chấm |
| `phụ thuộc:` | Trong tra | Có dấu, có hai chấm |
| `Mặc định=` | Cuối comment | Viết hoa M, có dấu bằng |

Trong `tra(...)`: các thành phần ngăn bằng `;`. Các phần lớn của comment ngăn bằng `. ` (chấm + khoảng trắng).

**Ghi chú cho parser (không phải việc của người viết SP):** danh sách bảng nguồn không cần khai tay — bảng danh mục gom tự động từ các cụm `tra Bảng(...)`, bảng dữ liệu trích tự động từ FROM/JOIN trong thân SP.