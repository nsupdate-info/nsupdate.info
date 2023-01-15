# Build locally

1. Install `build` (see [docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives) for example via `pacman -S python-build` on ArchLinux
2. Afterwards run the command to generate pip packgases in `dist/`: `pyproject-build`

NOTE: This is also needed before development because the command generates `./src/nsupdate/_version.py`.

# Run locally

1. Create database using `python ./manage.py migrate`
2. Create a superuser with `python ./manage.py createsuperuser`
2. Run the server with `python ./manage.py runserver`
