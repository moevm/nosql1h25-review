from src.io import MongoImporter


def main():
    mongo_io_manager = MongoImporter("rotten_scores")
    mongo_io_manager.import_data("backup/rotten_scores", drop=True)


if __name__ == '__main__':
    main()
