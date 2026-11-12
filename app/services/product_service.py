import os
from decimal import Decimal
from typing import Optional, Dict, Any

import httpx
from fastapi import HTTPException, status

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")


async def get_product_and_check_stock(
    product_id: int,
    required_quantity: int,
    token: Optional[str] = None
) -> Dict[str, Any]:
    # Gui request sang Product Service (port 8001) kiem tra thong tin va ton kho
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{PRODUCT_SERVICE_URL}/products/{product_id}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Khong the ket noi den Product Service o {PRODUCT_SERVICE_URL}: {str(exc)}"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay san pham co id = {product_id}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Loi tu Product Service: {response.text}"
        )

    product_data = response.json()
    available_quantity = int(product_data.get("quantity", 0))

    # Kiem tra so luong ton kho
    if available_quantity < required_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"San pham '{product_data.get('name')}' (id={product_id}) khong du so luong trong kho "
                f"(con {available_quantity}, yeu cau {required_quantity})"
            )
        )

    return product_data


async def deduct_product_stock(
    product_id: int,
    deduct_quantity: int,
    token: Optional[str] = None
) -> bool:
    # Cap nhat tru so luong ton kho sau khi dat hang thanh cong
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{PRODUCT_SERVICE_URL}/products/{product_id}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            get_resp = await client.get(url, headers=headers)
            if get_resp.status_code == 200:
                current_qty = int(get_resp.json().get("quantity", 0))
                new_qty = max(0, current_qty - deduct_quantity)
                await client.put(url, json={"quantity": new_qty}, headers=headers)
                return True
    except Exception:
        pass
    return False
