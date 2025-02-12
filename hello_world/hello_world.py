from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from datetime import datetime

from pprint import pprint


def main():
    client = MongoClient()
    db: Database = client.rewagg
    games: Collection = db.games
    inserted = games.insert_one(
        {
            "name": "Hollow Knight",
            "developer": "Team Cherry",
            "publisher": "Team Cherry",
            "genres": ["Metroidvania"],
            "summary": "Hollow Knight is a 2D action-adventure game with an emphasis on traditional 2D animation and skillful gameplay. Journey to Hallownest, a vast and ancient underground kingdom inhabited by a bizarre collection of insects and monsters. Players will forge their own path as they explore ruined cities, forests of fungus, temples of bone and other fantastic lands, all on their way to uncovering an ancient mystery.",
            "release_date": datetime(2018, 6, 12),
            "platforms": ["PC", "Wii U", "Nintendo Switch", "PS4", "XBOX One"],
            "esrb_rating": "E10+",
        }
    )
    print(inserted, f"{type(inserted)}")
    retrieved = games.find_one()
    pprint(retrieved)


if __name__ == '__main__':
    main()
