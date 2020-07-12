## Cardshare

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
