import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./shorter.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

links = sqlalchemy.Table(
    "links",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("url", sqlalchemy.String),
    sqlalchemy.Column("short", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)
