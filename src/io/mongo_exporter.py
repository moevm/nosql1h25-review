import subprocess
from pathlib import Path


class MongoExporter:
    """
    Class to handle exporting data from a MongoDB database to a backup directory.

    Wrapper for the `mongodump` command.
    """

    def __init__(self, db_name: str, backup_dir: str, host: str = "localhost", port: int = 27017):
        """
        Initialize the MongoExporter with database name, backup directory, host and port.
        :param db_name: database name to export data from
        :param backup_dir: path to the backup directory
        :param host: host of the MongoDB server
        :param port: port of the MongoDB server
        """
        self.db_name = db_name
        self.backup_dir = Path(backup_dir)
        self.host = host
        self.port = port

    def export_data(self):
        """
        Export data from the MongoDB database to the backup directory.
        :return:
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "mongodump",
            "--host", self.host,
            "--port", str(self.port),
            "--db", self.db_name,
            "--out", str(self.backup_dir)
        ], check=True)
