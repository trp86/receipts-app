# GitHub Actions Workflows

## ETL Sync Workflow

**File:** `etl-sync.yml`

**Schedule:** Every hour (0 * * * *)

**What it does:**
- Calls `/api/admin/run-etl` endpoint on Render backend
- Syncs unsynced receipts from Neon to MotherDuck
- Runs automatically in the background

---

## Manual Trigger

You can manually trigger the ETL sync:

1. Go to: https://github.com/trp86/receipts-app/actions
2. Select "ETL Sync - Neon to MotherDuck"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

---

## Schedule Options

Current: **Every hour**
```yaml
cron: '0 * * * *'
```

### Other Options:

**Every 30 minutes:**
```yaml
cron: '*/30 * * * *'
```

**Every 6 hours:**
```yaml
cron: '0 */6 * * *'
```

**Every day at midnight UTC:**
```yaml
cron: '0 0 * * *'
```

**Every day at 9 AM UTC (11 AM CEST):**
```yaml
cron: '0 9 * * *'
```

---

## Monitoring

### View Workflow Runs:
https://github.com/trp86/receipts-app/actions

### Check ETL Logs:
- Click on a workflow run
- Click "sync-receipts" job
- View logs

### Success Indicators:
- ✅ Green checkmark on workflow run
- "ETL sync completed successfully" in logs
- "X receipts synced" in response

---

## Troubleshooting

### Workflow fails with 500 error:
- Check Render backend is running
- Check MotherDuck token is valid
- View Render logs for errors

### Workflow runs but no receipts synced:
- All receipts may already be synced
- Check Neon DB: `SELECT COUNT(*) FROM receipts WHERE synced_to_dwh = FALSE`

### Workflow doesn't run:
- GitHub Actions must be enabled in repo settings
- Check: Settings → Actions → General → Allow all actions

---

## Cost

GitHub Actions is **free** for public repos and includes:
- 2,000 minutes/month for private repos
- Unlimited for public repos

This workflow uses ~30 seconds per run = ~15 minutes/day = negligible cost.

---

## Disable/Modify Schedule

To change schedule, edit `.github/workflows/etl-sync.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Change this line
```

To disable, either:
1. Delete the `etl-sync.yml` file
2. Or comment out the schedule section
