from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), 'info.env')
load_dotenv(dotenv_path=dotenv_path)
