import os

from flask import Flask, make_response, request
from flask_sqlalchemy import SQLAlchemy
from slack_bolt import BoltRequest
from slack_bolt.adapter.flask import SlackRequestHandler

from chatiq import ChatIQ

# chatiq.chatiq ChatIQ with your settings
chatiq = ChatIQ(
    slack_client_id=os.getenv("SLACK_CLIENT_ID"),
    slack_client_secret=os.getenv("SLACK_CLIENT_SECRET"),
    slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    postgres_url=os.getenv("DATABASE_URL"),  # Changed from POSTGRES_URL to DATABASE_URL
    weaviate_url=os.getenv("WEAVIATE_URL"),
    weaviate_api_key=os.getenv("WEAVIATE_API_KEY"),
    rate_limit_retry=True,  # Optional. Enable the rate limit retry handler (default is False)
)

# Start listening for Slack events
chatiq.listen()


# Create a Flask app
app = Flask(__name__)
# Create a SlackRequestHandler with the Bolt app from ChatIQ
handler = SlackRequestHandler(chatiq.bolt_app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)


# Handle installation and OAuth redirect endpoints
@app.route("/slack/install", methods=["GET"])
@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    # Use the SlackRequestHandler to handle these requests
    return handler.handle(request)


# Handle Slack events
@app.route("/slack/events", methods=["POST"])
def endpoint():
    # Get the request body and headers
    body = request.get_data().decode("utf-8")
    headers = {k: v for k, v in request.headers}
    # Create a BoltRequest from the request data
    bolt_req = BoltRequest(body=body, headers=headers)
    # Dispatch the Bolt request in the ChatIQ's Bolt app
    bolt_resp = chatiq.bolt_app.dispatch(bolt_req)
    # Return the response from the Bolt app
    return make_response(bolt_resp.body, bolt_resp.status, bolt_resp.headers)
