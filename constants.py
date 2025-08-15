import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('TGR_CHAT_ID')
