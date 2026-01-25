# Changelog

All notable changes to the Microbirding/SthlmBetong web app are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0-dev

**Date: In development**

Added species page with statistics on all observations, and styling of species names based on rarity.

### Fixed

- [ ] Fix issue with internal server error when observation data lacks "sex" attribute.
- [ ] Fix issue with missing left and right margins on mid-sized displays.
- [ ] Make text area on the Changelog page wider.

### Added

- [ ] Add species page that shows observation statistics for all observed species in the SthlmBetong geopolygon area.
- [ ] Add color and typographical styling of species names based on rarity classification, via file-based configuration.

### Miscellaneous

- [ ] Add support for downloading all observations up to the current time, within a given geopolygon area, and saving them in a local cache database.
- [ ] Add support for downloading all new and modified observations since the last download, and updating the local cache database. The schedule for downloading new and modified observations is configurable.
- [ ] Add support for generating rarity classification for species based on all observations in the cache database and according to a file-based configuration of classification rules. 
- [ ] Updated the personal data policy to reflect the above changes. No personal data processing is done with the personnel data in the observations in the cache.

## 0.1.2-dev

**Date: In development**

Refactor source-code directory structure.

### Miscellaneous

- [ ] Refactor source-code directory structure.

## 0.1.1

**Date: 2026-01-03**

Added tracking of selected date to see how users use that feature.

### Miscellaneous

- [x] Track selected date via Umami.

## 0.1.0

**Date: 2025-12-26**

The first proof-of-concept release.

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
