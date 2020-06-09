class GameRegistry:
    """
    A Game type registry and factory that enables game types to be defined as modules and registered with the factory.
    A Game module is a python class that inherits from Game, and calls register_game_type during module import.

    Available game types that have been registered can be queried using get_game_types, and creation of a specific game
        can be accomplished using the game names returned

    :type _gametypes: dict[str, cls] a string to class mapping of registered game types
    """
    def __init__(self):
        self._gametypes = {}

    def register_game_type(self, gametype: str, gameclass):
        print('registering {}'.format(gametype))
        """Register a game type based on a string name.  The game class should be a class derived from Game"""
        self._gametypes[gametype] = gameclass

    def get_game_types(self):
        """Return a list of game types registered"""
        return self._gametypes.keys()

    def create(self, gametype, **kwargs):
        """
        Create a game based on a type string, passing the keyword arguments to the Game for settings.
        :param gametype: a string containing the name of a game type to create
        :param kwargs: a set of keyword arguments containing game settings to provide the game class initialization
        :return: the created game
        """
        gameclass = self._gametypes.get(gametype)
        if not gameclass:
            raise ValueError('Game Type not recognized: {}'.format(gametype))
        return gameclass(**kwargs)


# A Global game registry object used to register and create games
GameFactory = GameRegistry()

import gametypes
