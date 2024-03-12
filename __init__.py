from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), 'notes.env')
load_dotenv(dotenv_path=dotenv_path)
