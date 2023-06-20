from flask import Flask, make_response, request
from slack_bolt import BoltRequest
from slack_bolt.adapter.flask import SlackRequestHandler

from chatiq import ChatIQ

# Initialize ChatIQ with your settings
chatiq = ChatIQ(
    slack_client_id="your-slack-client-id",  # Optional, or read SLACK_CLIENT_ID from environment variables
    slack_client_secret="your-slack-client-secret",  # Optional, or read SLACK_CLIENT_SECRET from environment variables
    slack_signing_secret="your-slack-signing-secret",  # Optional, or read SLACK_SIGNING_SECRET from environment variables
    openai_api_key="your-openai-api-key",  # Optional, or read OPENAI_API_KEY from environment variables
    postgres_url="your-postgres-url",  # Optional, or read POSTGRES_URL from environment variables
    weaviate_url="your-weaviate-url",  # Optional, or read WEAVIATE_URL from environment variables
    weaviate_api_key="your-weaviate-api-key",  # Optional, or read WEAVIATE_API_KEY from environment variables
    rate_limit_retry=True,  # Optional. Enable the rate limit retry handler (default is False)
)
# Start listening for Slack events
chatiq.listen()

# Create a Flask app
app = Flask(__name__)
# Create a SlackRequestHandler with the Bolt app from ChatIQ
handler = SlackRequestHandler(chatiq.bolt_app)


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
