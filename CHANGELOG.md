# Changelog

All notable changes to the Microbirding/SthlmBetong web app are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.0.1-dev

**Date: 2025-10-04**

The first proof-of-concept prototype release.

### Added

- [ ] Add short description of the app and personal data policy on the "Om" page.
- [ ] Add Map showing the geographical extent of SthlmBetong on the "Karta" page.
- [ ] Add simple content for the "Obsar", "Listor", "Karta" and "Om" pages.
- [x] Fix responsive layout for smaller (mobile) screens.
- [x] Show version info and changelog.
- [x] Add dark mode.
- [x] Add navigation to previous and next days observations.
- [x] Include links to each observation in Artportalen.
- [x] Show basic information on each observation.
- [x] Add main app page that shows observations from Artportalen, for today and within the SthlmBetong geopolygon area.

### Fixed

- [x] Handle Artportalens HTTP status code 429 (Too many requests). Implemented a retry scheme with a maximum of 5 retries and exponential backoff. But response times for the app starts to degrade after just 20+ simultaneous users, due to the rate limiting of Artportalens API. Eventually we will need to implement a local cache for better response times.

### Miscellaneous

- [x] Set up reasonably good logging.
- [x] Set up server with [Docker](https://www.docker.com/), [Portainer](https://www.portainer.io/) and [Traefik](https://traefik.io/traefik) for running a public dev environment with [Let's encrypt](https://letsencrypt.org/) certificates, on [DigitalOcean](https://www.digitalocean.com/).
- [x] Write a Dockerfile for the web app.
- [x] Set up application code structure and a CI/CD-pipeline.
- [x] Decide on tech stack for web app; [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [HTMX](https://htmx.org/), [TailwindCSS](https://tailwindcss.com/) and [Docker](https://tailwindcss.com/).
- [x] Implement a simple CLI-program for trying out the Artportalen API:s.
- [x] Fix a geopolygon for the SthlmBetong area.
- [x] Set up [Github](https://github.com/) repo.
- [x] Register a developer account and obtain [API keys from Artportalen](https://api-portal.artdatabanken.se/).
