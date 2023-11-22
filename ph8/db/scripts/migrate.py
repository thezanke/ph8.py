from ph8.db import engine, models


def migrate():
    models.Base.metadata.create_all(engine)


if __name__ == "__main__":
    migrate()
