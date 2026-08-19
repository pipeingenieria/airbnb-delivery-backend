from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos los dos routers que tenemos hasta ahora
from app.routers import core, catalogo , partner

app = FastAPI(
    title="Airbnb Delivery API",
    description="Ecosistema Digital de Domicilios y Servicios para Airbnb",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acoplamos las rutas a la API
app.include_router(core.router)
app.include_router(catalogo.router)
app.include_router(partner.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "El ecosistema está en línea 🚀"}