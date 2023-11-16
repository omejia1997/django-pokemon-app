from django.http import Http404
import requests
import threading
from urllib.parse import unquote
from django.shortcuts import render
from django.core.paginator import Paginator
from pokemonapp.models import Pokemon

data_load_pokemon = None
consult = ""

def pokemon_information(request):
    name_pokemon = request.GET.get('name_pokemon', '')
    data_pokemon = _get_data_pokemon(name_pokemon)
    return render(request, 'pokemon_information.html', {"pokemon_data": data_pokemon})
    
def search(request):
    global data_load_pokemon
    global consult
    threads = []

    if 'page' in request.GET:
        page = request.GET['page'] 
    else:
        page = 1
    result_filter = []
    
    if 'search' in request.GET:
        consult = request.GET['search']

    if(consult is ""):
        result_filter = data_load_pokemon
    else:
        result_filter  = list(filter(lambda x: consult.lower() in x.name, data_load_pokemon)) if data_load_pokemon is not None else []
    
    paginator = Paginator(result_filter,9)
    data_paginador = paginator.page(page)
        
    for pokemon in data_paginador.object_list:
        if pokemon.number_abilities is None:
            thread = threading.Thread(target=concurrent_task,args=(pokemon.name,None,))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()
    
    result_filter  = list(filter(lambda x: consult.lower() in x.name, data_load_pokemon)) if data_load_pokemon is not None else []
    
    paginator = Paginator(result_filter,9)
    data_paginador = paginator.page(page)
    return render(request, 'index.html', {"pokemons_data": data_paginador, "paginator": paginator, "consult":consult})   

def pokemons(request):
    global data_load_pokemon
    pokemon_list = []
    threads = []
    if 'page' in request.GET:
        page = request.GET['page'] 
    else:
        page = 1
    try:
        if data_load_pokemon is None:
            pokemons_data = _get_pokemons()
            for pokemon in pokemons_data["results"]:
                name_pokemon = pokemon.get("name")
                pokemon_instance = Pokemon(name=name_pokemon)
                pokemon_list.append(pokemon_instance)
            
            data_load_pokemon = pokemon_list
        paginator = Paginator(data_load_pokemon,9)
        data_paginador = paginator.page(page)
        start_array = 9 * (int(page) - 1)

        for i,pokemon in enumerate(data_paginador.object_list):
            iterator = i+start_array
            if pokemon.number_abilities is not None:
                break
            thread = threading.Thread(target=concurrent_task,args=(pokemon.name,iterator,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        paginator = Paginator(data_load_pokemon,9)
        data_paginador = paginator.page(page)
        
    except Exception as e:
        pokemons_data = {"error": str(e)}
        raise Http404

    return render(request, 'index.html', {"pokemons_data": data_paginador, "paginator": paginator})

def concurrent_task(pokemon_name,iterator):
    global data_load_pokemon
    data_pokemon = _get_data_pokemon(pokemon_name)
    number_abilities_pokemon = len(data_pokemon["abilities"])
    url_image_pokemon = data_pokemon["sprites"]["other"]["dream_world"]["front_default"]
    if url_image_pokemon is None:
        url_image_pokemon = data_pokemon["sprites"]["front_default"]
        if url_image_pokemon is None:
            url_image_pokemon = "https://vignette3.wikia.nocookie.net/clubpenguin/images/4/4c/Pokeball.png/revision/latest?cb=20130901024704"
    
    pokemon_instance = Pokemon(name=pokemon_name, url_image=url_image_pokemon, number_abilities=number_abilities_pokemon)
    if(iterator is not  None):
        data_load_pokemon[iterator] = pokemon_instance
    else:
        for i, pokemon in enumerate(data_load_pokemon):
            if pokemon.name == pokemon_name:
                data_load_pokemon[i] = pokemon_instance
                break

def _get_pokemons():
    endpoint_url = "https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0"
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status() 
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la solicitud: {str(e)}")
    
def _get_data_pokemon(pokemon):
    endpoint_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la solicitud: {str(e)}") 
