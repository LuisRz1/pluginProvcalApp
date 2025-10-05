# Sistema de Catering - Backend

Sistema de gestión de catering empresarial con arquitectura de puertos y adaptadores.

## Stack Tecnológico

- Python 3.11
- FastAPI
- Strawberry GraphQL
- PostgreSQL
- SQLAlchemy (async)
- Alembic

## Instalación
```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/catering-backend.git
cd catering-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload