from src.io import MongoImporter


def main():
    mongo_io_manager = MongoImporter("game_reviews_db")
    mongo_io_manager.import_data("backup/game_reviews_db", drop=True)


if __name__ == '__main__':
    main()
