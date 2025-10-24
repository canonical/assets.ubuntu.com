# assets.![ubuntu](https://assets.ubuntu.com/v1/9f61b97f-logo-ubuntu.svg "Ubuntu").com codebase

The assets server manages the assets (mainly images and PDFs) for different Canonical and Ubuntu websites.

It has 2 main parts:

- https://assets.ubuntu.com/v1 : The API, which is a flask app that provides a RESTful API for storing and serving binary assets over HTTP
- https://assets.ubuntu.com/manager : The web interface, which is jinja2 templates that provide a web interface for managing the assets server

## Summary

- [assets..com codebase](#assetscom-codebase)
  - [Summary](#summary)
  - [Creating assets using the web interface](#creating-assets-using-the-web-interface)
  - [Transforming images](#transforming-images)
  - [Using the RestAPI](#using-the-restapi)
    - [Authentication](#authentication)
    - [Managing tokens](#managing-tokens)
      - [Generating a new token](#generating-a-new-token)
      - [Removing a token](#removing-a-token)
      - [Listing all the tokens](#listing-all-the-tokens)
    - [Managing assets](#managing-assets)
      - [Uploading assets](#uploading-assets)
      - [Deleting assets](#deleting-assets)
      - [Listing assets](#listing-assets)
        - [Pagination](#pagination)
    - [Managing redirects](#managing-redirects)
      - [Creating redirects](#creating-redirects)
      - [Updating redirects](#updating-redirects)
      - [Deleting redirects](#deleting-redirects)
  - [Security](#security)
  - [Caching](#caching)

## Creating assets using the web interface

You will need to login with an SSO account that is in the `canonical-content-people` team.

You can then create assets using the web interface at https://assets.ubuntu.com/manager/create.

## Transforming images

When getting an image asset, the asset can be transformed using the `op` (operation) option.

You can manually specify one of these operations along with their corresponding options:

- `region`:
  - `rect`: The region as x,y,w,h; x,y: top-left position, w,h: width/height of region
- `resize`:
  - `w`: Width
  - `h`: Height
  - `max-width`
- `max-height`:
- `rotate`:
  - `deg`: Degrees to rotate the image

The default option is resize and can be used without setting `op`.

The default option is resize and can be used without setting `op`, e.g.:

```
https://assets.ubuntu.com/v1/4d7a830e-logo-ubuntuone.png?w=30
```

Or you can use another feature, like `region` e.g.:

```
https://assets.ubuntu.com/v1/4d7a830e-logo-ubuntuone.png?op=region&rect=0,0,50,50
```

## Using the RestAPI

Creating a new asset can you be done using the [assets manager](https://assets.ubuntu.com/manager), however in case of advanced option such as image transformation or creating redirects, you can use the API directly.

### Authentication

The API uses a token based authentication system. You can specify your token in 3 different ways:

- As a `token` query parameter: e.g. `https://assets.ubuntu.com/v1?token=1234`
- As an `Authorization` HTTP header:

```
Authorization: "token 1234"
```

- In case of a POST request, along with the request body:

```
key: 1234
```

### Managing tokens

#### Generating a new token

You can generate a new token by running the following command:

```bash
curl -X POST --data name=token-name https://assets.ubuntu.com/v1/tokens?token={your-exisiting-token}
```

#### Removing a token

You can remove a token by running the following command:

```bash
curl -X DELETE https://assets.ubuntu.com/v1/tokens/{token-to-be-delete}?token={your-token}
```

#### Listing all the tokens

You can list all the tokens by running the following command:

```bash
curl https://assets.ubuntu.com/v1/tokens?token={your-token}
```

### Managing assets

#### Uploading assets

You can upload assets with the cryptically named [`upload-assets`](https://github.com/canonical/canonicalwebteam.upload-assets) tool. This can be installed with `snap install upload-assets` or `sudo pip3 install upload-assets`.

It's usually best to store your API key in your RC file (e.g. `~/.bashrc`) by adding a line like `export UPLOAD_ASSETS_API_TOKEN=xxxxxx`. (You then probably need to `source ~/.bashrc` to load the environment variable).

You can then upload assets:

```bash
$ upload-asset --api-domain localhost:8017 MY-IMAGE.png
{'url': u'http://localhost:8017/v1/xxxxx-MY-IMAGE.png', 'image': True, 'created': u'Tue Sep 27 16:13:22 2016', 'file_path': u'xxxxx-MY-IMAGE.png', 'tags': u''}
```

You can also directly upload assets using the API:

```bash
echo "asset=$(base64 -w 0 MY-IMAGE.png)" | \
  curl --request POST --data @- --data "friendly-name=MY-IMAGE.png" "https://assets.ubuntu.com/v1/?token={your-api-token}"
```

In the example above, we used an option called `friendly-name` which is an option among others:

- `asset`: (**required**) The base64 encoded asset
- `friendly-name`: (optional) The name of the asset to be included in the asset's URL
- `url-path`: (optional, default: the SHA1 of the `asset`) The path of the asset as it will be served over HTTP
- `optimize`: (optional, default: `false`) Whether to optimize the image, only works for images of type PNG, JPEG and SVG, this option is ignored for other types of assets
- `tags`: (optional, default: `[]`) A comma separated list of tags to be associated with the asset

#### Deleting assets

**Warning: Please read this before deleting anything**

_The assets server serves all assets with a `cache-control` header instructing all clients to cache the asset for a year. This is to get the best possible performance on our websites. You need to bear this in mind before deleting any assets. If the asset has been cached by any clients - from our own Content Cache, to other intermediary caches, to users' browsers - you may struggle to get the assets deleted from those caches._

_For this reason it's best to find ways around needing to regularly delete assets._

_This is also why the [assets manager](https://assets.ubuntu.com/manager) doesn't support deleting assets through the interface._

To delete an assets, simply use `curl` with the `DELETE` method:

```bash
curl --request DELETE "https://assets.ubuntu.com/v1/{asset-filename}?token={your-api-token}"
```

#### Listing assets

You can list all the assets by running the following command:

```bash
curl https://assets.ubuntu.com/v1/?token={your-api-token}
```

You can also filter the assets by:

- `tag`: Filter the assets by a specific tag or by a query string to filter the assets by filename, e.g. `tag=ubuntu` will return all the assets with `ubuntu` in their filename
- `type`: The type of the asset, e.g. `type=png` will return all the assets with the `png` extension
- `include_deprecated`: Whether to include or not the deprecated assets. Default is `false`

##### Pagination

By default, the API will return the first 20 assets. You can specify the number of assets to return by using the `per_page` query parameter, e.g. `per_page=100`.

You can also specify the page number by using the `page` query parameter, e.g. `page=2` (this will return the second page of assets).

### Managing redirects

Since assets are cached for a very long time, if you know you will want to update the version of an assets behind a specific URL, this should be achieved by setting up a (non-permanent) redirect to the assets.

E.g., Every day we upload the latest Server Guide to e.g. `https://assets.ubuntu.com/v1/25868d7a-ubuntu-server-guide-2022-07-11.pdf`, and then we change the `https://assets.ubuntu.com/ubuntu-server-guide` URL to redirect to this latest version.

#### Creating redirects

You can set up a new redirect with `curl --data redirect_path={the-path-to-redirect} --data target_url={the-redirect-target} https://assets.ubuntu.com/v1/redirects?token={your-api-token}`.

E.g. this would create the `https://assets.ubuntu.com/ubuntu-server-guide` redirect mentioned above:

```bash
$ curl --data redirect_path=ubuntu-server-guide --data target_url=https://assets.ubuntu.com/v1/25868d7a-ubuntu-server-guide-2022-07-11.pdf "https://assets.ubuntu.com/v1/redirects?token=xxxxxxxxxxx"
{
    "permanent": false,
    "message": "Redirect created",
    "target_url": "https://assets.ubuntu.com/v1/25868d7a-ubuntu-server-guide-2022-07-11.pdf",
    "redirect_path": "ubuntu-server-guide"
}
```

#### Updating redirects

Once a redirect already exists, you can use the `PUT` method to update it using `curl --request PUT --data target_url={target-url} https://assets.ubuntu.com/v1/redirects/{redirect-path}?token={your-api-token}`.

E.g. (following the above example):

```bash
$ curl --request PUT --data target_url=https://assets.ubuntu.com/v1/fe8d7514-ubuntu-server-guide-2022-07-13.pdf "https://assets.ubuntu.com/v1/redirects/ubuntu-server-guide?token=xxxxxxxxx"
{
    "target_url": "https://assets.ubuntu.com/v1/fe8d7514-ubuntu-server-guide-2022-07-13.pdf",
    "permanent": false,
    "redirect_path": "ubuntu-server-guide"
}
```

#### Deleting redirects

Deleting redirects is similarly simple, with `curl --request DELETE https://assets.ubuntu.com/v1/redirects/{redirect-path}?token={your-api-token}`, e.g. `curl --request DELETE https://assets.ubuntu.com/v1/redirects/ubuntu-server-guide?token=xxxxxxxxx`.

## Security

As the server only uses a basic token for authentication, it is paramount that in a production setting, the API functions are only accessed over HTTPS, to keep the API token secret. For this reason, when `DEBUG==false` the server will force a redirect to HTTPS for all API calls.

## Caching

The server is intended to be run in production behind a caching layer (e.g. [squid cache](http://www.squid-cache.org/)). And as the server stores assets by default with a unique hash corresponding to the file's contents (e.g. `<code><b>`a2f56da4`</b>`-some-image.png`</code>`), the cache expiration time should be as long as possible to maximise performance.
