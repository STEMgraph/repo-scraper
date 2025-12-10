# Repo-Scraper

A prototype solution to skim through all public repositories of an organizatioin and get all updated README.mds.

## Setup

### ... locally for development and testing purposes

- Clone this repository to your local workstation.
- Create a folder called `secrets` in your local working directory.
- Create a GitHub Personal Access Token and store it as plain text in `secrets/github.pat`.
- Copy `env-template` to `.env`.
- In the `.env` file, enter the value for `GITHUB_ORG`. This will be the Organization / Owner whose public repositories are getting scraped.
- Run `docker compose up --build`.

The API is now up and running at `http://localhost:8080/docs`.
