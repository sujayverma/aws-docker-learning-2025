from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os

from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *

# Honeycomb Code
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# X-Ray -----
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
xray_url = os.getenv('AWS_XRAY_URL')

# Cloud watch logs
import watchtower, logging
import boto3

# Rollbar 
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception



if not os.environ.get("AWS_REGION"):
    os.environ["AWS_REGION"] = "ap-south-1"  # Change to your desired AWS region

AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
# Initialize and configure logger for cloud watch logs.
# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.INFO)
# console_handler = logging.StreamHandler()
# LOGGER.addHandler(console_handler)

# CloudWatch logging


# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
# Initialize automatic instrumentation with Flask
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
frontend = os.getenv('FRONTEND_URL')
backend = os.getenv('BACKEND_URL')
origins = [frontend, backend]

# Initialize Xray tracing middleware.

# xray_recorder.configure(service='backend-flask', context_missing='LOG_ERROR', daemon_address='xray-daemon:2000', plugins=[])
# XRayMiddleware(app, xray_recorder)

# CloudWatch logging
# LOGGER.addHandler(watchtower.CloudWatchLogHandler(log_group='backend-flask', boto3_client=boto3.client("logs", region_name="ap-south-1")))
# LOGGER.info("Hi")

cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  expose_headers="location,link",
  allow_headers="content-type,if-modified-since",
  methods="OPTIONS,GET,HEAD,POST"
)

# rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
# with app.app_context():
#     """init rollbar module"""
#     rollbar.init(
#         # access token
#         rollbar_access_token,
#         # environment name - any string, like 'production' or 'development'
#         'backend-flask',
#         # server root directory, makes tracebacks prettier
#         root=os.path.dirname(os.path.realpath(__file__)),
#         # flask already sets up logging
#         allow_logging_basic_config=False)

#     # send exceptions from `app` to rollbar, using flask's signal system.
#     got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

# @app.after_request
# def after_request(response):
#     timestamp = strftime('[%Y-%b-%d %H:%M]')
#     LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
#     return response

# @app.route('/rollbar/test')
# def rollbar_test():
#   rollbar.report_message('Hello World!', 'warning')
#   return 'Hello World!'

# @app.route('/rollbar/hello')
# def hello():
#     print("DEBUG - in hello()")
#     x = None
#     x[5]
#     return "Hello World!"

@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
  user_handle  = 'andrewbrown'
  model = MessageGroups.run(user_handle=user_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

@app.route("/api/messages/@<string:handle>", methods=['GET'])
def data_messages(handle):
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.args.get('user_reciever_handle')

  model = Messages.run(user_sender_handle=user_sender_handle, user_receiver_handle=user_receiver_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
def data_create_message():
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.json['user_receiver_handle']
  message = request.json['message']

  model = CreateMessage.run(message=message,user_sender_handle=user_sender_handle,user_receiver_handle=user_receiver_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return
@tracer.start_as_current_span("home.calls")
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  # data = HomeActivities.run(logger=LOGGER)
  data = HomeActivities.run()
  with tracer.start_as_current_span(name="hello"):
    span = trace.get_current_span()
    span.set_attribute("message", "hello world!")
  return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
# @xray_recorder.capture('Hit the Notification endpoint')
def data_notifications():
  # segment = xray_recorder.begin_segment('notification_data')
  
  # sub_segment = xray_recorder.begin_subsegment('notication_handler')
 
  now = datetime.now(timezone.utc).astimezone()
  data = NotificationsActivities.run()
  # sub_segment.put_metadata('value', data, 'data_fetched')
  # sub_segment.put_annotation('request_time', str(now))
  # xray_recorder.end_subsegment()
  return data, 200
  # try:
    # now = datetime.now(timezone.utc).astimezone()
    # data = NotificationsActivities.run()
    # sub_segment.put_metadata('value', data, 'data_fetched')
    # sub_segment.put_annotation('request_time', str(now))
    # return data, 200
  # finally:
    # xray_recorder.end_subsegment()
    # return

  # xray_recorder.end_subsegment()
  # xray_recorder.end_segment()
  

@app.route("/api/activities/@<string:handle>", methods=['GET'])
def data_handle(handle):
  model = UserActivities.run(handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

@app.route("/api/activities/search", methods=['GET'])
def data_search():
  term = request.args.get('term')
  model = SearchActivities.run(term)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities():
  user_handle  = 'andrewbrown'
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, user_handle, ttl)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

if __name__ == "__main__":
  app.run(debug=True)