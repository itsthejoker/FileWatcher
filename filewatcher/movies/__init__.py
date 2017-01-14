#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# http://www.omdbapi.com/?t=aladdin&y=&plot=full&r=json

import requests
from addict import Dict


class OMDbAPI(object):
    '''
    Class that handles basic retrieval of information from the Open Movie
    Database API via Requests.
    '''
    def __init__(self):
        # shorthand identifiers for the OMDb
        self.url = 'http://www.omdbapi.com/'
        self.title = 't'
        self.year = 'y'
        self.plot = 'plot'
        self.request_type = 'r'

    def get_movie(self, movie_title, movie_year=None, full_plot=False):

        payload = {
            self.title: movie_title,
            self.year: movie_year,
            self.plot: ['full' if full_plot else 'short'],
            self.request_type: 'json'
        }

        r = requests.get(self.url, params=payload).json()
        response_dict = Dict()
        response_dict.update(r)

        response_dict = self._convert_keys(response_dict)

        return response_dict

    def _convert_keys(self, incoming_dict):
        correction_dict = {
            'Plot': 'plot',
            'Released': 'released',
            'Country': 'country',
            'Title': 'title',
            'Director': 'director',
            'Runtime': 'runtime',
            'Year': 'year',
            'Metascore': 'metascore',
            'Genre': 'genre',
            'Awards': 'awards',
            'Type': 'type',
            'imdbRating': 'imdb_rating',
            'imdbVotes': 'imdb_votes',
            'Language': 'language',
            'Poster': 'poster',
            'imdbID': 'imdb_id',
            'Writer': 'writer',
            'Actors': 'actors',
            'Response': 'response',
            'Rated': 'rated'
        }

        fixed_dict = Dict()
        for key, value in correction_dict.items():
            fixed_dict[value] = incoming_dict[key]

        return fixed_dict
