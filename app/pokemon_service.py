from .db import get
from flask import abort
from werkzeug.exceptions import BadRequest
import functools
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Simple in-memory cache for demonstration purposes
_cache = {}

# In-memory storage for captured Pokemon, using (number, name) tuples
captured_pokemon = set()

def cache(func):
    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        cache_key = f"{args}-{kwargs}"
        if cache_key in _cache:
            return _cache[cache_key]
        result = func(*args, **kwargs)
        _cache[cache_key] = result
        return result
    return wrapper_cache

def get_image_url(name):
    return f"https://img.pokemondb.net/sprites/silver/normal/{name.lower()}.png"

@cache
def get_pokemon_list(page, page_size, sort, filter_type, search_query=None):
    try:
        data = get()
    except Exception as e:
        logger.error("Failed to read data from the database", exc_info=True)
        abort(500, description="Failed to read data from the database")

    if sort not in ['asc', 'desc']:
        logger.error(f"Invalid sort value: {sort}")
        raise BadRequest("Sort must be 'asc' or 'desc'")

    if filter_type:
        data = [pokemon for pokemon in data if filter_type in (pokemon['type_one'], pokemon['type_two'])]

    if search_query:
        search_query = search_query.lower()
        data = [pokemon for pokemon in data if any(search_query in str(value).lower() for value in pokemon.values())]

    reverse = sort == 'desc'
    data.sort(key=lambda x: x['number'], reverse=reverse)

    total_items = len(data)
    if page < 1 or page_size < 1:
        logger.error(f"Invalid pagination values: page={page}, page_size={page_size}")
        raise BadRequest("Page number and page size must be greater than 0")
    start = (page - 1) * page_size
    end = start + page_size
    paginated_data = data[start:end]

    for pokemon in paginated_data:
        pokemon['image_url'] = get_image_url(pokemon['name'])
        pokemon['captured'] = (pokemon['number'], pokemon['name']) in captured_pokemon

    return {
        'data': paginated_data,
        'total_items': total_items,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_items + page_size - 1) // page_size
    }

def capture_pokemon(number, name):
    capture_id = (number, name)
    captured_pokemon.add(capture_id)
    # Update cache directly
    for key, value in _cache.items():
        for pokemon in value['data']:
            if pokemon['number'] == number and pokemon['name'] == name:
                pokemon['captured'] = True
    logger.info(f"Pokemon captured: number={number}, name={name}")
    return {'status': 'success', 'capture_id': capture_id}
