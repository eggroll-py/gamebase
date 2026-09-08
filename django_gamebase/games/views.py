from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Game
from .igdb_import import search_and_import

@login_required
def game_list(request):
    query = request.GET.get('q', '').strip()

    if query:
        games = Game.objects.filter(title__icontains=query)
        if not games.exists():
            games = search_and_import(query)

    else:
        games = Game.objects.all()[:35]

    return render(request, 'games/game_list.html', {'games': games, 'query': query})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    prices = game.priceentry_set.all()
    return render(request, 'games/game_detail.html', {'game': game, 'prices': prices})




