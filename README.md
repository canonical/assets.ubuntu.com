Assets server
===

This is a Restful API service for creating and serving assets.

It's built using [Django REST framework](http://www.django-rest-framework.org/).

Commits will be synced from the [Github project](https://github.com/CanonicalLtd/assets-server) to the [Launchpad project](https://launchpad.net/assets-server) using [bzr-sync](https://wiki.canonical.com/ProjectsSyncedFromGitToBzr). You can and should only push your changes to Github, and let `bzr-sync` take care of the rest.

Dependencies
---

Install system dependencies:

``` bash
sudo apt-get install mongodb libjpeg-dev zlib1g-dev libpng12-dev libmagickwand-dev python-dev
```

Then you can install the Python dependencies:

``` bash
pip install -r requirements.txt
```

Local development
---

And run the service:

``` bash
python manage.py runserver
```
