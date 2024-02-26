import urllib3
import json

# Initialize HTTP client
http = urllib3.PoolManager()

def lambda_handler(event, context):
    # Webhook URL for Slack service
    url = "<SLACK_WEBHOOK_URL>"

    # Parse GitHub event and payload from request
    git_event = event['headers'].get('X-GitHub-Event')
    git_payload = json.loads(event.get('body'))

    # Extract necessary information from GitHub payload
    action = git_payload.get('action')
    org = git_payload.get('organization', {}).get('login')
    html_url = git_payload.get('alert', {}).get('html_url')
    alert_state = git_payload.get('alert', {}).get('state')
    alert_severity = git_payload.get('alert', {}).get('severity')
    repository = git_payload.get('repository', {}).get('name')
    repo_url = git_payload.get('repository', {}).get('html_url')
    sender = git_payload.get('sender', {}).get('login')

    #Set colors for messages: red/green
    action_types = {"created": "#FF051E", "reintroduced": "#FF051E", "reopened": "#FF051E", 
                    "resolved": "#0FD634", "fixed": "#0FD634"}
     
    #Set blue for informational messages
    action_type = action_types.get(action, "#3AA3E3") if action else "#3AA3E3"
    
    #Set purple for dependabot
    if action_type == "#FF051E" and git_event.startswith("dependabot"):
        action_type = "#893AE3"

    text = ""
    if action is not None: text += f"*Action:* {action}\n"
    if repository is not None: text += f"*Repository:* <{repo_url}|{repository}>\n"
    if alert_severity is not None: text += f"*Alert Severity:* {alert_severity}\n"
    if alert_state is not None: text += f"*Alert State:* {alert_state}\n"
    if html_url is not None: text += f"*Alert Url:* {html_url}\n"
    if org is not None: text += f"*Organization:* {org}\n"
    if sender is not None: text += f"*Sender:* {sender}\n"

    # Create message for Slack
    msg =  {
            "text": f"*{git_event}*",
            "attachments": [
                {
                    "text": text,
                    "color": f"{action_type}"
                }
            ]
        }


    # Encode the message and POST it to Slack
    encoded_msg = json.dumps(msg).encode('utf-8')
    resp = http.request("POST", url, body=encoded_msg)

    # Print the response
    print({
        "message": msg['text'],
        "status_code": resp.status,
        "response": resp.data,
    })

    return {
        "statusCode": 200,
        "body": "Message posted to Slack"
    }
