# Working on the assets project

The ubuntu.com codebase is a [Flask](https://flask.palletsprojects.com/) app, which builds on our own [flask-base](https://pypi.org/project/canonicalwebteam.flask-base/), [templatefinder](https://pypi.org/project/canonicalwebteam.templatefinder/), [blog](https://pypi.org/project/canonicalwebteam.blog/) and [search](https://pypi.org/project/canonicalwebteam.search/) packages.

We use [Yarn](https://yarnpkg.com/lang/en/) for building static files like CSS through [`package.json` scripts](https://yarnpkg.com/lang/en/docs/package-json/#toc-scripts).

## Setup

1. To run the project simply, you will need to install `dotrun`, by following the [installation instructions](https://github.com/canonical/dotrun#installation)
2. docker: Docker is used to run the project. You can install it by following the [installation instructions](https://docs.docker.com/install/)
3. docker-compose: Docker compose is used to run the Postgres database and the SWIFT server (files server), you can install it by following the [installation instructions](https://docs.docker.com/compose/install/)
4. [Taskfile](https://taskfile.dev/docs/installation): It is used to run everything with a single `task` command.

## Running the project

Please make sure you are running the latest version of 
- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/install/)
- [Taskfile](https://taskfile.dev/docs/installation)

Starting the project with all it's services is as simple as

```bash
task
```

That's it! The project should now be running at http://localhost:8017/manager.

You can stop the project using

```bash
task stop
````

Please checkout [Taskfile.yml](/Taskfile.yml) for all available commands

### Generating API tokens

To generate a new API token, run:

```bash
dotrun exec flask token create test
```

To list all the API tokens, run:

```bash
dotrun exec flask token list
```
