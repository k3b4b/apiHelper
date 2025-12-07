from src.db.database import engine
from src.db.models import Base
from src.core.logger import logger

# создание базы
def init_db():
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")