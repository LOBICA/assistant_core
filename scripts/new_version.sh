#!/usr/bin/env bash

set -euo pipefail

usage() {
	echo "Usage: $0 <patch|minor|major|x.y.z>"
	exit 2
}

if [ "$#" -ne 1 ]; then
	usage
fi

NEW_VERSION_ARG=$1

# ensure git working tree is clean
if [ -n "$(git status --porcelain)" ]; then
	echo "Error: working tree is not clean. Commit or stash your changes before releasing." >&2
	git status --porcelain
	exit 1
fi

echo "Running format, lint and tests before bumping version..."
poetry run make format
poetry run make lint
poetry run make test

echo "Bumping version: $NEW_VERSION_ARG"
poetry version "$NEW_VERSION_ARG"

# Capture the new version string (poetry prints it in stdout)
NEW_VERSION=$(poetry version --short)

echo "Expecting CHANGELOG.md to contain an entry for v$NEW_VERSION"
if ! grep -q "## v$NEW_VERSION" CHANGELOG.md; then
	echo "Error: CHANGELOG.md does not contain a header '## v$NEW_VERSION'. Please add release notes before running this script." >&2
	exit 1
fi

git add pyproject.toml CHANGELOG.md
echo "Committing version bump"
git commit -m "Bump version to v$NEW_VERSION"

echo "Creating annotated tag v$NEW_VERSION"
git tag -a -m "Release v$NEW_VERSION" "v$NEW_VERSION"

echo "Pushing commits and tags"
git push origin --follow-tags

echo "Done. Released v$NEW_VERSION"
