from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Airbnb Delivery API",
    description="Ecosistema Digital de Domicilios y Servicios para Airbnb",
    version="1.0.0"
)

# Configuración básica de CORS (luego la restringiremos a la URL de Angular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "El ecosistema está en línea 🚀"}
