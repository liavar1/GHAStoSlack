# GitHub Advanced Security to Slack Integration
Sending GitHub advanced security (GHAS) alerts to Slack
I did it on the GitHub Enterprise server but I believe it works for github.com as well.

As of now, the integration of GitHub to Slack natively supports actions related to commits, pull requests (PRs), and Issues. However, when trying to facilitate a finer degree of control, such as filtering security alerts, the functionality falls short. The Slack notifications for these filtered actions are absent. This issue persists even when creating a Slack App and sending GitHub alerts to the webhook associated with the Slack App.

This overarching problem stems from the fact that the Slack webhook does not provide support for all the keys in the JSON payload that GitHub sends. The ones it supports are quite limited. Therefore, to ensure all necessary information is relayed to Slack, it becomes necessary to have an intermediary, or a "proxy webhook", which can process the payload from GitHub and rewrite it in a way that is compatible with Slack.

To achieve this, we're leveraging AWS services - API Gateway and Lambda function. Here's how we do it:

![The flow](.github/images/GHAStoSlack.png?raw=true "GHAStoSlack")

## Steps

1. The AWS API Gateway acts as the direct receiver of notifications from GitHub. This behaves as our "proxy webhook" taking in the payload from GitHub.

2. It then forwards this message to an AWS Lambda function. This function is designed to parse the payload, perform necessary transformations, and format the data into a Slack-compatible JSON.

3. The formatted message is sent to Slack via a POST request.

This way, we can ensure all relevant information from GitHub, including actions that aren't supported directly, are relayed effectively to Slack.

Note: This approach can be customized further to relay only the needed information, making GitHub to Slack communication efficient and customized to your specific needs.

## The How To
To create a webhook with AWS Lambda and API Gateway, you would create a new HTTP REST API. Here are the steps:

1. Create a new Lambda function:

Go to AWS Lambda in your AWS Console and select "Create function". You can call your function something like `GithubWebhookToSlack` and select Python.
In your function code, you'll process the incoming GitHub payload and send a formatted message to Slack.
I've created 2 Lambda functions, and each one builds a different message:
- [block_kit.py](block_kit.py)
- [legacy_msg.py](legacy_msg.py)

The issue is that Slack deprecated some features on their messages and moved to a "block_kit" concept. I personally didn't like it because you can't color anything (hence the emoji).
The deprecated one looks good on the desktop app but not as good on mobile (the text is not bold and with stars around it).
So pick whatever you like best.


2. Create a new REST API in API Gateway:

Go to AWS API Gateway and select "Create API", then select "REST API".


3. Set up your API:

You'll mostly use the default settings here, but make sure to choose "Regional" for the Endpoint Type.
In the "Actions" dropdown, choose "Create Resource" to make a new resource under your API - this could be something like `/webhook`. 
Then, with your new resource selected, go back to the "Actions" dropdown and choose "Create Method".
Select "POST", and it will create a new POST method for your resource.


4. Connect your API to your Lambda function:

After you've created your POST method, you'll be able to set up its integration.
Choose "Lambda Function" for the Integration type, make sure "Use Lambda Proxy integration" is ticked (which passes data between API Gateway and Lambda as is, in the `event` object),
and enter the name of your Lambda function in the "Lambda Function" textbox.


5. Deploy your API:

To make your API usable, you need to deploy it. Go to `Actions` > `Deploy API`.
You'll need to create a new Deployment stage (you can call it something like `GHAS`). After deployment, you'll get an "Invoke URL", which will look like `https://xxxxxx.execute-api.{region}.amazonaws.com/prod/{resource}`, where `xxxxxx` is randomly generated by AWS, `{region}` is your AWS region, and `{resource}` is the resource path you created.

6. Setup your GitHub webhook:

Go to your Organization/Repo -> Settings -> Hooks -> Add webhook.
- Payload URL = <The_API_GW_URL>
- Content type = application/json
- Which events would you like to trigger this webhook?
    - Code scanning alerts
    - Dependabot alerts
    - Secret scanning alert locations
    - Secret scanning alerts
    - Security and analyses

Now, you've got a webhook URL that's ready to receive POST requests from GitHub!

