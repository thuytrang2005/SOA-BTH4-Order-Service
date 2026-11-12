from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.jwt import verify_token


# Những đường dẫn được phép truy cập KHÔNG cần token
PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class JwtMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        # Bỏ qua các path công khai và tài nguyên docs
        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Các path còn lại đều cần JWT
        authorization = request.headers.get("Authorization")

        if authorization is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Không có token"}
            )

        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization phải có dạng Bearer <token>"}
            )

        token = authorization.split(" ", 1)[1]
        payload = verify_token(token)

        if payload is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token không hợp lệ hoặc đã hết hạn"}
            )

        # Lưu username va token vao request
        request.state.user = payload.get("sub")
        request.state.token = token

        return await call_next(request)
