# Device Disconnector

[![PyPI Downloads](https://static.pepy.tech/badge/device-disconnector)](https://pepy.tech/projects/device-disconnector)
![Release](https://img.shields.io/github/v/release/brainelectronics/device-disconnector?include_prereleases&color=success)
![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/brainelectronics/device-disconnector/branch/main/graph/badge.svg)](https://app.codecov.io/github/brainelectronics/device-disconnector)

Disconnect devices with REST calls to IP based Device Disconnector

---------------

## General

Disconnect devices with REST calls to IP based Device Disconnector

<!-- MarkdownTOC -->

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
  - [Setup](#setup)
  - [Testing](#testing)
  - [Changelog](#changelog)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Installation

```bash
[<PYTHON> -m] pip[3] install [--user] [--upgrade] device-disconnector
```

## Usage

The following commands turns USB port 3 and Switch pin 1 both on at the Device
Disconnector at `192.168.178.50`.

```bash
control-device \
  192.168.178.50 \
  usb3=on \
  switch1=on \
  -vvvv
```

## Contributing

### Setup

For active development you need to have `poetry` and `pre-commit` installed

```bash
python3 -m pip install --upgrade --user poetry pre-commit
git clone https://github.com/brainelectronics/device-disconnector.git
cd device-disconnector
pre-commit install
poetry install
```

### Testing

```bash
# run all tests
poetry run coverage run -m pytest -v

# run only one specific tests
poetry run coverage run -m pytest -v -k "test_parse_bool"
```

Generate the coverage files with

```bash
python create_report_dirs.py
poetry run coverage run -m pytest -v --cov-report=html
```

The coverage report is placed at `reports/coverage/html/index.html`

### Changelog

The changelog format is based on [Keep a Changelog][ref-keep-a-changelog], and
this project adheres to [Semantic Versioning][ref-semantic-versioning].

Please add a changelog snippet, see below, for every PR you contribute. The
changes are categorised into:

- `bugfixes` fix an issue which can be used out of the box without any further
changes required by the user. Be aware that in some cases bugfixes can be
breaking changes.
- `features` is used to indicate a backwards compatible change providing
improved or extended functionalitiy. This does, as `bugfixes`, in any case
not require any changes by the user to keep the system running after upgrading.
- `breaking` creates a breaking, non backwards compatible change which
requires the user to perform additional tasks, adopt his currently running
code or in general can't be used as is anymore.

The scope of a change shall either be:
- `internal` if no new deployment is required for this change, like updates in
the documentation for example
- `external` or `all` if this change affects the public API of this package or
requires a new tag and deployment for any other reason

The changelog entry shall be short but meaningful and can of course contain
links and references to other issues or PRs. New lines are only allowed for a
new bulletpoint entry. Usage examples or other code snippets should be placed
in the code documentation, README or the docs folder.

The name of the snippet shall be `<ISSUE_ID.md>`

```bash
[poetry run] changelog-generator \
    create .snippets/1.md
```

## Credits

A big thank you to the creators and maintainers of [SemVer.org][ref-semver]
for their documentation and [regex example][ref-semver-regex-example]

<!-- Links -->
[ref-keep-a-changelog]: https://keepachangelog.com/en/1.0.0/
[ref-semantic-versioning]: https://semver.org/spec/v2.0.0.html
[ref-semver]: https://semver.org/
[ref-semver-regex-example]: https://regex101.com/r/Ly7O1x/3/
