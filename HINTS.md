# Open Source Prospector #
## File layout ##
This project follows the standard Openshift v2 layout as per the
[Django Openshift example](https://github.com/openshift/django-example).

In the root directory, some noteworthy items are:

- `libs/`: bundled versions of third-party libraries, mostly submodules
- `.openshift/`: hook scripts for deployment on Openshift
- `scripts/`: convenience scripts, not really used any more since their
  functionality have been moved into Django management commands.
- `wsgi/`: WSGI application and Django project.

Client-side resources such as Javascript and CSS files are organized inside the
individual apps' `static/` directories, under `static/js/` and `static/css/`
respectively.

The `static/js/` files are further organized by the view which uses them, with
the common files being in outer directories.


## Architecture ##
The Prospector project is built around the Django framework, making
extensive use of the Django ORM for all DB access, and for the frontend bits.

The Open Source Prospector consists of three main components, all of which talk
directly to the database.

- Django ORM models
- Frontend
- Metric calculation
- Importers

Configuration is done via auto-generated `django.contrib.admin` applications.


### Django ORM models ###
The database models are distributed among the Django apps by function.

- `btinfo`: Bug tracker metadata + imported information
- `cveinfo`: CPE metadata + imported CVE information
- `gtrendsinfo`: Google Trends queries + datapoints
- `jamiqinfo`: JamiQ topics + datapoints
- `mlinfo`: Mailing list metadata + imported information
- `participantinfo`: Participant/Contributor imported information
- `projectinfo`: Metadata on basic projects
- `vcsinfo`: VCS repository information
- `hmeter_frontend`: Aggregated information linking the models from individual
  projects and their respective resources from the `*info` apps.


### Frontend ###
The frontend code can be found in the `hmeter_frontend` Django app, which is
located in `wsgi/healthmeter/hmeter_frontend/`.

There are three main user-visible views:

- `hmeter_frontend.views.project.ProjectIndex`:
  The main project view, with URL `http://example.com/project/`. This view uses
  Client-side Javascript files are in
  `wsgi/healthmeter/hmeter_frontend/static/js/project/index`, and styles in
  `wsgi/healthmeter/hmeter_frontend/static/css/project-index.css`

- `hmeter_frontend.views.project.ProjectDetail`: The detailed project report,
  with URL `http://example.com/project/$id/`. This view is rendered according to
  the layout of the `Metric` tree as configured in the database by combining
  `hmeter_frontend/project/fragments/detail/sections/*` template fragments as
  per the configured `Metric.template_name` field.

- `hmeter_frontend.views.project.CompareProject`: Project comparison page, with
  URL `http://example.com/project/$comma_separated_ids`.


### Metric Calculation ###
The metric calculation portion is set up in `hmeter_frontend/metrics/`, with the
entry-point currently being in `hmeter_frontend.models.Metric.score_project`.

Each metric algorithm, as referenced by the `Metric.algorithm.name` field, can
be found in `hmeter_frontend.metrics.algorithms.*`, registered onto a `dict`
object in `hmeter_frontend.metrics.lookup`.

The metric algorithms follow a similar structure to the Django Class Based
Views, where each algorithm is a class that is constructed once per metric
calculation.


### Importers ###
The importers are implemented in `*.importers.`, with corresponding management
commands defined in `*.management.commands.update_*` for easy shell-based
invocation.

