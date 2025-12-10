# Repo-Scraper

A prototype solution to skim through all public repositories of an organizatioin and get all updated README.mds.

## Setup

### ... locally for development and testing purposes

- Clone this repository to your local workstation.
- Create a folder called `secrets` in your local working directory.
- Create and install a GitHup-App in your Github account. (see below)
- Generate a private key (.pem) in the App and download it as `readmefetcher.private-key.pem` into your `secrets` folder.
- Copy `env-template` to `.env`.
- In the `.env` file, enter the values for `GITHUB_APP_ID`, `GITHUB_INSTALLATION_ID` and `GITHUB_ORG`.
- Run `docker compose up --build`.

The API is now up and running at `http://localhost:8080/docs`.

### Creating the GitHub-App

- Go to **Settings -> Developer Settings -> GitHub Apps -> New GitHub App**
- Fill in:
  - **Name**: e.g. ReadmeFetcher
  - **Homepage URL**: any placeholder (not used here)
  - **Callback URL**: leave blank
  - **Webhook**: mark as not **Active**
- **Permissions**:
  - Repository: **Contents** Read-only
  - Repository: **Metadata** Read-only
- Install the app into **your** account.
- Find:
  - `GITHUB_APP_ID` as **App ID** under **General -> About**.
  - `GITHUB_INSTALLATION_ID`: Under **Install App**, enter the settings (the cogwheel icon). You are redirected to `https://github.com/settings/installations/<installation_id>`. The number at the end of the URL is the **Installation ID**.
