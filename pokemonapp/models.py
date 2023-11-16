from django.db import models

class Pokemon:

    def __init__(self, name: str, url_image: str = None, number_abilities: int = None):
        self.name = name
        self.url_image = url_image
        self.number_abilities = number_abilities

    def __str__(self):
        return f"{self.name} - Abilities: {self.number_abilities}"
    