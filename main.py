import os, time, json, base64
from fastapi import FastAPI, BackgroundTasks
import jwt, requests

APP_ID = int(os.environ['GITHUB_APP_ID'])
INSTALLATION_ID = os.environ['GITHUB_INSTALLATION_ID']
PRIVATE_KEY_PATH = os.environ['GITHUB_APP_PEM']
ORG = os.environ['GITHUB_ORG']
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/repos')
METADATA_FILE = os.path.join(STORAGE_DIR, 'metadata.json')

app = FastAPI()

def load_private_key():
    with open(PRIVATE_KEY_PATH, 'r') as f:
        return f.read()

def make_jwt():
    now = int(time.time())
    payload = {'iat': now - 60, 'exp': now + (9*60), 'iss': APP_ID}
    return jwt.encode(payload, load_private_key(), algorithm='RS256')

def get_installation_token(jwt_token):
    url = f'https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens'
    headers = {'Authorization': f'Bearer {jwt_token}', 'Accept': 'application/vnd.github+json'}
    r = requests.post(url, headers=headers); r.raise_for_status()
    return r.json()['token']

def list_org_repos(token):
    url = f'https://api.github.com/orgs/{ORG}/repos?per_page=100'
    headers = {'Authorization': f'token {token}'}
    repos = []
    while url:
        r = requests.get(url, headers=headers); r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get('next', {}).get('url')
    return repos

def latest_commit_sha(token, owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    headers = {'Authorization': f'token {token}'}
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
        return json.load(open(METADATA_FILE))
    return {}

def save_metadata(m):
    with open(METADATA_FILE, 'w') as f:
        json.dump(m, f)

def refresh_challenge_db_task():
    jwt_token = make_jwt()
    token = get_installation_token(jwt_token)
    repos = list_orgs_repos(token)
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

@app.post("/refresh_challenge_db"):
async def refresh_challenge_db(background_tasks: BackgroundTasks):
    backgrond_tasks.add_task(refresh_challenge_db_task)
    return {"status": "refresh challenge db started"}
