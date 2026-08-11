import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Leer la URL configurada para el túnel de Fly.io
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Configurar la fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Dependencia para inyectar la sesión en los endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session