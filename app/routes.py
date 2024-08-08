from flask import Blueprint, request, jsonify
from .pokemon_service import get_pokemon_list, capture_pokemon
from werkzeug.exceptions import BadRequest

# Create a Blueprint
main = Blueprint('main', __name__)

@main.route('/api/pokemon', methods=['GET'])
# @limiter.limit("5 per minute") # I would Add rate limit here at (using limitter library) on production
def get_pokemon():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        sort = request.args.get('sort', 'asc')
        filter_type = request.args.get('type')
        search_query = request.args.get('search_query')
        
        if page < 1 or page_size < 1:
            raise BadRequest("Page number and page size must be greater than 0")
        
        if sort not in ['asc', 'desc']:
            raise BadRequest("Sort must be 'asc' or 'desc'")
        
    except ValueError:
        return jsonify({"error": "Invalid input parameters"}), 400
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

    pokemons = get_pokemon_list(page, page_size, sort, filter_type, search_query)
    return jsonify(pokemons)

@main.route('/api/pokemon/capture', methods=['POST'])
def capture_pokemon_route():
    try:
        data = request.get_json()
        number = data.get('number')
        name = data.get('name')
        
        if not number or not name:
            raise BadRequest("Pokemon number and name are required")
        
        result = capture_pokemon(number, name)
        return jsonify(result)
    
    except ValueError:
        return jsonify({"error": "Invalid input parameters"}), 400
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
