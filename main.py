from src.io.mongo_io_manager import MongoIOManager

def main():
    io_manager = MongoIOManager("rewagg", "backup")
    io_manager.import_data(drop=True)


if __name__ == '__main__':
    main()