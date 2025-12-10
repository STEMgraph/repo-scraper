import os, time, json, base64
from fastapi import FastAPI, BackgroundTasks
import requests

ORG = os.environ['GITHUB_ORG']
PAT_FILE = os.environ['GITHUB_PAT_FILE']
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/repos')
METADATA_FILE = os.path.join(STORAGE_DIR, 'metadata.json')

app = FastAPI()

def get_pat():
    with open(PAT_FILE, 'r') as f:
        return f.read().strip()

def list_org_repos(token):
    url = f'https://api.github.com/orgs/{ORG}/repos?per_page=100'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    repos = []
    while url:
        r = requests.get(url, headers=headers); r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get('next', {}).get('url')
    return repos

def latest_commit_sha(token, owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers); r.raise_for_status()
    return r.json()['sha']

def fetch_readme(token, owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/readme'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return base64.b64decode(data['content']).decode('utf-8')

def ensure_metadata():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE) as f:
            return json.load(f)
    return {}

def save_metadata(m):
    with open(METADATA_FILE, 'w') as f:
        json.dump(m, f)

def sync_readme_task():
    token = get_pat()
    repos = list_org_repos(token)
    meta = ensure_metadata()
    for r in repos:
        owner, name, branch = r['owner']['login'], r['name'], r['default_branch']
        sha = latest_commit_sha(token, owner, name, branch)
        if meta.get(name, {}).get('sha') != sha:
            readme = fetch_readme(token, owner, name)
            if readme:
                filename = os.path.join(STORAGE_DIR, f'{name}__{sha}.md')
                tmp = filename + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    f.write(readme)
                os.replace(tmp, filename)
                meta[name] = {'sha': sha, 'downloaded_at': int(time.time()), 'path': filename}
    save_metadata(meta)

@app.post("/sync_readme")
async def sync_readme(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_readme_task)
    return {"status": f"synchronizing README.md files from {ORG} started"}
