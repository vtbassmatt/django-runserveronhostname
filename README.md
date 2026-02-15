# Run Server on Hostname

My problem: I have multiple Django projects, but when I use the dev server (`./manage.py runserver`), they clobber each others' cookies since they run at 127.0.0.1 by default.

The manual solution: I set my hostfile (`/etc/hosts`) up so that each project has its own pseudo-hostname. Usually this is "projectname.localhost". But that means I have to remember which name I gave to each project _and_ remember to pass it every time I `./manage runserver`.

This package lets me define a desired dev server hostname in my Django settings, then `runserver` will respect it by default. If for any reason, I want to override that setting on a one-off basis, that still works.

## Installation

1. Install the `django-runserveronhostname` package using whatever package manager you prefer (I use `uv`).
2. Add `runserveronhostname` to `INSTALLED_APPS` in your Django settings.
3. Add a setting `RUNSERVER_ON = 'myname.whatever:8000'` (you must include a port number). This could also be used to bind to a particular IP address (`RUNSERVER_ON = '0.0.0.0:8000'`) if you prefer.

Important note: this package doesn't do anything about making sure you can actually bind to the requested name or IP address. You will need to manually add an entry to your hostfile, DNS, etc.

## Usage

When you run the dev server (`./manage.py runserver`, `django-admin runserver`, etc.), if you have `RUNSERVER_ON` defined, it'll use that. This works with any `runserver` implementation:
- naive implementation in Django
- `staticfiles` implementation in Django
- `daphne`'s runserver override
