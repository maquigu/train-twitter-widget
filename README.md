BayesTwitterWidget
==================

For a live demo go to: http://socialwest.stanford.edu/california-water/
<br>
This project has the following dependencies:
- Python Celery
- RabbitMQ for Celery AMQP backend
- A working SSL setup (can be off-loaded to nginx)
- Python Tornado web server

<br>
This project is comprised of three components:
- A client for the Twitter REST API which is run as a celery worker (tasks.py)
- A websocket server (under handlers)
- A javascript client (under static/js)
