import os
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# Afficher les variables
print("=" * 60)
print("VARIABLES D'ENVIRONNEMENT CHARGÉES :")
print("=" * 60)
print(f"DB_HOST      : {os.getenv('DB_HOST')}")
print(f"DB_PORT      : {os.getenv('DB_PORT')}")
print(f"DB_NAME      : {os.getenv('DB_NAME')}")
print(f"DB_USER      : {os.getenv('DB_USER')}")
print(f"DB_PASSWORD  : {os.getenv('DB_PASSWORD')}")
print(f"DATABASE_URL : {os.getenv('DATABASE_URL')}")
print("=" * 60)