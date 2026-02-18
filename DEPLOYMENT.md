# Deployment Guide: Render + Supabase (Free Tier)

This guide provides step-by-step instructions to deploy your SaaS application using a 100% free stack.

## 1. Database (Supabase)
1. Go to [Supabase](https://supabase.com/) and create a new project.
2. Navigate to **Project Settings** -> **Database**.
3. Under **Connection string**, select **URI**.
4. Copy the string. It should look like `postgresql://postgres.[ID]:[PASSWORD]@...`
5. Note: SQLAlchemy handles the `postgres://` vs `postgresql://` conversion automatically now.

## 2. Hosting (Render)
1. Connect your GitHub repository to [Render](https://render.com/).
2. Click **New +** -> **Blueprint**.
3. Select your repository. 
4. Render will automatically detect the `render.yaml` file and promp you to approve the services (Web, Worker, DB, Redis).
5. **Note**: If you want to use Supabase instead of Render's built-in DB, you can skip the DB creation in the blueprint and manually add the `DATABASE_URL` env var to the Web/Worker services.

## 3. Environment Variables
Ensure the following are set in Render's dashboard (if not using the Blueprint's defaults):
- `DATABASE_URL`: Your Supabase URI.
- `SECRET_KEY`: A long, random string.
- `FLASK_ENV`: set to `production`.

## 4. Static Files
The app is configured with **WhiteNoise**, so static files (CSS, JS, Images) will be served directly by Gunicorn without needing a separate CDN for the free tier.

## 5. Background Tasks
Render will spin up a separate **Worker** service for Celery. This service is also on the free tier. 
- Web: Serves the UI/API.
- Worker: Processes recurring invoices and emails.

## 6. Verification
Once deployed, verify the health status:
`https://your-app-name.onrender.com/health`
Should return: `{"status": "ok", "db": "ok", "redis": "ok"}`
