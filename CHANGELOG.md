# Changelog for microbirding

All notable changes to the webapp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is used by the main build script (currently [this Github actions file](https://github.com/pacoispaco/microbirding/blob/main/.github/workflows/cicd-dev.yml), which will extract the release version number in the first "double hashmark title" with square brackets at the top of this Markdown-file. It will use that to tag the built Docker image with the extracted release version number and the latest git commit sha. It will also create a **version tag file**  containing that tag, and include that in the Docker image so the app can show the build version.

## [unreleased]

The first proof-of-concept prototype release.

### Added

- [x] Main app page shows observations from Artportalen, for today and within the SthlmBetong geopolygon area.
- [x] Show basic information on each observation.
- [x] Include links to observation in Artportalen.
- [x] Navigate to previous and next days observations.
- [x] Dark mode.
- [ ] Handle Artportalens status code 429 (Too many requests).
- [ ] Responsive layout for smaller (mobile) screens.
- [ ] Map showing the geographical extent of SthlmBetong on the "Karta" page.
- [ ] Short description of the app and personal data policy on the "Om" page.
- [ ] Simple content for the "Obsar", "Listor", "Karta" and "Om" pages.
