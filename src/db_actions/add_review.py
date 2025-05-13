from typing import Literal, TypeVar

from src.schemas import Game, UserReview, CriticReview, Stats, StatsReviews

from pymongo.database import Database
from pymongo.collection import Collection

T = TypeVar('T', UserReview, CriticReview)


def add_user_review(db: Database, review: UserReview) -> None:
    _add_review(db, review, 'user_reviews', 'user')


def add_critic_review(db: Database, review: CriticReview) -> None:
    _add_review(db, review, 'critic_reviews', 'critic')


def _add_review(db: Database, review: T, collection_name: str,
                review_type: Literal['user', 'critic'], ) -> None:
    reviews_collection: Collection[T] = db[collection_name]
    reviews_collection.insert_one(review)

    game = db['games'].find_one({'_id': review['gameId']})
    if game is None:
        raise ValueError(f"Game with ID {review['gameId']} not found in the database.")

    _update_game_stats_and_recent_reviews(db, game, review, review_type=review_type)


def _update_game_stats_and_recent_reviews(db: Database, game: Game, review: T,
                                          review_type: Literal['user', 'critic']) -> None:
    _update_game_stats(db, game, review['rating'], review_type)
    _update_game_recent_reviews(db, game, review, review_type)


def _update_game_stats(db: Database, game: Game, rating: int,
                       review_type: Literal['user', 'critic']) -> None:
    stats = _get_game_stats(game, review_type)
    stats['total'] += 1
    stats['avgRating'] = (stats['avgRating'] * (stats['total'] - 1) + rating) / stats['total']
    if review_type == 'critic':
        stats['avgRating'] = round(stats['avgRating'])
    else:
        stats['avgRating'] = round(stats['avgRating'], 1)

    db['games'].update_one({'_id': game['_id']},
                           {'$set': {f'stats.{review_type}Reviews': stats}})


def _get_game_stats(game: Game,
                    review_type: Literal['user', 'critic']) -> StatsReviews:
    if game.get('stats') is None:
        game['stats'] = Stats(
            userReviews=StatsReviews(total=0, avgRating=0),
            criticReviews=StatsReviews(total=0, avgRating=0)
        )
    if review_type == 'user':
        return game['stats'].get('userReviews', StatsReviews(total=0, avgRating=0))
    else:
        return game['stats'].get('criticReviews', StatsReviews(total=0, avgRating=0))


def _update_game_recent_reviews(db: Database, game: Game, review: T,
                                review_type: Literal['user', 'critic']) -> None:
    if review_type == 'user':
        recent_reviews = game.get('recentUserReviews', [])
    else:
        recent_reviews = game.get('recentCriticReviews', [])

    recent_reviews.append(review)
    if len(recent_reviews) > 3:
        recent_reviews.pop(0)

    db['games'].update_one({'_id': game['_id']},
                           {'$set': {f'recent{review_type.capitalize()}Reviews': recent_reviews}})
