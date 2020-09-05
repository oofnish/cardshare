import random
import string
from player import PlayerData
from deck import BasicCardDeck, BasicCard
from random import shuffle

GAME_KEY_LENGTH = 5


class BaseCardActions:
    """
    Definition of card actions. Each Game subclass should maintain their own collection of these actions that are
      approppriate for their own ruleset.  The base set provides only a very limited set of options.
    """
    DISCARD = 'discard'
    TRADE = 'trade'


class Game:
    """
    Primary game representation, provides common card and player operations, and acts as the primary interface for
        manipulating game data.
    This generic superclass provides common operations, and is intended to be subclassed for specific game types that
        specify their own data.  Notably, while the base class defines storage for card decks, the definition of those
        card decks is left to implementing classes.

    :type players: dict[str, PlayerData] The current list of players in the game
    :type card_decks: dict[str, BasicCardDeck] The current decks of cards, as defined for a Game subclass
    :type game_key: str A game identifier/key for this game

    TODO: Game rules, such as max_players, should be separated out and accessed with a common interface. Ensure the
        initialization of this and sub classes are updated when this is done.
    """
    def __init__(self, max_players: int):
        """
        Create a game object. Each subclass should ensure this is called first before configuring their data.
        :param max_players: maximum number of players allotted for this game
        """
        self.owner = None

        self.players = {}
        self.card_decks = {}

        self.max_players = max_players
        self.game_key = self.generate_random_key(GAME_KEY_LENGTH)

    @staticmethod
    def generate_random_key(length: int) -> str:
        """
        A static method to randomly generate a game ID / key of a specified length.  Keys are uppercase ascii character
            strings that can be easily shared to allow players to join each other's game.
        :param length: integer length for how long the key should be
        :return: randomly generated string of uppercase characters of length
        """
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for _ in range(length))

    def add_deck(self, name: str, deck_object: BasicCardDeck):
        """
        Add a BasicCardDeck or subclass to this game instance.  This is primarily intended to be a common helper
          function for adding card decks when defining game data in a Game subclass.
        :param name: a name for the deck, used as reference when performing deck operations such as draw
        :param deck_object: a BasicCardDeck object that contains card instances and provides reference to their data
        :return: None
        """
        self.card_decks[name] = deck_object

    def add_player(self, player_name: str):
        """
        Add a player to the game.  This creates and initializes a new player object.  As part of this process, informs
            the player object of the potential card hands using the player object add_hand interface
        :param player_name: a string that will identify the player.
        :return: None
        """
        player_data = PlayerData(player_name)
        for deck in self.card_decks.keys():
            player_data.add_hand(deck)
        self.players[player_data.name] = player_data

    def set_owner(self, player_name: str):
        """
        Set the owner of this game to the identified player.  An owner could be granted special permissions to
            administer the game during play, though such functionality is not provided in the base Game class.  As such,
            this function should be overridden to implement any ownership logic required by a Game subclass
        :param player_name: Name of the player who will receive ownership
        :return:
        """
        self.owner = player_name

    def draw_card(self, deck_name: str) -> BasicCard:
        """
        draws a card from the specified deck, using the deck object's draw interface.  The card is returned for
            reference or to be placed in another collection.  If the deck name is invalid, or no cards are available,
            None is returned.
            For typical player draw actions, use player_draw_card instead -- this function is intended for cases when
            a card should be drawn without automatic player ownership.
        :param deck_name: the name of a card deck to draw a card from.
        :return: BasicCard if one is found in the specified deck, or None
        """
        card = None

        if deck_name in self.card_decks:
            card = self.card_decks[deck_name].draw()

        return card

    def card_action(self, player_name: str, target_player: str, card_id: str, action: str):
        """
        Perform an action as the provided player on the specified card.  Subclasses should override this function to
            provide expanded card actions based on their rule set.  If the action is not understood, the player does not
            exist, or the action fails -- this function fails silently.
        TODO: card actions could be moved into a polymorphic rules class to enable the interface to be better
            formalized, and would provide better ability to add required parameters, such as 'target', and error
            handling interface
        :param player_name: The player performing the action
        :param target_player: A player receiving the action
        :param card_id: The identifier for the card involved in the action
        :param action: a string declaring what action to peform.  This string should be in the BaseCardActions enum
        :return: None
        """
        if player_name not in self.players:
            return

        if action == BaseCardActions.DISCARD:
            self.players[player_name].remove_card_by_id(card_id)
        if action == BaseCardActions.TRADE:
            hand, card = self.players[player_name].find_card(card_id)
            if card is None or hand is None:
                return
            self.players[target_player].add_card_to_hand(hand, card)
            self.players[player_name].remove_card_by_id(card_id)

    def random_card(self, player_name: str, filter: str):
        """
        Search player's hand for a random card that matches the filter properties
        :param player_name: player to query for cards
        :param filter: filter to apply when searching for a card
        :return: a card object or None if no cards are available
        """

        if player_name not in self.players:
            return None
        filter_rules = filter.split(';')
        cards = self.players[player_name].get_cards(filter_rules)

        shuffle(cards)

        return cards[0]

    def player_draw_card(self, player_name, source_deck, dest_hand=None) -> BasicCard:
        """
        Draws a card for a specified player. This function is preferred over 'draw_card' for most player draw actions,
            as it adds the card to the appropriate hand owned by the player.  The drawn card is returned for reference
        :param player_name: Name of the player that will receive the card
        :param source_deck: The source Game card deck from which to draw
        :param dest_hand: The destination player's hand to receive the card. By default, (if None), this uses the deck
            name for the hand name
        :return: BasicCard object representing the card drawn and added to the player's hand
        """
        if not dest_hand:
            dest_hand = source_deck
        card = self.draw_card(source_deck)
        if card:
            self.players[player_name].add_card_to_hand(dest_hand, card)
        return card


