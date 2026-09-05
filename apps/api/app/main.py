from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.audit_logs.infra.http.router import router as audit_logs_router
from app.modules.orders.infra.http.exception_handlers import (
    register_order_exception_handlers,
)
from app.modules.orders.infra.http.router import router as orders_router
from app.modules.products.infra.http.exception_handlers import (
    register_product_exception_handlers,
)
from app.modules.products.infra.http.router import router as products_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(audit_logs_router)
register_product_exception_handlers(app)
register_order_exception_handlers(app)


@app.get("/consume-status")
def get_consume_status() -> dict[str, str]:
    return {"message": "Consume status endpoint is working!"}
