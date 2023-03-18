import os
import json
import configparser

file = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASE_URL = f"sqlite:///{os.path.join(file, 'database.db')}"

# with open(os.path.join(PROJECT_DIR, 'database_secrets.json'), 'r') as f:
#     database_secrets = json.load(f)

# DATABASE_URL = f"postgres://{database_secrets['username']}:{database_secrets['password']}@localhost:5432/autoGenerations";

#c = configparser.ConfigParser()
#c.read(os.path.join(os.path.dirname(file), 'credentials.ini'))
#DATABASE_URL = f"postgresql://{c['database']['USER']}:{c['database']['PASSWORD']}@localhost:5432/github_metrics"