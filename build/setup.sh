#!/usr/bin/bash

#Quit on error.
set -e
# Treat undefined variables as errors.
set -u


function main {
    local uwsgi_uid="${1:-}"
    local uwsgi_gid="${2:-}"

    # Change the uid
    if [[ -n "${uwsgi_uid:-}" ]]; then
        usermod -u "${uwsgi_uid}" www-data
    fi
    # Change the gid
    if [[ -n "${uwsgi_gid:-}" ]]; then
        groupmod -g "${uwsgi_gid}" www-data
    fi

    # Setup permissions on the run directory where the sockets will be
    # created, so we are sure the app will have the rights to create them.

    # Set owner.
    chown www-data:www-data /var/run/uwsgi
    # Set permissions.
    chmod u=rwX,g=rwX,o=--- /var/run/uwsgi

    # Set app folder permissions
    chown -R www-data:www-data /nsupdate
    chown -R www-data:www-data /static
    chown -R www-data:www-data /upload

}


main "$@"
