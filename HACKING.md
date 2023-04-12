# Working on the assets project

The ubuntu.com codebase is a [Flask](https://flask.palletsprojects.com/) app, which builds on our own [flask-base](https://pypi.org/project/canonicalwebteam.flask-base/), [templatefinder](https://pypi.org/project/canonicalwebteam.templatefinder/), [blog](https://pypi.org/project/canonicalwebteam.blog/) and [search](https://pypi.org/project/canonicalwebteam.search/) packages.

We use [Yarn](https://yarnpkg.com/lang/en/) for building static files like CSS through [`package.json` scripts](https://yarnpkg.com/lang/en/docs/package-json/#toc-scripts).

## Setup

1. To run the project simply, you will need to install `dotrun`, by following the [installation instructions](https://github.com/canonical/dotrun#installation)
2. docker: Docker is used to run the project. You can install it by following the [installation instructions](https://docs.docker.com/install/)
3. docker-compose: Docker compose is used to run the Postgres database and the SWIFT server (files server), you can install it by following the [installation instructions](https://docs.docker.com/compose/install/)

## Running the project

### Starting the database and the SWIFT server

To start the database and the SWIFT server, run:

```bash
docker-compose up -d
```

### Starting the project

To start the project, run:

```bash
dotrun
```

That's it! The project should now be running at http://localhost:8017/manager.

### Generating API tokens

To generate a new API token, run:

```bash
dotrun exec flask token create test
```

To list all the API tokens, run:

```bash
dotrun exec flask token list
```
