# Guide on using django-crontab for scheduling jobs

1. Install django-crontab using ``make requirements``.
2. Create the job you want to run on a cadence under the folder `<appname>/cronjobs/`, where ``<appname>`` is the app that most closely relates to what your job does [(example)](https://github.com/omou-org/mainframe/blob/master/comms/cronjobs/example.py).
3. Add your job as well as the schedule you want to run the job on to the CRONJOBS list in `settings/__init.py` [(example)](https://github.com/omou-org/mainframe/blob/master/mainframe/settings/__init__.py#L191).
4. Run `make cronjobs` to reflect any changes made to the settings file on your system for testing. If you don't need to test locally, you can skip this step.

## How do I define a schedule?
You can use this [helper](https://crontab.guru/), or just google "crontab tutorial".

## Can I view logs of my jobs when testing locally?
Yes, you can include a redirect to a log file when defining your job, as shown in the example. Bear in mind you'll to first create the directory that the log file will be living in (`mkdir -p /tmp/mainframe/comms` for example) before it can write to it.

## I'm still running into issues or I have a different question!
Ping Jerry on Teams and I can help you out.
