# Assets server

[![Build Status](https://travis-ci.org/ubuntudesign/assets-server.svg?branch=master)](https://travis-ci.org/ubuntudesign/assets-server)
[![Coverage Status](https://coveralls.io/repos/github/ubuntudesign/assets-server/badge.svg?branch=master)](https://coveralls.io/github/ubuntudesign/assets-server?branch=master)
[![CircleCI build status](https://circleci.com/gh/canonical-web-and-design/assets.ubuntu.com.svg?style=shield)](https://circleci.com/gh/canonical-web-and-design/assets.ubuntu.com) [![Code coverage](https://codecov.io/gh/canonical-web-and-design/assets.ubuntu.com/branch/master/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/assets.ubuntu.com)

This is the codebase for https://assets.ubuntu.com, a Restful API service for storing and serving binary assets over HTTP, built with [Django REST framework](http://www.django-rest-framework.org/).

## Local development

The simplest way to run the site locally is to first [install Docker](https://docs.docker.com/engine/installation/) (on Linux you may need to [add your user to the `docker` group](https://docs.docker.com/engine/installation/linux/linux-postinstall/)), and then use the `./run` script:

``` bash
./run
```

Once the containers are setup, you can visit <http://127.0.0.1:8017> in your browser.

### Security

As the server only uses a basic token for authentication, it is paramount that in a production setting, the API functions are only accessed over HTTPS, to keep the API token secret. For this reason, when `DEBUG==false` the server will force a redirect to HTTPS for all API calls.

### Caching

The server is intended to be run in production behind a caching layer (e.g. [squid cache](http://www.squid-cache.org/)). And as the server stores assets by default with a unique hash corresponding to the file's contents (e.g. <code><b>a2f56da4</b>-some-image.png</code>), the cache expiration time should be as long as possible to maximise performance.

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
$ ./run exec ./manage.py gettoken {token-name}
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

You can also use [curl](https://curl.haxx.se/docs/manpage.html):

``` bash
$ echo "asset=$(base64 -w 0 MY-IMAGE.png)" | \
  curl --data @- --data "friendly-name=MY-IMAGE.png" "http://localhost:8017/v1/?token=XXXXXX"
{
    "optimized": false,
    "created": "Wed Sep 28 11:07:33 2016",
    "file_path": "xxxxxxxx-MY-IMAGE.png",
    "tags": ""
}
```

### Assets manager

You may wish to setup the [assets-manager](https://github.com/ubuntudesign/assets-manager/), a simple web interface for managing assets on your assets server.

## Tests

You can run all tests with:

``` bash
./run test
```
