import tempfile
from datetime import datetime, time, timedelta, timezone as datetime_timezone
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from account_auth.models import CustomUser

from .daily_scheduler import DailyScheduler


class DailySchedulerTests(SimpleTestCase):
	@timezone.override("UTC")
	def test_runs_job_once_when_due_and_again_on_next_day(self):
		runs = []
		scheduler = DailyScheduler()
		scheduler.register_daily_job("date reminders", lambda: runs.append("run"), time(9, 0))
		first_day_before_due = datetime(2026, 10, 20, 8, 59, tzinfo=datetime_timezone.utc)
		first_day_due = datetime(2026, 10, 20, 9, 0, tzinfo=datetime_timezone.utc)
		first_day_later = datetime(2026, 10, 20, 12, 0, tzinfo=datetime_timezone.utc)
		next_day_due = datetime(2026, 10, 21, 9, 0, tzinfo=datetime_timezone.utc)

		scheduler._run_due_jobs(first_day_before_due)
		self.assertEqual(runs, [])

		scheduler._run_due_jobs(first_day_due)
		scheduler._run_due_jobs(first_day_later)
		self.assertEqual(runs, ["run"])

		scheduler._run_due_jobs(next_day_due)
		self.assertEqual(runs, ["run", "run"])

	@timezone.override("UTC")
	def test_seconds_until_next_job_uses_supplied_scheduler_time(self):
		scheduler = DailyScheduler()
		scheduler.register_daily_job("date reminders", lambda: None, time(13, 0))
		now = datetime(2026, 10, 20, 12, 0, tzinfo=datetime_timezone.utc)

		self.assertEqual(scheduler._seconds_until_next_job(now), 3600)

		scheduler.jobs[0]["last_run_date"] = now.date()
		self.assertEqual(
			scheduler._seconds_until_next_job(now),
			int(timedelta(days=1, hours=1).total_seconds()),
		)


class InstanceBackupFilenameTests(TestCase):
	def test_filename_has_date_and_time(self):
		admin = CustomUser.objects.create_superuser(username="admin", password="StrongPassword!123")
		client = APIClient()
		client.force_login(admin)
		now = datetime(2026, 11, 1, 15, 30, 12, tzinfo=datetime_timezone.utc)

		with (
			tempfile.TemporaryDirectory() as data_dir,
			override_settings(DATA_DIR=data_dir),
			timezone.override("UTC"),
			patch("django.utils.timezone.now", return_value=now),
		):
			response = client.get("/api/instance-settings/backup/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response["Content-Disposition"],
			'attachment; filename="openinvento-instance-backup-2026-11-01-153012.zip"',
		)
