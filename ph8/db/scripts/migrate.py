if __name__ == "__main__":
    from ph8.db import engine, models

    models.Base.metadata.create_all(engine)
