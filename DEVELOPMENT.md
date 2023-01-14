# Dependency management

Get [Pipenv](https://pipenv.pypa.io/en/latest/installation/) and checkout the [Pipenv Command reference](https://pipenv.pypa.io/en/latest/commands/)

## Install new dependencies

https://pipenv.pypa.io/en/latest/commands/#install

```
pipenv install mypkg
```

## Spawn a shell with correct python paths

```
pipenv shell
```

Exit the shell with `exit`

## Dependency maintenance

### Update requirements.txt files including transitive dependencies

```
pipenv update
```

NOTE: This is not done today and only a suggestion.

```
pipenv requirements --exclude-markers > requirements.d/all.txt
pipenv requirements --exclude-markers --dev-only > requirements.d/dev.txt
```

Verify the updated dependencies don't include any security vulnerabilities

```
pipenv check
```

# Build locally

1. Install `build` (see [docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives) for example via `pacman -S python-build` on ArchLinux
2. Afterwards run the command to generate pip packgases in `dist/`: `pyproject-build`

NOTE: This is also needed before development because the command generates `./src/nsupdate/_version.py`.

# Run locally

1. Install dependencies `pipenv install --dev`
2. Generate `src/nsupdate/_version.py` file by running `pyproject-build`
2. Create database using `pipenv run ./manage.py migrate`
3. Create a superuser with `pipenv run ./manage.py createsuperuser`
4. Run the server with `pipenv run ./manage.py runserver`

# Lint

Run [pylint](https://pylint.readthedocs.io/en/stable/) in error-only mode to check any problems: `pipenv run pylint src/nsupdate`

NOTE: The project does not use pylint for formatting. Disabling the `errors-only` mode in `.pylintrc` will show a lot of warnings.

# Run tests

Tests need to run inside Docker because they depend on specific bind9 config on 127.0.0.1:53.

1. Build the docker image using: `docker build -t nsupdate scripts/docker/` once
2. Then run tests via `docker run --dns 127.0.0.1 -v $PWD:/app nsupdate`