from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemCreateInOrder(OrderItemBase):
    unit_price: Optional[Decimal] = Field(None, ge=0)
    product_name: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    order_id: int
    unit_price: Optional[Decimal] = Field(None, ge=0)
    product_name: Optional[str] = None


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: str = Field(..., min_length=1, max_length=255)


class OrderCreate(OrderBase):
    items: Optional[List[OrderItemCreateInOrder]] = []


class OrderStatusUpdate(BaseModel):
    status: str


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    customer_email: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
