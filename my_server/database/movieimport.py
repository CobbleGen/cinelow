from .pers_movie_dbf import add_movie, get_movie
import requests
import json

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

def importFromPage(page):
    respons = requests.get('https://api.themoviedb.org/3/movie/top_rated?api_key=' + tmdb_key + '&page=' + page)
    if respons.status_code != 200:
        print('Failed.')
    else:
        movie_data = json.loads(respons.text)
        for result in movie_data['results']:
            if not get_movie(result['id']):     
                yes_no = input(f'Import "{result["original_title"]}" \t y/n? \t')
                if yes_no == 'y':
                    add_movie(result['id'])
        answer = input(f'Page {page} finished, continue? \t y/n? \t ')
        if answer == 'y':
            importFromPage(str(int(page)+1))


start_page = input('What starting page do you want?')
importFromPage(start_page)


#from my_server.database import movieimport
#Next up: 31