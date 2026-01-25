# Changelog

All notable changes to the Microbirding/SthlmBetong web app are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.2

**Date: 2026-01-25**

Fix minor bug and refactor source code directory structure.

### Fixed

- [x] Fix [issue 11](https://github.com/pacoispaco/microbirding/issues/11) with internal server error when observation data lacks "sex" attribute.

### Miscellaneous

- [x] Refactor source-code directory structure for Python code.

## 0.1.1

**Date: 2026-01-03**

Add tracking of selected date to see how users use that feature.

### Miscellaneous

- [x] Track selected date via Umami.

## 0.1.0

**Date: 2025-12-26**

Release first proof-of-concept app.

### Fixed

- [x] Fix bug in display of sex icons.
- [x] Rewrite Tailwind CSS layout and tighten up layout on mobile.
- [x] Fix better background and header colors.
- [x] Handle Artportalens HTTP status code 429 (Too many requests). Implement a retry scheme with max 5 retries and exponential back-off. But response times for the app starts to degrade after just 20+ simultaneous users, due to the rate limiting of Artportalens API. Eventually I will need to implement a local cache for better response times.

### Added

- [x] Add short description of the app and a personal data policy on the "Om" page.
- [x] Add map showing the geographical extent of SthlmBetong on the "Karta" page.
- [x] Add 404 page.
- [x] Fix responsive layout for smaller (mobile) screens.
- [x] Show version info and changelog.
- [x] Add dark mode.
- [x] Add navigation to previous and next days observations.
- [x] Include links to each observation in Artportalen.
- [x] Show basic information on each observation.
- [x] Add main app page that shows observations from Artportalen, for today and within the SthlmBetong geopolygon area.

### Miscellaneous

- [x] Add hint coloring for DEV-environment.
- [x] Add analytics tracking with [Umami](https://umami.is/).
- [x] Set up reasonably good logging with log rotation and deletion.
- [x] Set up server with [Docker](https://www.docker.com/), [Portainer](https://www.portainer.io/) and [Traefik](https://traefik.io/traefik) for running a public development environment with [Let's encrypt](https://letsencrypt.org/) certificates, on [DigitalOcean](https://www.digitalocean.com/).
- [x] Write a Docker file for the web app.
- [x] Set up application code structure and a CI/CD-pipeline with [GitHub Actions](https://github.com/features/actions).
- [x] Decide on tech stack for web app; [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [HTMX](https://htmx.org/), [TailwindCSS](https://tailwindcss.com/) and [Docker](https://tailwindcss.com/). For maps I use [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/) and [OpenStreetMap](https://www.openstreetmap.org).
- [x] Implement a simple CLI-program for trying out the Artportalen API:s.
- [x] Fix a geopolygon for the SthlmBetong area.
- [x] Set up [GitHub](https://github.com/) repository.
- [x] Register a developer account and get [API keys from Artportalen](https://api-portal.artdatabanken.se/).
