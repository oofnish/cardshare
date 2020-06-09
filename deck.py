from random import shuffle, seed
from uuid import uuid4


class CardDeckException (Exception):
    pass


class BasicCard:
    """
    Definition of a basic card object.  Game specific cards should subclass this, if necessary, to provide more detailed
        information about a card's properties.  The basic implementation provides name, description, and the cruical
        card id.
    It is intended that cards be instantiated using the 'Instance' function, enabling actions to be taken specifically
        when grabbing a specific card versus a prototype card
    """
    def __init__(self, cardname: str, carddesc: str):
        self.cardid = ''
        self.name = cardname
        self.description = carddesc

    def instance(self):
        """Instantiating a basic card assigns an ID, which is an overkill-level uuid currently"""
        self.cardid = str(uuid4())
        return self


class BasicCardDeck:
    """
    Provides the definition of cards within a card deck, and a collection of currently instantiated cards.  The shared
        deck contains a finite set of cards that are shuffled during creation in the base implementation.  card types
        and card type count fields maintain the rules for creating the shared deck (which cards, and how many)
    """
    def __init__(self):
        """During initialization, the random number generator is seeded with the current time,  for relatively
        deterministic shuffling."""
        self.shared_deck = []
        self.card_type_count = {}
        self.card_types = {}
        seed()

    def define_card(self, cardname: str, carddesc: str):
        """
        Create a card definition for a basic card.  the card name and description values are passed directly to
           creating the prototype for the card (not an instance, to avoid card information objects having default card
           ids.) if a card name already exists, it is removed and replaced
        :param cardname: name of the card to create ( BasicCard->name )
        :param carddesc: description of the card to create (BasicCard->description)
        """
        if cardname in self.card_types:
            del self.card_types[cardname]

        self.card_types[cardname] = BasicCard(cardname, carddesc)

    def add_cards(self, cardname: str, count: int):
        """
        Adds a quantity of cards based on card name and count.  The cards should have already been defined with define
            card, otherwise a CardDeckException is raised.  This is a definition-only action, cards are not instantiated
            until build_deck is called.
        :param cardname: a name of the card to assign a quantity.
        :param count: the number of this card to add to the deck
        """
        if cardname not in self.card_types:
            raise CardDeckException('Invalid card type specified: {}'.format(cardname))

        self.card_type_count[cardname] = count

    def build_deck(self):
        """
        Trigger the creation of the shared deck, which contains instantiated cards based on the definition and counts.
            Here, the cards are actually instantiated (assigning IDs to them) and added to the finite collection. should
            the shared deck already exist, the contents are discarded before the deck is rebuilt.
        """
        self.shared_deck = []

        for name, count in self.card_type_count.items():
            card = self.card_types[name]
            for c in range(count):
                self.shared_deck.append(BasicCard(card.name, card.description).instance())

    def reset_deck(self):
        """
        Reset the deck by (re)running the Build and Shuffle operations.
        """
        self.build_deck()
        self.shuffle_deck()

    def shuffle_deck(self):
        """
        Shuffle the shared deck card list, using the shuffle function from random
        """
        shuffle(self.shared_deck)

    def draw(self):
        """
        Draws a card from the shared list, removing it from the list and returning it.
        :return: next BasicCard drawn from the shared deck, or None if there are no cards left.
        """
        if len(self.shared_deck) > 0:
            return self.shared_deck.pop()
        return None

    def __len__(self):
        """
        Override the class length to return the current size of the shared deck
        :return: number of items in the deck
        """
        return len(self.shared_deck)
