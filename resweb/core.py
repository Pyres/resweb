from functools import wraps
from flask import Flask, g, redirect, request, Response
from pyres import ResQ, failure

from resweb.views import (
    Overview,
    Queues,
    Queue,
    Workers,
    Working,
    Failed,
    Stats,
    Stat,
    Worker,
    Delayed,
    DelayedTimestamp
)
from base64 import b64decode
app = Flask(__name__)
app.config.from_object('resweb.default_settings')
app.config.from_envvar('RESWEB_SETTINGS', silent=True)
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if app.config.get('BASIC_AUTH'):
        return username == app.config.get('AUTH_USERNAME') and password == app.config.get('AUTH_PASSWORD')
    else:
        return True

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print app.config.get('BASIC_AUTH')
        auth = request.authorization
        if app.config.get('BASIC_AUTH') and (not auth or not check_auth(auth.username, auth.password)):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.pyres = ResQ(app.config['RESWEB_HOST'], password=app.config.get('RESWEB_PASSWORD', None))

@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'pyres'):
        g.pyres.close()

@app.route("/")
@requires_auth
def overview():
    return Overview(g.pyres).render().encode('utf-8')

@app.route("/working/")
@requires_auth
def working():
    return Working(g.pyres).render().encode('utf-8')

@app.route("/queues/")
@requires_auth
def queues():
    return Queues(g.pyres).render().encode('utf-8')

@app.route('/queues/<queue_id>/')
@requires_auth
def queue(queue_id):
    start = int(request.args.get('start', 0))
    return Queue(g.pyres, queue_id, start).render().encode('utf-8')

@app.route('/failed/')
@requires_auth
def failed():
    start = request.args.get('start', 0)
    start = int(start)
    return Failed(g.pyres, start).render().encode('utf-8')

@app.route('/failed/retry/', methods=["POST"])
@requires_auth
def failed_retry():
    failed_job = request.form['failed_job']
    job = b64decode(failed_job)
    decoded = ResQ.decode(job)
    failure.retry(g.pyres, decoded['queue'], job)
    return redirect('/failed/')

@app.route('/failed/delete/', methods=["POST"])
@requires_auth
def failed_delete():
    failed_job = request.form['failed_job']
    job = b64decode(failed_job)
    failure.delete(g.pyres, job)
    return redirect('/failed/')

@app.route('/failed/delete_all/')
@requires_auth
def delete_all_failed():
    #move resque:failed to resque:failed-staging
    g.pyres.redis.rename('resque:failed', 'resque:failed-staging')
    g.pyres.redis.delete('resque:failed-staging')
    return redirect('/failed/')


@app.route('/failed/retry_all')
@requires_auth
def retry_failed(number=5000):
    failures = failure.all(g.pyres, 0, number)
    for f in failures:
        j = b64decode(f['redis_value'])
        failure.retry(g.pyres, f['queue'], j)
    return redirect('/failed/')

@app.route('/workers/<worker_id>/')
@requires_auth
def worker(worker_id):
    return Worker(g.pyres, worker_id).render().encode('utf-8')

@app.route('/workers/')
@requires_auth
def workers():
    return Workers(g.pyres).render().encode('utf-8')

@app.route('/stats/')
@requires_auth
def stats_resque():
    return redirect('/stats/resque/')

@app.route('/stats/<key>/')
@requires_auth
def stats(key):
    return Stats(g.pyres, key).render().encode('utf-8')

@app.route('/stat/<stat_id>/')
@requires_auth
def stat(stat_id):
    return Stat(g.pyres, stat_id).render().encode('utf-8')

@app.route('/delayed/')
@requires_auth
def delayed():
    start = request.args.get('start', 0)
    start = int(start)
    return Delayed(g.pyres, start).render().encode('utf-8')

@app.route('/delayed/<timestamp>/')
@requires_auth
def delayed_timestamp(timestamp):
    start = request.args.get('start', 0)
    start = int(start)
    return DelayedTimestamp(g.pyres, timestamp, start).render().encode('utf-8')

def main():
    app.run(host=app.config['SERVER_HOST'], port=int(app.config['SERVER_PORT']))
if __name__ == "__main__":
    main()
