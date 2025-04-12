import subprocess
from pathlib import Path


class MongoExporter:
    def __init__(self, db_name: str, backup_dir: str, host: str = "localhost", port: int = 27017):
        self.db_name = db_name
        self.backup_dir = Path(backup_dir)
        self.host = host
        self.port = port

    def export_data(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "mongodump",
            "--host", self.host,
            "--port", str(self.port),
            "--db", self.db_name,
            "--out", str(self.backup_dir)
        ], check=True)
