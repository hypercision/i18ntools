# Deploying a New Version

When we are ready to release a new version of the i18ntools package, we update the version number in [pyproject.toml](https://github.com/hypercision/i18ntools/blob/481a33fcd069b4f35c7293ac082f7115f6b28432/pyproject.toml#L3),
commit the change on the `main` branch, and push the commit to GitHub.

Then we push a new tag to GitHub i.e. `v0.1.0`. This will trigger a GitHub actions workflow to publish the package to the [Python Package Index (PyPI)](https://pypi.org/project/i18ntools/).

Then we create a new [release in GitHub](https://github.com/hypercision/i18ntools/releases):
- Click "Draft a new release"
- Title the release the new version number i.e. "v0.1.0"
- Click "Choose a tag" and enter the newly created tag.
- Then click "Publish release"
