from .mongo_exporter import MongoExporter
from .mongo_importer import MongoImporter


class MongoIOManager:
    """
    Facade for MongoDB data export and import operations.
    """

    def __init__(self, db_name: str, backup_dir: str, host: str = "localhost", port: int = 27017):
        self.exporter = MongoExporter(db_name, backup_dir, host, port)
        self.importer = MongoImporter(db_name, host, port)

    def export_data(self):
        """
        Export data from the MongoDB database to the backup directory.
        :return: None
        """
        self.exporter.export_data()

    def import_data(self, *, drop: bool = False):
        """
        Import data from the backup directory into the MongoDB database.
        :param drop: If True, drop the existing database before importing.
        :return: None
        """
        self.importer.import_data(self.exporter.backup_dir / self.exporter.db_name, drop)
