import os.path as op

from crontab import CronTab


def setup_cron():
    cron  = CronTab(user=True)

    curr_dir = op.realpath(op.dirname(__file__))
    poll_path = op.realpath(op.join(curr_dir, "..", "bin", "poll_dota_lounge.py"))
    log_dir = op.realpath(op.join(curr_dir, ".."))

    cmd = 'python {} 2>&1 >> {}/log/cron.log'.format(poll_path, log_dir)

    cron.remove_all(command=cmd)
    cron.remove_all()

    job = cron.new(command=cmd, comment="Poll dota lounge for new match betting data.")

    job.minute.every(1)
    job.enable()

    cron.write()
