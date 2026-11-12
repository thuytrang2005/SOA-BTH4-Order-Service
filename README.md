# BTH4 - Order Management Service

Bài thực hành 4 môn SOA - Dịch vụ quản lý đơn hàng (FastAPI).

## Kiến trúc

- Order Service (BTH4): port 8002, DB orders.db
- Product Service (BTH3): port 8001, DB products.db
- Auth Service (BTH2): port 8000, DB users.db
- Xác thực qua JWT dùng chung SECRET_KEY từ Auth Service (TH2)
- Kiểm tra tồn kho sản phẩm từ Product Service (TH3)

## Danh sách API

### Đơn hàng (Orders)
- `GET /orders`: Lấy danh sách tất cả các đơn hàng
- `GET /orders/{id}`: Lấy thông tin chi tiết một đơn hàng
- `POST /orders`: Tạo đơn hàng mới (kiểm tra tồn kho)
- `PUT /orders/{id}`: Cập nhật trạng thái đơn hàng
- `DELETE /orders/{id}`: Xóa một đơn hàng

### Chi tiết đơn hàng (Order Items)
- `GET /order_items`: Lấy danh sách tất cả mặt hàng trong đơn hàng
- `GET /order_items/{id}`: Lấy thông tin chi tiết một mặt hàng
- `POST /order_items`: Tạo mặt hàng mới (kiểm tra tồn kho)
- `PUT /order_items/{id}`: Cập nhật mặt hàng
- `DELETE /order_items/{id}`: Xóa một mặt hàng trong đơn hàng

## Cài đặt và chạy

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8002 --reload
```
