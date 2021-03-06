import warnings

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy import create_engine
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tools.local_utils import get_settings

warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning, r'^sqlalchemy\.sql\.sqltypes$')

Base = declarative_base()


class Post(Base):
    __tablename__ = 'wp_posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(200), unique=True, nullable=False, name='post_name')
    title = Column(String(200), nullable=False, name='post_title')
    content = Column(Text, nullable=False, name='post_content')
    date = Column(DateTime, nullable=False, name='post_date')
    date_gmt = Column(DateTime, nullable=False, name='post_date_gmt')
    modified = Column(DateTime, nullable=False, name='post_modified')
    modified_gmt = Column(DateTime, nullable=False, name='post_modified_gmt')
    post_type = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False, name='post_password')
    status = Column(String(20), nullable=False, name='post_status')
    comment_count = Column(Integer, nullable=False)


# Engine is called each time db_model is imported
settings = get_settings()
engine = create_engine(settings['config']['db_url'])
Base.metadata.create_all(engine)


def get_db_session():
    return sessionmaker(bind=engine, autoflush=False)()
