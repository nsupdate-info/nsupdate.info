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
