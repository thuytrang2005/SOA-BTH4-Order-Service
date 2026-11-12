from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers.order_controller import OrderController
from app.schemas import OrderCreate, OrderResponse, OrderUpdate, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    """GET /orders - Lấy danh sách tất cả các đơn hàng"""
    return OrderController.get_all_orders(db)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """GET /orders/id - Lấy thông tin chi tiết một đơn hàng"""
    return OrderController.get_order_by_id(db, order_id)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """POST /orders - Tạo đơn hàng mới (kiểm tra tồn kho)"""
    token = getattr(request.state, "token", None)
    return await OrderController.create_order(db, order_data, token=token)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
):
    """PUT /orders/{id} - Cập nhật trạng thái đơn hàng"""
    return OrderController.update_order(db, order_id, order_data)


@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """DELETE /orders/id - Xóa một đơn hàng"""
    return OrderController.delete_order(db, order_id)
