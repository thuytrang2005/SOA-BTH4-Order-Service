from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order, OrderItem
from app.schemas import OrderItemCreate, OrderItemUpdate
from app.services.product_service import get_product_and_check_stock


def recalculate_order_total(db: Session, order_id: int):
    # Tinh lai tong tien don hang tu cac order_item
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    new_total = sum((item.total_price for item in items), Decimal("0.00"))

    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.total_amount = new_total
        db.commit()
        db.refresh(order)


class OrderItemController:
    @staticmethod
    def get_all_order_items(db: Session, order_id: Optional[int] = None) -> List[OrderItem]:
        query = db.query(OrderItem)
        if order_id is not None:
            query = query.filter(OrderItem.order_id == order_id)
        return query.order_by(OrderItem.id.asc()).all()

    @staticmethod
    def get_order_item_by_id(db: Session, item_id: int) -> OrderItem:
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Khong tim thay chi tiet don hang co id = {item_id}"
            )
        return item

    @staticmethod
    async def create_order_item(
        db: Session,
        item_data: OrderItemCreate,
        token: Optional[str] = None
    ) -> OrderItem:
        # Kiem tra don hang co ton tai khong
        order = db.query(Order).filter(Order.id == item_data.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Don hang id = {item_data.order_id} khong ton tai"
            )

        # Kiem tra san pham va ton kho ben Product Service
        product_info = await get_product_and_check_stock(
            product_id=item_data.product_id,
            required_quantity=item_data.quantity,
            token=token
        )

        product_name = item_data.product_name or product_info.get("name", f"Product #{item_data.product_id}")
        unit_price = item_data.unit_price if item_data.unit_price is not None else Decimal(str(product_info.get("price", "0")))
        total_price = unit_price * item_data.quantity

        new_item = OrderItem(
            order_id=item_data.order_id,
            product_id=item_data.product_id,
            product_name=product_name,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        # Tinh lai tong tien don hang
        recalculate_order_total(db, item_data.order_id)

        return new_item

    @staticmethod
    async def update_order_item(
        db: Session,
        item_id: int,
        item_data: OrderItemUpdate,
        token: Optional[str] = None
    ) -> OrderItem:
        item = OrderItemController.get_order_item_by_id(db, item_id)

        if item_data.quantity is not None and item_data.quantity != item.quantity:
            # Kiem tra ton kho voi so luong moi
            await get_product_and_check_stock(
                product_id=item.product_id,
                required_quantity=item_data.quantity,
                token=token
            )
            item.quantity = item_data.quantity
            item.total_price = item.unit_price * item_data.quantity

            db.commit()
            db.refresh(item)

            # Tinh lai tong tien
            recalculate_order_total(db, item.order_id)

        return item

    @staticmethod
    def delete_order_item(db: Session, item_id: int) -> dict:
        item = OrderItemController.get_order_item_by_id(db, item_id)
        order_id = item.order_id

        db.delete(item)
        db.commit()

        # Tinh lai tong tien
        recalculate_order_total(db, order_id)

        return {"message": f"Da xoa mat hang id = {item_id}"}
