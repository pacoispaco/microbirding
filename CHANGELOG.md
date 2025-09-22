# Changelog

All notable changes to the webapp are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1-unreleased]

The first proof-of-concept prototype release.

### Added

- [ ] Short description of the app and personal data policy on the "Om" page.
- [ ] Simple content for the "Obsar", "Listor", "Karta" and "Om" pages.
- [ ] Map showing the geographical extent of SthlmBetong on the "Karta" page.
- [ ] Handle Artportalens status code 429 (Too many requests).
- [ ] Responsive layout for smaller (mobile) screens.
- [x] Show version info and changelog.
- [x] Dark mode.
- [x] Navigate to previous and next days observations.
- [x] Include links to observation in Artportalen.
- [x] Show basic information on each observation.
- [x] Main app page shows observations from Artportalen, for today and within the SthlmBetong geopolygon area.

### Miscellaneous

- [x] Set up reasonably good logging.
- [x] Set up server with Docker, Portainer and Traefik for running a public dev environment with Let's encrypt cetificates.
- [x] Write a Dockerfile for the web app.
- [x] Set up application code structure and a CI/CD-pipeline.
- [x] Decide on tech stack for web app; Python, FastAPI, HTMX, TailwindCSS and Docker.
- [x] Implement a simple CLI-program for trying out the Artportalen API:s.
- [x] Fix a geopolygon for the SthlmBetong area.
- [x] Set up Github repo.
- [x] Register a developer account and obtain API keys from Artportalen.
