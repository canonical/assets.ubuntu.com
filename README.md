Assets server
===

This is a Restful API service for creating and serving assets.

It's built using [Django REST framework](http://www.django-rest-framework.org/).

Commits will be synced from the [Github project](https://github.com/CanonicalLtd/assets-server) to the [Launchpad project](https://launchpad.net/assets-server) using [bzr-sync](https://wiki.canonical.com/ProjectsSyncedFromGitToBzr). You can and should only push your changes to Github, and let `bzr-sync` take care of the rest.

Usage
---

### Development

``` bash
make setup    # Install dependencies
make develop  # Run development server on port 8012
```

### Tokens

To interact with the assets server, you'll need to generate a token:

``` bash
$ scripts/get-token.sh your-name  # Generate a new token called "your-name"
Token 'your-name' created
3fe479a6b8184be4a4cdf42085f19f9a
```

You can now pass this token in your requests to the assets server API. E.g.:

```
http://localhost:8012/v1/?token=3fe479a6b8184be4a4cdf42085f19f9a  # List all existing assets in JSON format
```

Advanced usage
---

### Python environment

By default `make setup` will create a new python environment in a folder called `env` in the project directory.

However, if you first create a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/), `make setup` will install dependencies into there instead. E.g.:

``` bash
mkvirtualenv assets-server  # Make our custom virtual environment using virtualenvwrapper
make setup                  # Install dependencies into this new environment
```

### Server ports

You can tell the development server to run on any port using the `PORT` environment variable. E.g.:

``` bash
PORT=9001 make develop  # Run the development server on port 9001
```

Tests
---

First create a new token for the tests to use:

``` bash
scripts/get-token.sh tests > tests/fixtures/api-token
```

Run the tests with [pytest](http://pytest.org/:

``` bash
py.test
```
