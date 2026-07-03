# QUY TẮC VIẾT META & COMMENT THAM SỐ STORED PROCEDURE
## Phục vụ AI Assistant tra cứu báo cáo ERP

| | |
|---|---|
| **Phiên bản** | 1.2 |
| **Phạm vi áp dụng** | Các  PROCEDURE  báo cáo (nhóm CP_*) |
| **Đối tượng đọc** | Dev viết/bảo trì stored procedure |

---

# PHẦN A — TỔNG QUAN

## A.1. Mục đích

Hệ thống AI Assistant cho phép người dùng hỏi bằng ngôn ngữ tự nhiên ("cho xem nhập xuất tồn quý 2 của kho Hà Nội") và tự động: **chọn đúng báo cáo → điền đúng tham số → gọi  PROCEDURE **. Để làm được, mỗi  PROCEDURE  phải khai báo metadata theo quy tắc trong tài liệu này. Metadata gồm 2 phần:

1. **Khối META** (đầu  PROCEDURE ): khai báo các *báo cáo* mà  PROCEDURE  phục vụ — dùng để AI tìm đúng báo cáo từ câu hỏi
2. **Comment tham số** (inline từng dòng): khai báo ý nghĩa, cách tra cứu, hành vi mặc định — dùng để AI điền đúng giá trị

## A.2. Nguyên tắc thiết kế

- **Chỉ viết tay thứ máy không tự suy được**: ý nghĩa nghiệp vụ, từ khóa người dùng, ví dụ. Danh sách bảng nguồn KHÔNG khai tay — parser tự trích từ các cụm `tra` và từ FROM/JOIN trong thân  PROCEDURE .
- **Metadata sống sát code**: mô tả tham số nằm cùng dòng khai báo để người sửa  PROCEDURE  nhìn thấy và cập nhật kịp.
- **Metadata phản ánh đúng hành vi thật**: metadata sai nguy hiểm hơn thiếu, vì AI sẽ tự tin làm sai.
- **Một ngữ pháp cho mọi  PROCEDURE **:  PROCEDURE  một báo cáo hay nhiều báo cáo dùng chung format, không có ngoại lệ.

## A.3. Ba loại tham số — ai điền giá trị?

| Nhãn | Tên gọi | Ai điền | AI có hỏi người dùng? |
|---|---|---|---|
| `[SYS]` | Tham số hệ thống | App tự truyền (từ phiên đăng nhập, cấu hình) | Không |
| `[BC]` | Tham số định danh báo cáo | Lấy từ khối BaoCao đã match trong META | Không |
| *(không nhãn)* | Tham số nghiệp vụ | AI điền từ câu hỏi, theo quy tắc `Mặc định=` | Có, nếu bắt buộc mà thiếu |

---

# PHẦN B — KHỐI META (CẤP  PROCEDURE )

## B.1. Vị trí và khung

Đặt **ngay sau dòng `ALTER/CREATE PROCEDURE`**, trước phần khai báo tham số:

```sql
/*===META===
BaoCao: <Tên báo cáo> | <tham số định danh>
  TuKhoa: <từ khóa>
  ViDu: <ví dụ mapping>
===END META===*/
```

## B.2. Khối BaoCao — đơn vị khai báo báo cáo

Một  PROCEDURE  có thể phục vụ **nhiều báo cáo** khác nhau (phân biệt bởi giá trị tham số như @M_Load,...). Mỗi báo cáo khai một khối `BaoCao` gồm 3 dòng:

### Dòng 1 — `BaoCao: <Tên> | <tham số định danh>`

- **Tên báo cáo**: đúng tên nghiệp vụ mà người dùng biết. Đây là thông tin quan trọng nhất để AI match câu hỏi.
- **Tham số định danh** (sau dấu `|`): các cặp `@ThamSo='giá trị'` xác định biến thể này, cách nhau dấu phẩy nếu nhiều.

### Dòng 2 — `TuKhoa:` *(bắt buộc)*

Từ khóa người dùng hay dùng khi hỏi **đúng báo cáo này**: từ đồng nghĩa, viết tắt (NXT), tiếng Anh nếu có. Viết theo ngôn ngữ người dùng cuối, không theo ngôn ngữ dev. Không trộn từ khóa của biến thể này sang biến thể khác.

### Dòng 3 — `ViDu:` *(khuyến khích)*

1–3 ví dụ mapping `"câu hỏi tự nhiên" -> tham số`. Ví dụ giúp AI học cách điền tham số — đặc biệt giá trị với model nhỏ.

## B.3. Quy tắc theo số lượng báo cáo và tham số định danh

### Trường hợp 1 —  PROCEDURE  chỉ có MỘT báo cáo

Viết đúng một khối BaoCao, **bỏ luôn phần sau dấu `|`** (không có biến thể cần phân biệt):

```sql
/*===META===
BaoCao: Báo cáo doanh thu bán hàng
  TuKhoa: doanh thu, doanh số, bán hàng, revenue
  ViDu: "Doanh thu tháng 12/2025" -> @M_Ngay_ct1='20251201', @M_Ngay_ct2='20251231'
===END META===*/
```

Lưu ý:  PROCEDURE  đơn thì @M_Load (nếu có) thường chỉ là cờ kỹ thuật do app truyền → gắn nhãn `[SYS]`, không phải `[BC]`. **Nhãn phản ánh vai trò trong  PROCEDURE  đó, không gắn cứng theo tên tham số.**

### Trường hợp 2 —  PROCEDURE  nhiều báo cáo, MỘT tham số định danh

```sql
/*===META===
BaoCao: Bảng kê tồn kho vật tư | @M_Load='1'
  TuKhoa: bảng kê tồn kho, danh sách tồn kho, tồn kho chi tiết
  ViDu: "Bảng kê tồn kho xi măng cuối tháng 6" -> @M_Load='1', @M_Ngay_ct2='20260630', @M_Ma_Nhom_VT='XM'

BaoCao: Tổng hợp tồn kho vật tư | @M_Load='2'
  TuKhoa: tổng hợp tồn kho, tồn kho theo nhóm, tồn theo kho
  ViDu: "Tổng tồn kho từng kho cuối tháng 6" -> @M_Load='2', @M_Ngay_ct2='20260630'

BaoCao: Tổng hợp nhập xuất tồn | @M_Load='3'
  TuKhoa: nhập xuất tồn, NXT, xuất nhập tồn, biến động kho
  ViDu: "Nhập xuất tồn quý 2" -> @M_Load='3', @M_Ngay_ct1='20260401', @M_Ngay_ct2='20260630'
===END META===*/
```

### Trường hợp 3 —  PROCEDURE  nhiều báo cáo, NHIỀU tham số định danh

Liệt kê đủ các cặp sau dấu `|`, cách nhau dấu phẩy:

```sql
/*===META===
BaoCao: Bảng kê nhập vật tư | @M_Load='1', @M_Kieu='N'
  TuKhoa: bảng kê nhập, nhập kho, phiếu nhập
  ViDu: "Bảng kê nhập vật tư tháng 6" -> @M_Load='1', @M_Kieu='N', @M_Ngay_ct1='20260601', @M_Ngay_ct2='20260630'

BaoCao: Bảng kê xuất vật tư | @M_Load='1', @M_Kieu='X'
  TuKhoa: bảng kê xuất, xuất kho, phiếu xuất
  ViDu: "Xuất kho tháng 6 của kho HN" -> @M_Load='1', @M_Kieu='X', @M_Ma_Kho='KHN'

BaoCao: Tổng hợp nhập xuất theo vật tư | @M_Load='2', @M_Kieu=''
  TuKhoa: tổng hợp nhập xuất, NX theo vật tư
  ViDu: "Tổng nhập xuất từng mặt hàng quý 2" -> @M_Load='2', @M_Ngay_ct1='20260401', @M_Ngay_ct2='20260630'
===END META===*/
```

**Ba quy tắc bắt buộc với nhiều tham số định danh:**

1. Mọi tham số xuất hiện sau dấu `|` ở BẤT KỲ khối nào đều phải gắn nhãn `[BC]` trong phần khai báo tham số
2. Mỗi khối BaoCao phải khai đủ giá trị cho TẤT CẢ tham số [BC] — kể cả giá trị rỗng (viết rõ `@M_Kieu=''`), không bỏ lửng
3. Tổ hợp giá trị định danh của mỗi khối phải DUY NHẤT — hai khối trùng nhau toàn bộ là lỗi khai báo

Ghi chú: chỉ khai các tổ hợp **thực sự là báo cáo có tên** — không cần khai mọi hoán vị. Tổ hợp không khai thì không tồn tại với AI.

---

# PHẦN C — COMMENT THAM SỐ (INLINE)

## C.1. Ngữ pháp chuẩn

Mỗi tham số khai báo trên **một dòng riêng**, comment bằng `--` đặt **cùng dòng**:

```
-- [SYS|BC] <Mô tả (thông tin bổ sung)>. [tra Bảng(khóa; tìm: cột,cột; lọc: đk; phụ thuộc: cột=@ThamSố)]. [Mặc định=X (chú thích)]
```

- Phần trong `< >`: bắt buộc. Phần trong `[ ]`: tùy chọn.
- Các phần lớn ngăn nhau bằng **dấu chấm + khoảng trắng** `. `
- Thành phần trong `tra(...)` ngăn nhau bằng **dấu chấm phẩy** `;`

## C.2. Nhãn `[SYS]` / `[BC]` — đứng đầu comment nếu có

```sql
,@M_Load NVARCHAR(50) = '1'          -- [BC] Mã báo cáo, xác định bởi biến thể trong META
,@M_Kieu NVARCHAR(10) = ''           -- [BC] Kiểu nhập/xuất, xác định bởi biến thể trong META
,@M_User_Name NVARCHAR(100) = 'ABC'  -- [SYS] User đăng nhập, app tự truyền
```

Tham số `[SYS]` và `[BC]` **không cần** khai `Mặc định=` và không cần `tra`.

## C.3. Mô tả và thông tin bổ sung trong ngoặc đơn

Mô tả ngắn gọn ý nghĩa tham số, theo ngôn ngữ tự nhiên. Ngoặc đơn ngay sau mô tả chứa thông tin bổ sung, tùy loại tham số:

| Loại tham số | Nội dung ngoặc đơn | Ví dụ |
|---|---|---|
| Mã danh mục (có `tra`) | **Tên danh mục nghiệp vụ** | `Mã đơn vị (Danh mục đơn vị)` |
| Ngày tháng | Định dạng | `Ngày bắt đầu (yyyyMMdd)` |
| Danh sách nhiều giá trị | Cách phân cách (+ tên danh mục nếu có tra) | `DS mã vật tư (Danh mục vật tư, phân cách dấu phẩy)` |
| Enum | Không dùng ngoặc — liệt kê sau dấu hai chấm | `Loại: 1=tổng hợp, 2=chi tiết` |

Nhiều thông tin trong cùng ngoặc: cách nhau dấu phẩy.

```sql
,@M_Ma_DV NVARCHAR(50) = ''    -- Mã đơn vị (Danh mục đơn vị). tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi). Mặc định='' (tất cả)
,@M_Ngay_ct1 SMALLDATETIME     -- Ngày bắt đầu kỳ (yyyyMMdd)
,@M_Ma_VT NVARCHAR(500) = ''   -- DS mã vật tư (Danh mục vật tư, phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT). Mặc định='' (tất cả)
,@M_Loai NVARCHAR(10) = '1'    -- Loại báo cáo: 1=tổng hợp, 2=chi tiết, 3=so sánh. Mặc định='1'
```

Mục đích của tên danh mục trong ngoặc: cho AI ngữ cảnh tiếng Việt (không phải đoán từ chữ viết tắt DMDV), và làm tên hiển thị khi assistant hỏi lại người dùng ("Tìm thấy 3 kết quả trong *Danh mục đơn vị*...").

## C.4. `tra Bảng(...)` — khai báo tra danh mục

Chỉ dùng với tham số nhận **mã** từ bảng danh mục. Khai báo cách hệ thống chuyển *mô tả bằng lời* của người dùng ("chi nhánh ở Cầu Giấy") thành *mã* truyền vào  PROCEDURE :

```
tra Bảng(khóa; tìm: cột1,cột2; lọc: điều_kiện; phụ thuộc: cột=@ThamSốKhác)
```

| Thành phần | Bắt buộc? | Ý nghĩa |
|---|---|---|
| `Bảng` | Có | Tên bảng danh mục |
| `khóa` | Có | Cột chứa mã thực sự truyền vào tham số |
| `tìm:` | Có | Các cột được dò khi người dùng mô tả bằng lời (tên, địa chỉ, MST, mã vạch...). Cột đầu là cột ưu tiên hiển thị |
| `lọc:` | Không | Điều kiện **TĨNH**, luôn áp mỗi lần tra (VD: `Status='1'` — chỉ bản ghi đang hoạt động) |
| `phụ thuộc:` | Không | Điều kiện **ĐỘNG** theo giá trị tham số khác trong cùng lần gọi (xem C.6) |

```sql
,@M_Ma_KH NVARCHAR(50) = ''  -- Mã khách hàng (Danh mục khách hàng). tra DMKH(Ma_KH; tìm: Ten_KH, Dia_Chi, Ma_So_Thue; lọc: Status='1'). Mặc định='' (tất cả)
```

**Cách hệ thống dùng:** người dùng nói "khách Hòa Phát" hoặc "khách ở Cầu Giấy" → dò trong Ten_KH, Dia_Chi, Ma_So_Thue (chỉ bản ghi Status='1') → ra Ma_KH. Khớp nhiều dòng → hỏi lại người dùng kèm danh sách, KHÔNG tự chọn.

**Lưu ý khi viết:** khai đủ mọi cột người dùng có thể dùng để mô tả — thiếu cột `Dia_Chi` thì câu hỏi "chi nhánh ở Cầu Giấy" sẽ không resolve được.

## C.5. `Mặc định=X (chú thích)` — hành vi khi người dùng không nhắc đến

Quy tắc quan trọng nhất của toàn ngữ pháp — quyết định AI **tự điền hay hỏi lại**:

| Trường hợp | AI xử lý khi câu hỏi không nhắc đến tham số |
|---|---|
| **Có** `Mặc định=X` | Tự điền X, không hỏi |
| **KHÔNG có** `Mặc định=` | Tham số **BẮT BUỘC** → AI hỏi lại người dùng, không tự đoán |

Phần `(chú thích)` sau giá trị: ghi chú tự do giúp người đọc và AI hiểu ý nghĩa của giá trị mặc định — quan trọng nhất là `Mặc định='' (tất cả)` cho biết chuỗi rỗng nghĩa là "không lọc, lấy toàn bộ".

```sql
,@M_Ma_DV NVARCHAR(50) = ''      -- Mã đơn vị (Danh mục đơn vị). tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi). Mặc định='' (tất cả)
,@M_Ma_Dvcs NVARCHAR(50) = '01'  -- Mã đơn vị cơ sở (Danh mục ĐVCS). tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
,@M_Ngay_ct SMALLDATETIME        -- Ngày chốt tồn (yyyyMMdd)          <-- không có Mặc định = BẮT BUỘC
```

**Hai điều phải soát khi review:**

1. *"Tham số này tự điền mặc định mà không hỏi người dùng thì có ổn không?"* — Ổn: viết `Mặc định=X`. Không ổn: BỎ TRỐNG.
2. `Mặc định=` phải phản ánh **đúng hành vi thật trong thân  PROCEDURE ** — kiểm tra mệnh đề WHERE trước khi ghi `Mặc định='' (tất cả)`. Nếu  PROCEDURE  xử lý chuỗi rỗng theo cách khác (báo lỗi, không trả dòng nào) thì KHÔNG được ghi vậy.

Ghi chú thiết kế: quên `Mặc định=` khiến AI hỏi thừa (phiền nhưng an toàn); ghi `Mặc định=` sai khiến AI điền sai không hỏi (nguy hiểm). Khi phân vân, thiên về bỏ trống.

## C.6. `phụ thuộc:` — ràng buộc liên tham số

D�ng khi giá trị hợp lệ của tham số này phụ thuộc tham số khác: nhóm vật tư → vật tư, đơn vị → kho, khách hàng → hợp đồng...

```sql
,@M_Ma_Nhom_VT NVARCHAR(50) = ''  -- Mã nhóm vật tư (Danh mục nhóm VT). tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
,@M_Ma_VT NVARCHAR(50) = ''       -- Mã vật tư (Danh mục vật tư). tra DMVT(Ma_VT; tìm: Ten_VT; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
```

Đọc là: *khi tra DMVT, nếu @M_Ma_Nhom_VT đã có giá trị thì thêm điều kiện `Ma_Nhom_VT = <giá trị đó>`; nếu rỗng thì tra toàn bảng.*

**Hệ thống dùng ràng buộc theo 3 cách:**

1. **Thu hẹp khi tra xuôi**: đã biết nhóm → chỉ dò vật tư trong nhóm, tránh trùng tên khác nhóm
2. **Suy ngược**: người dùng chỉ nói "xi măng Hà Tiên" → tra ra Ma_VT, đọc cùng dòng được Ma_Nhom_VT → tự điền ngược tham số nhóm, đỡ hỏi thừa
3. **Phát hiện mâu thuẫn**: vật tư không thuộc nhóm đã chọn → hỏi lại người dùng thay vì chạy  PROCEDURE  ra kết quả rỗng khó hiểu

**Chuỗi nhiều cấp** (ĐVCS → đơn vị → kho): mỗi tham số chỉ khai phụ thuộc **cấp liền trên**, chuỗi tự nối:

```sql
,@M_Ma_DV NVARCHAR(50) = ''   -- Mã đơn vị (Danh mục đơn vị). tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
,@M_Ma_Kho NVARCHAR(50) = ''  -- Mã kho (Danh mục kho). tra DMKHO(Ma_Kho; tìm: Ten_Kho; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
```

**Giới hạn**: phụ thuộc phức tạp (qua bảng trung gian, quan hệ nhiều-nhiều) không đưa vào cú pháp — mô tả bằng lời trong phần mô tả và xử lý đặc thù trong code.

---

# PHẦN D — VÍ DỤ MẪU HOÀN CHỈNH

 PROCEDURE  đa báo cáo, hội tụ đủ các trường hợp: [BC], [SYS], bắt buộc, tra đa cột, lọc, phụ thuộc chuỗi, danh sách nhiều giá trị:

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
	,@M_Ma_Dvcs NVARCHAR(50) = '01'     -- Mã đơn vị cơ sở (Danh mục ĐVCS). tra DMDVCS(Ma_Dvcs; tìm: Ten_Dvcs). Mặc định='01'
	,@M_Ma_DV NVARCHAR(50) = ''         -- Mã đơn vị (Danh mục đơn vị). tra DMDV(Ma_DV; tìm: Ten_DV, Dia_Chi; phụ thuộc: Ma_Dvcs=@M_Ma_Dvcs). Mặc định='' (tất cả)
	,@M_Ma_Kho NVARCHAR(500) = ''       -- DS mã kho (Danh mục kho, phân cách dấu phẩy). tra DMKHO(Ma_Kho; tìm: Ten_Kho; lọc: Status='1'; phụ thuộc: Ma_DV=@M_Ma_DV). Mặc định='' (tất cả)
	,@M_Ma_Nhom_VT NVARCHAR(50) = ''    -- Mã nhóm vật tư (Danh mục nhóm VT). tra DMNVT(Ma_Nhom_VT; tìm: Ten_Nhom_VT). Mặc định='' (tất cả)
	,@M_Ma_VT NVARCHAR(500) = ''        -- DS mã vật tư (Danh mục vật tư, phân cách dấu phẩy). tra DMVT(Ma_VT; tìm: Ten_VT, Ma_Vach; lọc: Status='1'; phụ thuộc: Ma_Nhom_VT=@M_Ma_Nhom_VT). Mặc định='' (tất cả)
	,@M_User_Name NVARCHAR(100) = 'ABC' -- [SYS] User đăng nhập, app tự truyền, dùng phân quyền
AS
BEGIN
	SET NOCOUNT ON;
	-- Dev tự IF ELSE theo @M_Load
	...
END
```

**Luồng xử lý minh họa — người dùng hỏi: "cho xem NXT quý 2 của kho Hà Nội"**

1. Match từ khóa "NXT" → biến thể *Tổng hợp nhập xuất tồn* → `@M_Load='3'` (từ META, nhãn [BC])
2. "quý 2" → `@M_Ngay_ct1='20260401'`, `@M_Ngay_ct2='20260630'` (học từ ViDu)
3. "kho Hà Nội" → tra DMKHO theo Ten_Kho → ra Ma_Kho; đọc cùng dòng được Ma_DV → tự điền ngược @M_Ma_DV
4. @M_Ma_Dvcs không được nhắc → điền Mặc định='01'; @M_Ma_Nhom_VT, @M_Ma_VT → điền '' (tất cả)
5. @M_User_Name → app truyền từ phiên đăng nhập
6. Đủ tham số → gọi  PROCEDURE 

Nếu người dùng chỉ hỏi "cho xem NXT" (thiếu thời gian): @M_Ngay_ct1/ct2 không có Mặc định= → AI hỏi lại "Anh muốn xem kỳ nào?"

---

# PHẦN E — CHECKLIST & TRA CỨU NHANH

## E.1. Checklist khi viết/sửa  PROCEDURE 

**Khối META:**
- [ ] Có `/*===META===` với ít nhất một khối BaoCao (mọi  PROCEDURE , kể cả đơn báo cáo)
- [ ] Mỗi khối đủ: tên báo cáo đúng tên nghiệp vụ + TuKhoa + ViDu
- [ ]  PROCEDURE  nhiều báo cáo: từ khóa từng biến thể riêng biệt, không trộn lẫn
- [ ] Nhiều tham số định danh: mỗi khối khai ĐỦ giá trị mọi tham số [BC] (kể cả rỗng); tổ hợp không trùng nhau

**Comment tham số:**
- [ ] Mỗi tham số một dòng, comment `--` cùng dòng
- [ ] Tham số sau dấu `|` trong META → gắn `[BC]`; tham số app truyền → gắn `[SYS]`
- [ ] Tham số mã danh mục: ngoặc đơn ghi tên danh mục + có `tra Bảng(khóa; tìm: ...)` khai đủ cột người dùng có thể mô tả
- [ ] Tham số ngày/danh sách: ghi format trong ngoặc đơn
- [ ] Tham số ràng buộc nhau: khai `phụ thuộc:` (chỉ cấp liền trên)
- [ ] Soát từng tham số nghiệp vụ: *tự điền không hỏi có ổn?* → Ổn: `Mặc định=X`. Không: bỏ trống (= bắt buộc)
- [ ] `Mặc định=` khớp hành vi thật trong thân  PROCEDURE  (soát WHERE trước khi ghi `Mặc định='' (tất cả)`)

## E.2. Bảng từ khóa máy đọc — viết đúng chính tả

| Từ khóa | Vị trí | Ghi chú |
|---|---|---|
| `BaoCao:` | META | Viết hoa B, C. Tên và tham số định danh ngăn bằng `\|`; nhiều tham số cách nhau `,` |
| `TuKhoa:` | Trong khối BaoCao | Thụt lề 2 khoảng trắng |
| `ViDu:` | Trong khối BaoCao | Thụt lề 2 khoảng trắng |
| `[SYS]` | Đầu comment tham số | Viết hoa, ngoặc vuông |
| `[BC]` | Đầu comment tham số | Viết hoa, ngoặc vuông |
| `tra` | Sau mô tả | Chữ thường |
| `tìm:` | Trong tra | Có dấu tiếng Việt |
| `lọc:` | Trong tra | Có dấu tiếng Việt |
| `phụ thuộc:` | Trong tra | Có dấu tiếng Việt |
| `Mặc định=` | Cuối comment | Viết hoa M, có dấu bằng |

**Dấu phân cách:** trong `tra(...)` dùng `;` giữa các thành phần — các phần lớn của comment ngăn bằng `. ` (chấm + khoảng trắng) — trong ngoặc đơn mô tả, nhiều thông tin cách nhau `,`
