# Twitter Scheduler
Helps with managing when tweets are sent.
The main feature is scheduling of tweets.
The focus is to provide basic features with the ability to add on features in the future.

# Dependencies
- python 3.6
- postgres
- twitter api key
- celery 4
- rabbitmq

# Setup
- <code>> git clone https://github.com/caleblogan/twitter-scheduler.git</code>
- <code>> cd twitter-scheduler</code>
- create and activate virtualenv
- <code>> pip install -r requirement.txt</code>
- <code>> docker-compose up</code>
- <code>> python manage.py runserver</code>
