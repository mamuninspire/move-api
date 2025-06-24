import os
from dotenv import load_dotenv

ENV = os.getenv("ENV")
print(f"ENV: {ENV}")

if ENV == "prod":
    from .prod import *
elif ENV == "dev":
    from .dev import *
else:
    from .local import *