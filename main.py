from src.io.mongo_io_manager import MongoIOManager


def main():
    mongo_io_manager = MongoIOManager("rotten_scores", "backup")
    mongo_io_manager.import_data()


if __name__ == '__main__':
    main()
