import os
from fastapi import FastAPI
from authx import AuthXConfig, AuthX
from authx.exceptions import MissingTokenError

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "access_token_cold"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False

token_security = AuthX(config=config)


