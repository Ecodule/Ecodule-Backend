import os
from dotenv import load_dotenv
load_dotenv()

EMAIL_VERIFICATION_SECRET_KEY = os.getenv("EMAIL_VERIFICATION_SECRET_KEY")