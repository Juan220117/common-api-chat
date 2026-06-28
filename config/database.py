import os
from sqlalchemy import create_engine, NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#1.- Obtener URL de la base de datos (debe apuntar a RDS Proxy).
#DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@rds-proxy-endpoint:3306/mydb')
#Test (Estos valores estaran almacenados en un secreto par mayor seguridad)
USER =os.getenv("USER")
PWSD =os.getenv("PWSD")
HOST =os.getenv("HOST")
PORT =os.getenv("PORT")
DB =os.getenv("DB")

DATABASE_URL = f"mysql+mysqldb://{USER}:{PWSD}@{HOST}:{PORT}/{DB}?charset=utf8"

# Crear el engine con NullPool
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_recycle=300
)

# Crear una fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos SQLAlchemy
Base = declarative_base()

def init_db():
    """Crear todas las tablas si no existen (útil para desarrollo)"""
    Base.metadata.create_all(bind=engine)
