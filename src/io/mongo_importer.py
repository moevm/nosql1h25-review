import subprocess
from pathlib import Path


class MongoImporter:
    def __init__(self, db_name, host="localhost", port=27017):
        self.db_name = db_name
        self.host = host
        self.port = port

    def import_data(self, backup_path: str, drop: bool = False):
        self._validate_backup_path(backup_path)
        subprocess.run([
            "mongorestore",
            "--host", self.host,
            "--port", str(self.port),
            "--db", self.db_name,
            "--drop" if drop else "",
            str(backup_path)
        ], check=True)


    @staticmethod
    def _validate_backup_path(backup_path: str):
        backup = Path(backup_path)
        if not backup.exists():
            raise FileNotFoundError(f"Backup path {backup_path} does not exist.")

        if not backup.is_dir():
            raise ValueError(f"Backup path {backup_path} is not a directory.")

        if not any(f.suffix == ".bson" for f in backup.glob("*.bson")):
            raise ValueError(f"No BSON files found in backup path {backup_path}.")
