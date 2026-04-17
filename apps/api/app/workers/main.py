"""Worker entrypoint for background jobs."""

from app.workers.reminder_jobs import run_due_reminder_scan

if __name__ == "__main__":
    created = run_due_reminder_scan()
    print(f"Orbis worker ran reminder scheduling scan. created_events={created}")
