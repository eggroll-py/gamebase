from sentence_transformers import SentenceTransformer
from games.models import Review, CollectionEntry, Game
from .choices import GameType
import numpy as np
from decimal import Decimal
from pgvector.django import CosineDistance
from django.db.models import Q
from sklearn.cluster import KMeans

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def compute_embedding(text: str) -> list[float]:
    model = get_model()
    vector = model.encode(text)
    return vector.tolist()

def build_embedding(game) -> str:
    parts = [game.summary or '']
    if game.genres.exists():
        parts.append('Genres: ' + ', '.join(g.name for g in game.genres.all()))
    if game.themes.exists():
        parts.append('Themes: ' + ', '.join(t.name for t in game.themes.all()))
    return ' '.join(p for p in parts if p)

def test_embedding() -> str:
    dark_souls = Game.objects.get(title='Dark Souls')
    hades2 = Game.objects.get(id=3)
    print('Full concat distance:', Game.objects.filter(id=hades2.id).annotate(d=CosineDistance('embedding', dark_souls.embedding)).values_list('d', flat=True).first())

    hades2_summary_only = compute_embedding(hades2.summary)
    dark_souls_summary_only = compute_embedding(dark_souls.summary)

    def cosine_sim(a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    print("Summary-only similarity:", cosine_sim(hades2_summary_only, dark_souls_summary_only))





def get_user_taste_vector(user):
    weighted_vectors = []
    total_weight = 0
    completed_ids = set(CollectionEntry.objects.filter(user=user, status='completed').values_list('game_id', flat=True))

    for review in Review.objects.filter(user=user, rating__gte=6).select_related('game'):
        if review.game.embedding is not None:
            weight = review.rating
            if review.game.id in completed_ids:
                weight += 2
            weighted_vectors.append(np.array(review.game.embedding) * weight)
            total_weight += weight

    for entry in CollectionEntry.objects.filter(user=user, status='completed').select_related('game'):
        if entry.game.embedding is not None:
            weight = 5
            weighted_vectors.append(np.array(entry.game.embedding) * weight)
            total_weight += weight

    if not weighted_vectors:
        return None

    return (sum(weighted_vectors) / total_weight).tolist()

def get_user_taste_clusters(user, k=2):
    weighted_data = []

    for review in Review.objects.filter(user=user, rating__gte=6).select_related('game'):
        if review.game.embedding is not None:
            weight = review.rating
            if CollectionEntry.objects.filter(user=user, game=review.game, status='completed').exists():
                weight += 2
            weighted_data.append((np.array(review.game.embedding), weight))

    reviewed_ids = {r.game.id for r in Review.objects.filter(user=user, rating__gte=6)}
    for entry in CollectionEntry.objects.filter(user=user, status='completed').exclude(game_id__in=reviewed_ids).select_related('game'):
        if entry.game.embedding is not None:
            weighted_data.append((np.array(entry.game.embedding), 5))

    if len(weighted_data) < 2:
        return None

    vectors = np.array([v for v, w in weighted_data])
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(vectors)

    cluster_vectors = []
    for cluster_id in range(k):
        cluster_items = [(v, w) for (v, w), label in zip(weighted_data, labels) if label == cluster_id]
        if not cluster_items:
            continue
        total_weight = sum(w for v, w in cluster_items)
        weighted_sum = sum(v * w for v, w in cluster_items)
        cluster_vectors.append((weighted_sum / total_weight).tolist())

    return cluster_vectors

def get_family_id(game):
    return (
        game.parent_game_id if game.parent_game_id is not None else game.id
    )

def dedupe_by_family(game_qs):
    best_in_family = {}
    for game in game_qs:
        key = get_family_id(game)
        if key not in best_in_family or game.distance < best_in_family[key].distance:
            best_in_family[key] = game

    result = list(best_in_family.values())
    result.sort(key=lambda g:g.distance)
    return result


def get_reccs_from_vector(taste_vector, exclude_ids, max_distance=0.5):
    if taste_vector is None:
        return []

    candidates = (Game.objects
    .exclude(id__in=exclude_ids)
    .exclude(embedding__isnull=True)
    .exclude(game_type=GameType.BUNDLE)
    .annotate(distance=CosineDistance('embedding', taste_vector))
    .filter(distance__lte=max_distance))

    return dedupe_by_family(candidates)

def get_avg_recommendations(user, max_distance=0.5):
    taste_vector = get_user_taste_vector(user)
    if taste_vector is None:
        return []

    owned_ids = CollectionEntry.objects.filter(user=user).values_list('game_id', flat=True)

    return get_reccs_from_vector(taste_vector, owned_ids, max_distance)


def get_clustered_recommendations(user, k=2, max_distance=0.5):
    clusters = get_user_taste_clusters(user=user, k=k)
    if clusters is None:
        return []

    owned_ids = CollectionEntry.objects.filter(user=user).values_list('game_id', flat=True)

    best_by_family = {}

    for cluster_index, cluster_vector in enumerate(clusters):
        recs = get_reccs_from_vector(cluster_vector, owned_ids, max_distance)

        for rec in recs:
            family_id = get_family_id(rec)
            current_best = best_by_family.get(family_id)
            if current_best is None or rec.distance < current_best[0].distance:
                best_by_family[family_id] = rec, cluster_index

            results = [[] for _ in clusters]
            for rec, cluster_index in best_by_family.values():
                results[cluster_index].append(rec)

            for cluster_recs in results:
                cluster_recs.sort(key=lambda game:game.distance)

            return results



    return results

def get_mixed_reccs(user):
    avg = get_avg_recommendations(user)
    clusters = get_clustered_recommendations(user)
    sources = [avg, *clusters]

    active_sources = [iter(source) for source in sources]

    seen_family_ids = set()
    final_recs = []

    while active_sources:
        next_round = []
        for source_iterator in active_sources:
            for game in source_iterator:
                family_id = get_family_id(game)
                if family_id in seen_family_ids:
                    continue

                seen_family_ids.add(family_id)
                final_recs.append(game)
                next_round.append(source_iterator)
                break
        active_sources = next_round

    return final_recs

def get_similar_games(game, max_distance=0.5):
    if game.embedding is None:
        return []

    reccs = get_reccs_from_vector(game.embedding, exclude_ids=[game.id], max_distance=max_distance)

    return list(reccs)


