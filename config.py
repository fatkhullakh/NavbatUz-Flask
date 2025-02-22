import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "e600375948b530326802ac7271b5afe0f16819955f0118f8d827a4d6137eaa01"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:Fatkh7267(?)@localhost/navbatuz_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
