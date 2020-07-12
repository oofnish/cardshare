from deck import BasicCardDeck, BasicCard


class CatanDeckNames:
    DEVELOPMENT = 'Development'
    CLAY = 'Clay'
    ROCK = 'Rock'
    SHEEP = 'Sheep'
    WHEAT = 'Wheat'
    WOOD = 'Wood'


class CatanDevelopmentNames:
    KNIGHT = 'Knight'
    YOP = 'Year Of Plenty'
    ROADBUILD = 'Road Building'
    MONOPOLY = 'Monopoly'
    VICTORY = 'Victory Point'


class CatanDeck(BasicCardDeck):
    """A Basic car deck that defines the decks of cards used in Settlers of Catan.   Note: the descriptions here are
        derived from the text printed on the real game cards from Mayfair Games."""
    def __init__(self, game_size):
        """ For SoC, the game size indicates the number of development cards available.  After definining each type
            of card, the correct amounts are created using the init_deck* functions """
        super().__init__()

        self.define_card(CatanDevelopmentNames.KNIGHT,
                         'Move the robber. Steal 1 resource card from the owner of an adjacent settlement or city.')
        self.define_card(CatanDevelopmentNames.YOP,
                         'Take any 2 resources from the bank. Add them to your hand. They can be 2 of the same resource'
                         ' or two different resources.')
        self.define_card(CatanDevelopmentNames.ROADBUILD, 'Place 2 new roads as if you had just built them.')
        self.define_card(CatanDevelopmentNames.MONOPOLY,
                         'When you play this card, announce 1 type of resource. All other players must give you all'
                         ' their resources of that type.')
        self.define_card(CatanDevelopmentNames.VICTORY, 'Play to increase your victory point score by 1.')

        if game_size > 4:
            self.init_deck_six()
        else:
            self.init_deck_four()

    def init_deck_four(self):
        """Development card deck counts for a 2-4 player game"""
        self.add_cards(CatanDevelopmentNames.KNIGHT, 14)
        self.add_cards(CatanDevelopmentNames.YOP, 2)
        self.add_cards(CatanDevelopmentNames.ROADBUILD, 2)
        self.add_cards(CatanDevelopmentNames.MONOPOLY, 2)
        self.add_cards(CatanDevelopmentNames.VICTORY, 5)

        self.reset_deck()

    def init_deck_six(self):
        """Development card deck counts for a 5-6 player game"""
        self.add_cards(CatanDevelopmentNames.KNIGHT, 20)
        self.add_cards(CatanDevelopmentNames.YOP, 3)
        self.add_cards(CatanDevelopmentNames.ROADBUILD, 3)
        self.add_cards(CatanDevelopmentNames.MONOPOLY, 3)
        self.add_cards(CatanDevelopmentNames.VICTORY, 5)

        self.reset_deck()


class CatanResourceDeck(BasicCardDeck):
    """
    The Catan Resource cards are a simple deck of cards for each resource.  Each resource deck contains only one type of
    card. While the real game contains a finite set of each resource, in practice, they are essentially endless. Becasue
    of this, it is not necessary to track the number of resource cards availalble in the deck.  Thus, this version of
    card deck provides an infinite pool of these cards by overriding the draw() function
    """
    def __init__(self, resource_name):
        super().__init__()
        self.resource_name = resource_name

    def draw(self):
        """
        Drawing a resource card instantiates a card and directly returns it, versus keeping an internal list of cards
        """
        return BasicCard(self.resource_name, 'A unit of {} resource'.format(self.resource_name)).instance()

    def __len__(self):
        """The length is meaningless for this  deck type, just return a big number"""
        return 9999
