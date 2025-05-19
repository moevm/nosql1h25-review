from src.io import MongoImporter, MongoExporter


def export_data():
    mongo_io_manager = MongoExporter("game_reviews_db", 'backup')
    mongo_io_manager.export_data()


def import_data():
    mongo_io_manager = MongoImporter("game_reviews_db")
    mongo_io_manager.import_data('backup/game_reviews_db', drop=True)


def main():
    import_data()


if __name__ == '__main__':
    main()
