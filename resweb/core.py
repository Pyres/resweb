from functools import wraps
from flask import Flask, g, redirect, request, Response, render_template, url_for
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
    view_ov = Overview(g.pyres)
    data = {
        'queues': view_ov.queues(),
        'fail_count': view_ov.fail_count(),
        'workers': view_ov.workers(),
        'empty_workers': view_ov.empty_workers(),
        'worker_size': view_ov.worker_size(),
        'total_workers': view_ov.total_workers(),
        'version': view_ov.version(),
        'resweb_version': view_ov.resweb_version(),
        'address': view_ov.address()
    }
    return render_template('overview.html', data=data)

@app.route("/working/")
@requires_auth
def working():
    view_working = Working(g.pyres)
    data = {
        'workers': view_working.workers(),
        'empty_workers': view_working.empty_workers(),
        'worker_size': view_working.worker_size(),
        'total_workers': view_working.total_workers(),
        'version': view_working.version(),
        'resweb_version': view_working.resweb_version(),
        'address': view_working.address()
    }
    return render_template('working.html', data=data)

@app.route("/queues/")
@requires_auth
def queues():
    view_queues = Queues(g.pyres)
    data = {
        'queues': view_queues.queues(),
        'fail_count': view_queues.fail_count(),
        'version': view_queues.version(),
        'resweb_version': view_queues.resweb_version(),
        'address': view_queues.address()
    }
    return render_template('queues.html', data=data)

@app.route('/queues/<queue_id>/')
@requires_auth
def queue(queue_id):
    start = int(request.args.get('start', 0))
    view_queue =  Queue(g.pyres, queue_id, start)
    data = {
        'queue': view_queue.queue(),
        'start': view_queue.start(),
        'end': view_queue.end(),
        'size': view_queue.size(),
        'pagination': view_queue.pagination(),
        'jobs': view_queue.jobs(),
        'version': view_queue.version(),
        'resweb_version': view_queue.resweb_version(),
        'address': view_queue.address()
    }
    return render_template('queue.html', data=data)

@app.route('/failed/')
@requires_auth
def failed():
    view_failed = Failed(g.pyres)
    data = {
        'failed_jobs': view_failed.failed_jobs(),
        'start': view_failed.start(),
        'end': view_failed.end(),
        'size': view_failed.size(),
        'pagination': view_failed.pagination(),
        'version': view_failed.version(),
        'resweb_version': view_failed.resweb_version(),
        'address': view_failed.address()
    }
    
    return render_template('failed.html', data=data)

@app.route('/failed/retry/', methods=["POST"])
@requires_auth
def failed_retry():
    failed_job = request.form['failed_job']
    job = b64decode(failed_job)
    decoded = ResQ.decode(job)
    failure.retry(g.pyres, decoded['queue'], job)
    return redirect(url_for('failed'))

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
    return redirect(url_for('failed'))

@app.route('/workers/<worker_id>/')
@requires_auth
def worker(worker_id):
    view_worker =  Worker(g.pyres, worker_id)
    data = {
        'worker': view_worker.worker(),
        'host': view_worker.host(),
        'pid': view_worker.pid(),
        'state': view_worker.state(),
        'started_at': view_worker.started_at(),
        'queues': view_worker.queues(),
        'processed': view_worker.processed(),
        'failed': view_worker.failed(),
        'data': view_worker.data(),
        'code': view_worker.code(),
        'runat': view_worker.runat(),
        'version': view_worker.version(),
        'resweb_version': view_worker.resweb_version(),
        'address': view_worker.address()
    }
    print data
    return render_template('worker.html', data=data)

@app.route('/workers/')
@requires_auth
def workers():
    view_workers = Workers(g.pyres)
    data = {
        'workers': view_workers.workers(),
        'size': view_workers.size(),
        'all': view_workers.all(),
        'version': view_workers.version(),
        'resweb_version': view_workers.resweb_version(),
        'address': view_workers.address()
    }
    print data
    return render_template('workers.html', data=data)

@app.route('/stats/')
@requires_auth
def stats_resque():
    return redirect(url_for('stats', key='resque'))

@app.route('/stats/<key>/')
@requires_auth
def stats(key):
    view_stats =  Stats(g.pyres, key)
    data = {
        'key': key,
        'sub_nav': view_stats.sub_nav(),
        'title': view_stats.title(),
        'stats': view_stats.stats(),
        'version': view_stats.version(),
        'resweb_version': view_stats.resweb_version(),
        'address': view_stats.address()
    }
    print data
    return render_template('stats.html', data=data)

@app.route('/stat/<stat_id>/')
@requires_auth
def stat(stat_id):
    view_stat =  Stat(g.pyres, stat_id)
    data = {
        'stat_id': stat_id,
        'key': view_stat.key(),
        'key_type': view_stat.key_type(),
        'stat_items': view_stat.items(),
        'size': view_stat.size(),
        'version': view_stat.version(),
        'resweb_version': view_stat.resweb_version(),
        'address': view_stat.address()
    }
    print data
    return render_template('stat.html', data=data)

@app.route('/delayed/')
@requires_auth
def delayed():
    view_delayed = Delayed(g.pyres)
    data = {
        'jobs': view_delayed.jobs(),
        'start': view_delayed.start(),
        'end': view_delayed.end(),
        'size': view_delayed.size(),
        'pagination': view_delayed.pagination(),
        'version': view_delayed.version(),
        'resweb_version': view_delayed.resweb_version(),
        'address': view_delayed.address()
    }
    print data
    return render_template('delayed.html', data=data)

@app.route('/delayed/<timestamp>/')
@requires_auth
def delayed_timestamp(timestamp):
    view_dt =  DelayedTimestamp(g.pyres, timestamp)
    data = {
        'formated_timestamp': view_dt.formated_timestamp(),
        'jobs': view_dt.jobs(),
        'start': view_dt.start(),
        'end': view_dt.end(),
        'size': view_dt.size(),
        'pagination': view_dt.pagination(),
        'version': view_dt.version(),
        'resweb_version': view_dt.resweb_version(),
        'address': view_dt.address()
    }
    print data
    return render_template('delayed_timestamp.html', data=data)

def main():
    app.run(host=app.config['SERVER_HOST'], port=int(app.config['SERVER_PORT']), debug=True)
if __name__ == "__main__":
    main()
