# occpm
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Source code for our project «Object-Centric Comparative Process Mining» in the «Process Discovery Using Python» lab offered at RWTH Aachen University in WS21.

# Installation

## Environment
When using conda you can create an environment from the provided `environment.yml` by:
```
$ conda env create -f environment.yml
$ conda activate occpm
```
If any dependency is missing please add it and only it to `environment.yml` without specifying a version number and please **do not** use `conda env export > environment.yml` since one should avoid hard references to specific package versions unless explicitly necessary.

### Static environment
If the environment created from `environment.yml` does not work you can try using `environment_static.yml`(which was created using `conda env export > environment_static.yml`) to obtain an environment with the exact versions used during development, however this is not guaranteed to work across OS's and if possible one should not use out-of-date versions of packages.

# Running the server
To run the application execute:
```
$ python manage.py runserver 0.0.0.0:8000 
```

# Development
## Migrate
To properly configure the databases behind django whenever the `INSTALLED_APPS` are changed, the following command should be executed
```
python manage.py migrate
``` 

## Code style & Hooks
This project uses [black](https://github.com/psf/black)'s code styling. It is included as a dependency in the provided environment and can be run using:
```
black .
```
Alternatively if you want to avoid the hassle of remembering to run black all the time a pre-commit configuration is provided as well, which will run *black* before every commit. You can enable this configuration using:
```
pre-commit install
```
