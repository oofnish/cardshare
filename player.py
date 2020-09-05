from deck import BasicCard


class PlayerData:
    """
    Container for player data, and interface for actions involving players.

    :type hand_cards: dict[str, list[BasicCard]] a set of card lists keyed by hand name
    :type hand_names: list[str] a list of potential hand names, which contains the key names for hand_cards even if the
        player doesn't currently have a hand of those cards, and providing the opportunity to provide consistent sorting
    """
    def __init__(self, name: str):
        """Initialize the player, setting the players name and empty data storage"""
        self.hand_cards = {}
        self.hand_names = []
        self.name = name

    def reset_player(self):
        """Reset the player's card ownership.  Note, hand_cards is not cleared."""
        self.hand_cards.clear()

    def add_card_to_hand(self, hand_name: str, card: BasicCard):
        """Add a BasicCard to the specified hand, and creates the hand if it does not yet exist."""
        if hand_name not in self.hand_cards:
            self.add_hand(hand_name)

        self.hand_cards[hand_name].append(card)

    def add_hand(self, hand_name):
        """Add a new hand to this player's data collection.  In the default implementation, this also creates an empty
            hand in addition to adding the name to the list of hands"""
        if hand_name not in self.hand_names:
            self.hand_names.append(hand_name)
        self.hand_cards[hand_name] = []

    def find_card(self, card_id):
        """Find a card by ID in the player's hands, returning the hand name and card if found"""
        for h, cards in self.hand_cards.items():
            for c in cards:
                if c.cardid == card_id:
                    return h, c
        return None, None

    def get_cards(self, filter_list):
        """
        Get all cards in an array based on the provided filter
        :param filter: an array of filters to apply
        :return: a list of cards matching the filter rules
        """
        hands = [h for h in self.hand_names]

        for f in filter_list:
            nv = f.split('=')
            if nv[0] == 'hand':
                if nv[1].startswith('-'):
                    hands.remove(nv[1][1:])

        cards = []
        for h in hands:
            cards.extend(self.hand_cards[h])

        return cards

    def remove_card_by_id(self, card_id):
        """Remove a card id from a player's hand(s), no matter what hand it appears in, and no matter how many times it
            appears."""
        for h, cards in self.hand_cards.items():
            # instead of search/remove, just reconstruct the list with the non-removed cards.
            self.hand_cards[h] = [c for c in cards if c.cardid != card_id]
