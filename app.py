"""
Cardshare

A simple web application enabling remote sharing of decks of cards for playing board games over screen share.  Games are
 implemented in a modular fashion, allowing a new game to be defined easily and enabling all games to use a common
 interface.  The intent of this system is for a group of friends who wish to play board games requiring private card
 hands to share a board (via screen or otherwise), and maintain their card hands with a private view into a common card
 deck.

Web communication is provided by Flask, and HTML rendered using Jinja2.  Communication after initial view render is done
 using rest style form posts, allowing the front end to be replaced with other mechanisms for providing a user interface
 if desired. When using a web interface, Flask provides input sanitation by default, and data is returned in Json
 format, which can be directly used by JQuery or a libary like mustache.js to provide dynamic data updates.

Since this uses Flask, a WSGI web application server (uWSGI, gunicorn) is required to host the application.  HTML view
 is templated HTML5 using CSS and javascript libraries JQuery, Skel, FontAwesome, and Mustache.  All resources used are
 available free on the Internet.

Future updates will expand the available game types ( At first, only a representation of Settlers of Catan is available)
 and possibly provide a mechanism for creating ad-hoc rules or games without source modification.

TODO: Concurrency note:  Flask by default runs in a single threaded mode, so applying synchronization techniques is not
    necessary for now. However, as a generic implementation, the Game object should handle multithreaded access, and
    synchronization should be handled appropriately there.

Note: text for card descriptions are derived from publishers of their respective games:
 Settlers of Catan: Mayfair Games

Web design is based on one from Templated (templated.co)
 Images are (c) unsplash.com

Code and modifications (c) Chase Grund

"""

from flask import Flask, render_template, url_for, redirect, request, session, make_response
from gameregistry import GameFactory

INVALID_SESSION_ERROR = 403
GAME_DATA_ERROR = 400
DEFAULT_GAME_TYPE = 'Catan'

app = Flask(__name__)
app.secret_key = b'?oneplus56=ninety7-4O!'

Games = {}


class CardShareException(Exception):
    pass


##############
# Helper processing functions, for creating games and adding players
##############


def create_game(game_type: str, owner_player_name: str, **kwargs):
    """Create a new game based on the Game Type string, owning player name, and game settings arguments as keyword args.

    :param game_type: A registered game type string, ref: gameregistry.py
    :param owner_player_name: A player name that will be set as the game owner, and the first player
    :param kwargs: a list of keyword arguments containing game creation parameters.
        TODO: refactor game creation parameters to a game-driven dynamic ruleset, move validation to game/rules module
    :return: None
    :raise: CardShareException if maximum players is <= 1, if the owner player name is invalid, or if the specified
        game type is not recognized.  Note: the same exception can be raised from the internal call for player add
    """
    # for now, validate max players game parameter here
    max_players = kwargs.get('max_players')
    if not max_players or max_players < 2:
        raise CardShareException('Invalid maximum player count provided, must be greater than 2')
    if not owner_player_name:
        raise CardShareException('A player name for the first player must be provided to create a game')

    newgame = GameFactory.create(game_type, max_players=max_players)
    if not newgame:
        raise CardShareException('Unrecognized game type: {}'.format(game_type))

    Games[newgame.game_key] = newgame

    add_new_player_to_game(newgame.game_key, owner_player_name)
    newgame.set_owner(owner_player_name)


def add_new_player_to_game(game_key: str, player_name: str):
    """Add a player to an existing game, based on the provided game key string and player name.

    :param game_key: A string containing a game key.  ref: game.py
    :param player_name: A player name, likely originating from player input.
    :return: None
    :raise: CardShareException if the game key is invalid, no player name is provided, the game key is not recognized,
        or the player name provided already exists in the game.
    """

    if not game_key:
        raise CardShareException('Please enter a valid game ID.')
    if not player_name:
        raise CardShareException('Please enter a player name.')
    if game_key not in Games:
        raise CardShareException('Unknown game ID specified when adding new player to game {} (player name: {})'.format(
                                 game_key,
                                 player_name))
    if player_name in Games[game_key].players:
        raise CardShareException('Player already exists in game {} (player name: {})'.format(
                                 game_key,
                                 player_name))

    Games[game_key].add_player(player_name)

    session['game_key'] = game_key
    session['player_name'] = player_name


##############
# Launch pages for initializing and joining games
##############


@app.route('/')
@app.route('/index')
def index_page():
    """A simple landing page, providing options to join or create a game."""
    return render_template('index.html')


@app.route('/create', methods=['POST', 'GET'])
def handle_create():
    """Game creation page, providing game type and rules settings and an input for the owning player name
        GET requests (eg. standard navigation) fall through to simply rendering the template page, while a post
        request (likely from a form on the page itself) forward data to game creation and redirect to the main game view
        Errors during handling of a post fall through to rendering the template with an error string for the user.

        TODO: since only one game type is implemented, game type is defaulted to DEFAULT_GAME_TYPE. ensure this is
            changed when more game types are added, and a game type selection provided on the create screen.
    """
    error_msg = None
    if request.method == 'POST':
        game_type = request.form.get('game-type', DEFAULT_GAME_TYPE)
        max_players = request.form.get('game-size', 0, type=int)
        player_name = request.form.get('name')
        try:
            create_game(game_type, player_name, max_players=max_players)
            return redirect(url_for('hand_view'))
        except CardShareException as cse:
            error_msg = str(cse)

    return render_template('create.html', error_msg=error_msg)


@app.route('/join', methods=['POST', 'GET'])
def handle_join():
    """Game join page, providing input for game ID and player name
        GET requests (eg. standard navigation) fall through to simply rendering the template page, while a post
        request (likely from a form on the page itself) forward data to player add and redirect to the main game view.
        Errors during handling of a post fall through to rendering the template with an error string for the user.
    """
    error_msg = None
    if request.method == 'POST':
        player_name = request.form.get('name')
        game_id = request.form.get('gameid').upper()
        try:
            add_new_player_to_game(game_id, player_name)
            return redirect(url_for('hand_view'))
        except CardShareException as cse:
            error_msg = str(cse)

    return render_template('join.html', error_msg=error_msg)


##############
# Main Game views
##############


@app.route('/handview')
def hand_view():
    """Main view for players, dynamic display of currently held cards, actions for drawing and trading, etc.  Here,
        the session data is checked, and if not found/invalid the user is redirected to the join game page.
        Actions performed on the page should use REST apis for manipulation and dynamic data display through jquery
    """

    if 'game_key' not in session or 'player_name' not in session:
        return redirect(url_for(handle_join))
    game_key = session['game_key']
    player_name = session['player_name']

    if game_key not in Games:
        return redirect(url_for(handle_join))
    game = Games[game_key]

    if player_name not in game.players:
        return redirect(url_for(handle_join))

    player = game.players[player_name]

    return render_template('handview.html', game=game, player=player, is_owner=(game.owner == player_name))


@app.route('/debug')
def debug_view():
    """Debug view.  Provides the full games collection for debugging game data during play testing.  Actions on this
        page perform operations impersonated as an appropriate player (eg. discarding cards)
        TODO: as this obviously allows cheating, remove before publish, review REST apis to remove impersonation
            facilities
    """

    return render_template('debug.html', games=Games)


##############
# JQuery / REST api functions.
#    These assume active sessions, return INVALID_SESSION_ERROR http code if not
##############


@app.route('/cardaction', methods=['POST'])
def card_action():
    """Card action API, triggers an action based on a specific card identifier.

    Post Params:
    cardid: an identifier for a specific card
    action: a string representing the action to perform.
    player_name: a string containing a player name, defaults to the session player name
    game_key: a string containing the active game key, defaults to the session game key

    :return 'success' and http 200 when the operation is successful, INVALID_SESSION_ERROR for failures

    TODO: when removing debug tools, force use of session data for player name and game key to remove impersonation
    """

    player_name = request.form.get('player_name', session['player_name'])
    game_key = request.form.get('game_key', session['game_key'])
    cardid = request.form.get('cardid')
    action = request.form.get('action')
    if game_key not in Games:
        return make_response('Game Not found', INVALID_SESSION_ERROR)
    game = Games[game_key]
    game.card_action(player_name, cardid, action)

    return 'success'


@app.route('/queryplayers', methods=['POST'])
def query_players():
    """Query a list of players in the current or specified game.  An optional 'exclude_player' parameter allows the list
    to filter out a single player's name, useful for getting a list of other players, eg. when trading a card

    Post Params:
    game_key: a game identifier to query for a list of players
    exclude_player: a player name to exclude from the list, returning all other players

    :return A Json formatted list of player names, and http 200 if successful, or INVALID_SESSION_ERROR if the game is
        not found.
    """

    game_key = request.form.get('game_key', session['game_key'])
    exclude_player = request.form.get('exclude_player')
    if game_key not in Games:
        return make_response('Game Not found', INVALID_SESSION_ERROR)
    game = Games[game_key]
    # create and return single-element dictionary for Json format
    return {'players': [pname] for pname in game.players if pname != exclude_player}


@app.route('/drawcard', methods=['POST'])
def draw_card():
    """Draw a card from a specified game deck.  The game interface will add the card to the player's hand, here we
        obtain the card and return its dictionary elements in the response so a jquery action can update view data
        'atomically'.

    Post Params:
    deck_name: the name of the card deck to draw from.
    hand_name: the name of the hand to add the card to. By default, this is named the same as the deck name

    :return A json formatted dictionary of card information fields and http 200 if successful. INVALID_SESSION_ERROR if
        the game is not found, or GAME_DATA_ERROR if there are no more cards available in that deck.
    """
    player_name = session['player_name']
    game_key = session['game_key']
    deck_name = request.form.get('deck_name')
    hand_name = request.form.get('hand_name', deck_name)
    if game_key not in Games:
        return make_response('Game Not found', INVALID_SESSION_ERROR)
    game = Games[game_key]
    card = game.player_draw_card(player_name, deck_name, hand_name)
    if not card:
        return make_response('Deck is Empty', GAME_DATA_ERROR)
    return card.__dict__


##############
# Entry
##############


if __name__ == '__main__':
    app.run()
