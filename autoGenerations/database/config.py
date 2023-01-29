import os
import configparser

file = os.path.dirname(__file__)
DATABASE_URL = f"sqlite:///{os.path.join(file, 'database.db')}"

#c = configparser.ConfigParser()
#c.read(os.path.join(os.path.dirname(file), 'credentials.ini'))
#DATABASE_URL = f"postgresql://{c['database']['USER']}:{c['database']['PASSWORD']}@localhost:5432/github_metrics"