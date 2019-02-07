# CashWash
2018 will remain in history as the year in which the puzzle of populist souverainism started coming together in a big network of illicit cash flows. Having experience in crime prevention and bank transactions, at the end of December 2018 I got hold of my first money laundering data set. The result is an open source project I called CashWash and this is its code repository.

This project is using data from:

* the [Azerbaijani Laundromat](https://www.occrp.org/en/azerbaijanilaundromat/) investigation by [OCCRP](https://occrp.org) and [Berlingske](https://www.berlingske.dk), available under the [CreativeCommons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) license.
* [OpenCorporates](https://opencorporates.com) under their [CreativeCommons Atrribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/) licence.
* [Bank.codes](https://bank.codes).
* [Wikipedia](https://wikipedia.org/) available under [ Creative Commons Attribution-ShareAlike 3.0](https://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License) license.
* [FontAwesome](http://fontawesome.com/) under [CreativeCommons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) according to their [free license](https://fontawesome.com/license/free).

No data from any of these data sources is published here. The platform allows you to provide your own API keys and extract any data yourself. To this end consider requesting your own license and adding it as indicated in the [private.py](https://github.com/mapto/CashWash/blob/master/private.py) file.

There are currently two versions supported, one using [flask](http://flask.pocoo.org/), and one using [bottle](https://bottlepy.org/docs/dev/). The version you want would determine the dependencies you want to install. If unsure, I suggest going for bottle.

# Installation and configuration

This project requires [python3](https://www.python.org/download/) and a [SQLite](https://sqlite.org) server.

To install dependencies to run with bottle you need to run this command first:

    pip3 install bottle sqlalchemy requests pyquery confusable_homoglyphs

If you prefer flask, the alternative is: 

    pip3 install flask sqlalchemy requests pyquery confusable_homoglyphs

Once project and dependencies downloaded, request your private keys for the external data sources, as [indicated](https://github.com/mapto/CashWash/blob/master/private.py). These will give you access to the data sources, they will not extract the data. Data itself is fetched on-demand.

Finally, you might wish to review your [settings](https://github.com/mapto/CashWash/blob/master/settings.py), but the defaults should work fine.

# Use

To Initialize the database, run

	python3 import_laundromat.py

Then, running the server is simple, for bottle (recommended) just use:

	python3 app_bottle.py

Or respectively for flask:

	python3 app_flask.py


