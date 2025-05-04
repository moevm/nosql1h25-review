from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from django.conf import settings

client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_NAME]

from django.http import HttpResponseForbidden

@login_required
def add_review(request, game_id):
    if request.method == 'POST':
        user = request.user
        game = db.games.find_one({'_id': ObjectId(game_id)})
       
        if not game:
            return render(request, '404.html', status=404)

        text = request.POST.get('text')
        rating = int(request.POST.get('rating'))
        platform = request.POST.get('platform')

        existing_review = db.user_reviews.find_one({
            'gameId': ObjectId(game_id),
            'userId': ObjectId(user.id),
            'platform': platform
        })

        if existing_review:
            return HttpResponseForbidden('You have already reviewed this game on this platform.')

        review = {
            'gameId': ObjectId(game_id),
            'userId': ObjectId(user.id),
            'gameTitle': game.get('title'),
            'text': text,
            'rating': rating,
            'platform': platform,
            'createdAt': datetime.utcnow(),
            'lastModified': datetime.utcnow()
        }
        db.user_reviews.insert_one(review)
        return redirect('games:game_detail', pk=game_id)

    return redirect('games:game_detail', pk=game_id)



@login_required
def edit_review(request, review_id):
    try:
        review = db.user_reviews.find_one({'_id': ObjectId(review_id)})
        
        if not review:
            return render(request, '404.html', status=404)
        
        if review['userId'] != ObjectId(request.user.id):
            return HttpResponseForbidden('У вас нет прав для редактирования этого отзыва.')
        
        game = db.games.find_one({'_id': review['gameId']})
        
        if request.method == 'POST':
            text = request.POST.get('text')
            rating = int(request.POST.get('rating'))
            platform = request.POST.get('platform')
            
            db.user_reviews.update_one(
                {'_id': ObjectId(review_id)},
                {
                    '$set': {
                        'text': text,
                        'rating': rating,
                        'platform': platform,
                        'lastModified': datetime.utcnow()
                    }
                }
            )
            
            messages.success(request, 'Отзыв успешно обновлен.')
            return redirect('profile:my_rating_and_reviews')
        user_reviews = db.user_reviews.find({
            'gameId': review['gameId'],
            'userId': ObjectId(request.user.id),
            '_id': {'$ne': ObjectId(review_id)}
        })
        used_platforms = {r['platform'] for r in user_reviews}

        all_platforms = game.get('platforms', [])
        available_platforms = [p for p in all_platforms if p not in used_platforms or p == review['platform']]

        return render(request, 'reviews/edit_review.html', {
            'review': review,
            'game': game,
            'available_platforms': available_platforms,
            'rating_choices': range(1, 11),
        })
        
    except Exception as e:
        messages.error(request, f'Произошла ошибка при редактировании отзыва: {str(e)}')
        return redirect('profile:my_rating_and_reviews')


@login_required
def delete_review(request, review_id):
    try:
        review = db.user_reviews.find_one({'_id': ObjectId(review_id)})
        
        if not review:
            return render(request, '404.html', status=404)
        
        if review['userId'] != ObjectId(request.user.id):
            return HttpResponseForbidden('У вас нет прав для удаления этого отзыва.')
        
        if request.method == 'POST':
            db.user_reviews.delete_one({'_id': ObjectId(review_id)})
            messages.success(request, 'Отзыв успешно удален.')
            return redirect('profile:my_rating_and_reviews')
            
        game_info = db.games.find_one({'_id': review['gameId']})
        return render(request, 'reviews/confirm_delete.html', {
            'review': review,
            'game': game_info
        })
        
    except Exception as e:
        messages.error(request, f'Произошла ошибка при удалении отзыва: {str(e)}')
        return redirect('profile:my_rating_and_reviews')
    

def review_list(request):
    return HttpResponse("Заглушка")
