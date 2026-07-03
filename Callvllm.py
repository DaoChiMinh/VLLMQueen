from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM local không kiểm tra key, nhưng thư viện bắt buộc có
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-4B-AWQ",   # phải khớp đúng tên model đang serve
    messages=[
        {"role": "system", "content": "/no_think Bạn là chuyên gia SQL Server. Chỉ trả về câu SQL, không giải thích."},
        {"role": "user", "content": "tổng tiến của các đơn hàng từ ngày đầu tháng đến ngày hôm nay từ bảng DonHang(ID, NgayTao, TrangThai, TongTien)"}
    ],
    temperature=0.1,
    max_tokens=512,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}}
)

print(response.choices[0].message.content)