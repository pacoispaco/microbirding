# Release instructions

The CI/CD-pipeline is currently set up so that it triggers a build of Docker image on:
* push to main (development images), and
* push of tags (release or release candidates).
And the CI/CD-pipeline build will fail if the git tag isn't a valid sematic versioning tag.

Checklist for every release:
- [ ] Decide on what the release is about features and bug fixes.
- [ ] Decide on semantic version of the release.
- [ ] Update the CHANGELOG.md file with info on the release.
- [ ] Create an annotated tag in git. You can begin with format `M.m.p-rc.1` for release candidate 1. Push the tag to the GitHub origin to trigger a build. Example: `git tag -a 0.1.0-rc.1 -m "Release candidate for the first release"` and then `git push origin tag 0.1.0-rc.1`.
- [ ] Install in development and/or pre-prod environment. Do acceptance testing. If needed; do fixes and tag and release more release candidates, until you are ready for the release.
- [ ] Create an annotated tag in git with format `M.m.p`. Push the tag to GitHub origin to trigger a build. Example: `git tag -a 0.1.0 -m "First release"` and then `git push origin tag 0.1.0`.
- [ ] Create a release in GitHub and add the contents from CHANGELOG.md for the specific release. Note that this doesn't trigger another build.
