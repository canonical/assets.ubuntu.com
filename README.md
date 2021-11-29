# Assets server

[![CircleCI build status](https://circleci.com/gh/canonical-web-and-design/assets.ubuntu.com.svg?style=shield)](https://circleci.com/gh/canonical-web-and-design/assets.ubuntu.com)
[![Coverage Status](https://coveralls.io/repos/github/ubuntudesign/assets.ubuntu.com/badge.svg?branch=master)](https://coveralls.io/github/ubuntudesign/assets.ubuntu.com?branch=master)

This is the codebase for https://assets.ubuntu.com, a Restful API service for storing and serving binary assets over HTTP, built with [Django REST framework](http://www.django-rest-framework.org/).

## Local development

The simplest way to run the site makes use of SQLite, which is not the same as production where it will use PostgreSQL:

``` bash
dotrun exec alembic upgrade head        # Run database migrations
dotrun exec flask token create mytoken  # Create a token
```

Save the output token

``` bash
dotrun  # Run the server
```

You can now access the API with your token in your browser - e.g.: <http://127.0.0.1:8017?token=THETOKEN>.

### Using PostgreSQL

``` bash
sudo apt-get install libpq-dev    # PostgreSQL libraries
python3 -m venv .venv             # Create a virtual environment
source .venv/bin/activate         # Enable the environment
pip3 install -r requirements.txt  # Install python dependencies

# Spin up a Docker postgresql database
docker run --rm --name db -e POSTGRES_PASSWORD=pw -d postgres
# Configure the database location
export DATABASE_URL=postgres://postgres:pw@`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db`/postgres
# Provision the database
alembic upgrade head

# Create a token
FLASK_APP=webapp.app flask token create mytoken
```

Now save the token that's output, and run the site with:

``` bash
# Run the site
./entrypoint 0.0.0.0:8017
```

You can now access the API with your token in your browser - e.g.: <http://127.0.0.1:8017?token=THETOKEN>.

### Security

As the server only uses a basic token for authentication, it is paramount that in a production setting, the API functions are only accessed over HTTPS, to keep the API token secret. For this reason, when `DEBUG==false` the server will force a redirect to HTTPS for all API calls.

### Caching

The server is intended to be run in production behind a caching layer (e.g. [squid cache](http://www.squid-cache.org/)). And as the server stores assets by default with a unique hash corresponding to the file's contents (e.g. <code><b>a2f56da4</b>-some-image.png</code>), the cache expiration time should be as long as possible to maximise performance.

### Migrations
If we need to change or create new models in `webapp.models` we can then run `./alembic revision --autogenerate -m "describe change here"`
to get the changes reflected as a data migration. Most of the changes you do [should be picked up](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).

## Using the server

### Transforming images

Images can be transformed using the `op` get option, along with the required arguments.

You can manually specify one of these operations along with their corresponding options:
 - `region`
  - `rect`: The region as x,y,w,h; x,y: top-left position, w,h: width/height of region
 - `resize`
  - `w`: Width
  - `h`: Height
  - `max-width`
  - `max-height`
 - `rotate`
  - `deg`: Degrees to rotate the image

The default option is resize and can be used without setting `op`
```
14e45f53-image.png?w=30
```

You can also specify multiple comma separated operations. They will be applied in the order they are listed.
```
14e45f53-image.png?op=region,resize&w=30&rect=0,0,50,50
```


### Tokens

To interact with the assets server, you'll need to generate an authentication token:

``` bash
$ dotrun exec ./manage.py gettoken {token-name}
Token '{token-name}' created
3fe479a6b8184be4a4cdf42085f19f9a
```

You can now pass this token in your requests to the assets server API. E.g.:

```
http://localhost:8017/v1/?token=3fe479a6b8184be4a4cdf42085f19f9a  # List all existing assets in JSON format
```

You can list all tokens with [scripts/list-tokens.sh](scripts/list-tokens.sh) or delete them with [scripts/delete-token.sh](scripts/delete-token.sh).

### Uploading assets via the command-line

The [asset-uploader project](https://github.com/ubuntudesign/asset-uploader) helps you upload assets from the command-line:

``` bash
$ ./upload-asset.py  \
    --server-url http://localhost:8017/v1/  \
    --auth-token XXXXXXXX  \
    MY-IMAGE.png
{'url': u'http://localhost:8017/v1/xxxxx-MY-IMAGE.png', 'image': True, 'created': u'Tue Sep 27 16:13:22 2016', 'file_path': u'xxxxx-MY-IMAGE.png', 'tags': u''}
```

### Assets manager

You may wish to setup the [assets-manager](https://github.com/ubuntudesign/assets-manager/), a simple web interface for managing assets on your assets server.

## Tests

You can run all tests with:

``` bash
dotrun test
```
