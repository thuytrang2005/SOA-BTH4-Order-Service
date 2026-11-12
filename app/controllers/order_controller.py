from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order, OrderItem
from app.schemas import OrderCreate, OrderUpdate, OrderStatusUpdate
from app.services.product_service import get_product_and_check_stock, deduct_product_stock

VALID_STATUSES = {"pending", "completed", "cancelled"}


class OrderController:
    @staticmethod
    def get_all_orders(db: Session) -> List[Order]:
        return db.query(Order).order_by(Order.id.desc()).all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Khong tim thay don hang co id = {order_id}"
            )
        return order

    @staticmethod
    async def create_order(
        db: Session,
        order_data: OrderCreate,
        token: Optional[str] = None,
        auto_deduct_stock: bool = False
    ) -> Order:
        # Tao record don hang moi
        new_order = Order(
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            total_amount=Decimal("0.00"),
            status="pending"
        )
        db.add(new_order)
        db.flush()

        total_amount = Decimal("0.00")
        items_to_deduct = []

        if order_data.items:
            for item in order_data.items:
                # Kiem tra san pham va ton kho ben Product Service
                product_info = await get_product_and_check_stock(
                    product_id=item.product_id,
                    required_quantity=item.quantity,
                    token=token
                )

                product_name = item.product_name or product_info.get("name", f"Product #{item.product_id}")
                unit_price = item.unit_price if item.unit_price is not None else Decimal(str(product_info.get("price", "0")))
                item_total_price = unit_price * item.quantity

                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item.product_id,
                    product_name=product_name,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    total_price=item_total_price
                )
                db.add(order_item)
                total_amount += item_total_price
                items_to_deduct.append((item.product_id, item.quantity))

        new_order.total_amount = total_amount
        db.commit()
        db.refresh(new_order)

        # Tru ton kho neu can
        if auto_deduct_stock and items_to_deduct:
            for prod_id, qty in items_to_deduct:
                await deduct_product_stock(prod_id, qty, token=token)

        return new_order

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        status_data: OrderStatusUpdate
    ) -> Order:
        order = OrderController.get_order_by_id(db, order_id)

        target_status = status_data.status.lower()
        if target_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trang thai khong hop le, chi nhan: {', '.join(VALID_STATUSES)}"
            )

        order.status = target_status
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_order(
        db: Session,
        order_id: int,
        order_data: OrderUpdate
    ) -> Order:
        order = OrderController.get_order_by_id(db, order_id)

        update_dict = order_data.model_dump(exclude_unset=True)
        if "status" in update_dict and update_dict["status"]:
            target_status = update_dict["status"].lower()
            if target_status not in VALID_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Trang thai khong hop le, chi nhan: {', '.join(VALID_STATUSES)}"
                )
            order.status = target_status

        if "customer_name" in update_dict and update_dict["customer_name"]:
            order.customer_name = update_dict["customer_name"]

        if "customer_email" in update_dict and update_dict["customer_email"]:
            order.customer_email = update_dict["customer_email"]

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def delete_order(db: Session, order_id: int) -> dict:
        order = OrderController.get_order_by_id(db, order_id)
        db.delete(order)
        db.commit()
        return {"message": f"Da xoa don hang id = {order_id}"}
