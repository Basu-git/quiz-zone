# Quiz Zone

Online MCQ quiz platform. Two pages (`index.html`, `quiz.html`), FastAPI backend, PostgreSQL (Supabase), deployed on AWS EC2 with Nginx + Uvicorn.

## Run locally
```bash
cd quiz-zone
python3 -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env          # then edit DATABASE_URL (leave it out to use a local SQLite file)
cd backend
python seed.py                # loads 5 quizzes / 25 questions
python test_api.py            # optional automated backend test
uvicorn main:app --reload
```
Open http://127.0.0.1:8000 (API docs: /docs). Do not open the HTML files by double-clicking; use the URL above.

## Supabase setup
1. supabase.com -> New project (free tier). Save the database password.
2. Project -> Connect -> **Session pooler** connection string (IPv4 compatible; the direct connection is IPv6-only and fails on most EC2 setups).
3. Put it in `.env` as `DATABASE_URL=postgresql://...`.
4. Tables are created automatically on first start. `deploy/schema.sql` is the same SQL if you prefer the Supabase SQL Editor.
5. Run `python seed.py` once.

## GitHub
```bash
git init && git add . && git commit -m "Quiz Zone"
git branch -M main
git remote add origin https://github.com/<you>/quiz-zone.git
git push -u origin main
```
Check that `.env` is NOT in the repo (it is in `.gitignore`).

## AWS EC2 deployment
1. **Account**: aws.amazon.com -> Create account (card + phone verification needed). Choose a region near you (e.g. Asia Pacific (Mumbai) ap-south-1).
2. **Free tier / pricing**: accounts created after 15 Jul 2025 get a credit-based free plan (credits, time-limited); older accounts get 750 h/month of t2/t3.micro for 12 months. Check Billing -> Free Tier and the pricing page for your account. A t3.micro costs roughly $0.01/hour on-demand, plus a public IPv4 address (~$0.005/hour).
3. **Launch instance**: EC2 -> Launch instance -> name `quiz-zone`, AMI **Ubuntu Server 24.04 LTS**, type **t3.micro** (or t2.micro if marked free-tier eligible), create a key pair (.pem), storage 8-10 GB gp3.
4. **Security group** inbound rules: SSH (22) from *My IP*; HTTP (80) from 0.0.0.0/0. Do NOT open port 8000.
5. **SSH**: `chmod 400 key.pem && ssh -i key.pem ubuntu@<EC2_PUBLIC_IP>` (on Windows use PowerShell, same command).
6. **Install**:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv git nginx
   ```
7. **Get code**: `git clone https://github.com/<you>/quiz-zone.git && cd quiz-zone`
8. **Dependencies**:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
9. **Env vars**: `cp .env.example .env && nano .env` -> paste the Supabase Session pooler URL.
10. **Seed**: `cd backend && python seed.py && cd ..`
11. **Test Uvicorn**: `cd backend && uvicorn main:app --host 127.0.0.1 --port 8000` (Ctrl+C to stop).
12. **systemd**:
    ```bash
    sudo cp deploy/quizzone.service /etc/systemd/system/quizzone.service
    sudo systemctl daemon-reload && sudo systemctl enable --now quizzone
    sudo systemctl status quizzone      # should say active (running)
    ```
13. **Nginx**:
    ```bash
    sudo cp deploy/nginx.conf /etc/nginx/sites-available/quizzone
    sudo ln -sf /etc/nginx/sites-available/quizzone /etc/nginx/sites-enabled/quizzone
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl restart nginx
    ```
14. **Test**: open `http://<EC2_PUBLIC_IP>` in a browser. Logs: `sudo journalctl -u quizzone -f`.

Updating later: `cd ~/quiz-zone && git pull && sudo systemctl restart quizzone`.

### Avoiding charges / cleanup
- Set a budget alert: Billing -> Budgets -> create a $1-$5 budget with email alerts.
- Stop the instance when not demoing (stopped = no compute charge, but storage is still billed and the public IP changes on restart).
- When finished: EC2 -> Instances -> select -> **Terminate**; then Elastic IPs (release any), Volumes (delete leftovers), and key pairs if unwanted. Pause/delete the Supabase project if no longer needed.
- Check Billing dashboard the next day to confirm zero running resources.

## Architecture (for viva)
Browser -> Nginx (port 80, reverse proxy) -> Uvicorn/FastAPI (127.0.0.1:8000) -> SQLAlchemy -> Supabase PostgreSQL.
- `index.html` fetches `GET /api/quizzes` and renders quiz cards.
- `quiz.html?id=N` fetches quiz info + shuffled questions (no answers), runs the timer, and POSTs selected answers to `/api/quizzes/N/submit`.
- The backend compares answers with `questions.correct_answer`, computes the score, saves a row in `quiz_attempts`, and returns the result + review. The browser only displays it.
- Pydantic validates input (A-D only, size limits); SQLAlchemy uses parameterised queries (no SQL injection); output is HTML-escaped (no XSS); credentials live in `.env`.
