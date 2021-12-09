# occpm

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Source code for our project «Object-Centric Comparative Process Mining» in the «Process Discovery Using Python» lab offered at RWTH Aachen University in WS21.

# Installation

## Using Docker
The code comes with a Dockerfile to build and run the application inside a [docker](https://www.docker.com/) container
To build the container run
```
docker build --rm -t occpm:latest .
```
After the container is build the webapp can be run using
```
docker run -p 8000:8000 occpm
```
## Manual Install
### Environment

When using conda you can create an environment from the provided `environment.yml` by:

```
$ conda env create -f environment.yml
$ conda activate occpm
```

If any dependency is missing please add it and only it to `environment.yml` without specifying a version number and please **do not** use `conda env export > environment.yml` since one should avoid hard references to specific package versions unless explicitly necessary.

#### Static environment

If the environment created from `environment.yml` does not work you can try using `environment_static.yml`(which was created using `conda env export > environment_static.yml`) to obtain an environment with the exact versions used during development, however this is not guaranteed to work across OS's and if possible one should not use out-of-date versions of packages.

### Running the server

To run the application execute:

```
$ python manage.py runserver
```

# Development

## Migrations

To properly configure the databases behind django whenever the `INSTALLED_APPS` or models of apps are changed, the following commands should be executed

```
python manage.py makemigrations
python manage.py migrate
```

## Updating the environment

When one wants to update the environment, either because some packages were added, or just to get the newest versions of packages without recreating the environment execute:

```
conda env update --file environment.yml --prune
```

## Code style & Hooks

This project uses [black](https://github.com/psf/black)'s code styling. It is included as a dependency in the provided environment and can be run using:

```
black .
```

Alternatively if you want to avoid the hassle of remembering to run black all the time a pre-commit configuration is provided as well, which will run _black_ before every commit. You can enable this configuration using:

```
pre-commit install
```
