# Self-hosted GitHub Actions runner (Python CI) for this Fedora machine.
#
# The base image already ships Ubuntu 26.04, Python 3.14, pip, venv, git,
# curl, jq, gcc and the GitHub runner itself. Add extra tooling below if a
# workflow needs it (nodejs, docker CLI, make, linters, ...).
FROM myoung34/github-runner:latest

USER root

# Fail the build early if the Python toolchain is missing or broken.
RUN python3 --version \
    && python3 -m venv /tmp/venv-smoke \
    && /tmp/venv-smoke/bin/python -m pip --version \
    && rm -rf /tmp/venv-smoke

# Keep the base image ENTRYPOINT/CMD: it registers the runner and starts it.
