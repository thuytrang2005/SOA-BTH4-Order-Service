from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers.order_item_controller import OrderItemController
from app.schemas import OrderItemCreate, OrderItemResponse, OrderItemUpdate

router = APIRouter(prefix="/order_items", tags=["Order Items"])


@router.get("", response_model=List[OrderItemResponse])
def get_order_items(
    order_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """GET /order_items - Lấy danh sách tất cả mặt hàng trong đơn hàng"""
    return OrderItemController.get_all_order_items(db, order_id=order_id)


@router.get("/{item_id}", response_model=OrderItemResponse)
def get_order_item(item_id: int, db: Session = Depends(get_db)):
    """GET /order_items/{id} - Lấy thông tin chi tiết một mặt hàng"""
    return OrderItemController.get_order_item_by_id(db, item_id)


@router.post(
    "",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order_item(
    item_data: OrderItemCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """POST /order_items - Tạo mặt hàng mới (kiểm tra tồn kho)"""
    token = getattr(request.state, "token", None)
    return await OrderItemController.create_order_item(db, item_data, token=token)


@router.put("/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: int,
    item_data: OrderItemUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """PUT /order_items/{id} - Cập nhật mặt hàng"""
    token = getattr(request.state, "token", None)
    return await OrderItemController.update_order_item(db, item_id, item_data, token=token)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_order_item(item_id: int, db: Session = Depends(get_db)):
    """DELETE /order_items/{id} - Xóa một mặt hàng trong đơn hàng"""
    return OrderItemController.delete_order_item(db, item_id)
