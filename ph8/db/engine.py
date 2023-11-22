from sqlalchemy import create_engine
import ph8.config

engine = create_engine(ph8.config.db.url)
