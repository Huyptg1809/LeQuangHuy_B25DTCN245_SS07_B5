from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# - Bảo mật dữ liệu: Tạo `PromoPublic` chỉ chứa trường an toàn. Gắn vào `response_model` để FastAPI tự động loại bỏ `max_budget` và `is_active` trước khi trả về.
# - Chuẩn hóa Exception: Dùng `@app.exception_handler` bọc HTTPException để tự động sinh JSON 6 trường (statusCode, data, error, message, timestamp, path).
# - Logic "Sai thì raise": Kiểm tra mã không tồn tại (404) -> Kiểm tra mã hết hạn (400) -> Thỏa mãn hết thì return (200).

promo_codes_db = {
    "SUMMER25": {"code": "SUMMER25", "discount_rate": 0.15, "max_budget": 50000000, "is_active": True},
    "WELCOME50": {"code": "WELCOME50", "discount_rate": 0.50, "max_budget": 10000000, "is_active": False}
}

class PromoInternal(BaseModel):
    code: str
    discount_rate: float
    max_budget: int
    is_active: bool

class PromoPublic(BaseModel):
    code: str
    discount_rate: float

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "data": None,
            "error": "Business Error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": request.url.path
        }
    )

@app.get("/promos/{code}", response_model=PromoPublic, status_code=status.HTTP_200_OK)
def get_promo(code: str):
    promo = promo_codes_db.get(code)
    
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mã giảm giá không tồn tại"
        )
        
    if not promo["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã giảm giá đã hết hạn sử dụng"
        )
        
    return promo