# GitHub Copilot custom instructions for assistant_core contributors
# This file provides guidance to GitHub Copilot (and human reviewers) about
# repository conventions and PR requirements.

project: assistant_core

instructions:
  - When suggesting code changes or PR descriptions, ensure the contributor adds
    a concise CHANGELOG.md entry under the NEXT section that explains what
    changed and why.

  - Remind contributors to follow `CONTRIBUTING.md`:
    - Run tests and add tests for behavior changes.
    - Run formatters and linters (make format / make lint).
    - Update documentation where applicable.

  - If the suggestion touches public APIs or behavior, encourage adding
    typed signatures and small unit tests.
