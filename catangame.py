from game import Game
from gameregistry import GameFactory
from catandeck import CatanDeck, CatanResourceDeck, CatanDeckNames


GAME_TYPE_CATAN = 'Catan'


class CatanGame(Game):
    """
    A Game that models the card types and rules in Settlers of Catan.  This game has one Development deck ( private
        hand of cards for players) and five Resource decks, each of a single type of resource.
    The game itself does not need any special operations outside of the interface provided by Game, except for the data
        definition in __init__
    """
    def __init__(self, **kwargs):
        max_players = kwargs.get('max_players', 0)
        super().__init__(max_players)

        self.add_deck(CatanDeckNames.DEVELOPMENT, CatanDeck(max_players))
        self.add_deck(CatanDeckNames.CLAY, CatanResourceDeck(CatanDeckNames.CLAY))
        self.add_deck(CatanDeckNames.ROCK, CatanResourceDeck(CatanDeckNames.ROCK))
        self.add_deck(CatanDeckNames.WHEAT, CatanResourceDeck(CatanDeckNames.WHEAT))
        self.add_deck(CatanDeckNames.WOOD, CatanResourceDeck(CatanDeckNames.WOOD))
        self.add_deck(CatanDeckNames.WOOL, CatanResourceDeck(CatanDeckNames.WOOL))


# register the game type with the game factory
GameFactory.register_game_type(GAME_TYPE_CATAN, CatanGame)
