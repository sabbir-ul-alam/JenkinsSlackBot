import os
import jenkins
import re
# Use the package we installed
from slack_bolt import App



# Connect to jenkins
server = jenkins.Jenkins('http://localhost:9090', username='sabbir', password='108060')

project = ""
branch = ""
profile = ""
# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),

)


## To check if queue if available for next build
def isQueueAvailable():
    queue_info=server.get_running_builds()
    print("check queue")
    print(queue_info)
    if len(queue_info)>0:
        print(queue_info[0])
        return False
    return True


def sendWarning(body,client,text):
        client.chat_postEphemeral(
            text= text,
            channel=body['channel']['id'],
            user=body['user']['id'],
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{} :alert:".format(text)
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Delete"
                        },
                        "value": "delete",
                        "action_id": "delete_2"
                    }
                }
            ]

        )


## delete message. Regex is ussed to here to use the same function for all delete activity
@app.action(re.compile("delete"))
def deleteMessage(ack,respond,body):
    ack()
    global project,branch,profile
    print(body)
    print(body['container']['message_ts'])
    respond({
        "delete_original": "true"
    })
    project = ""
    branch = ""
    profile = ""



##send request to jenkins to build job
@app.action("button_1")
def buildAndDeploy(ack,client,body,respond):
    ack()
    queueAvailable=isQueueAvailable()
    if queueAvailable is False:
        sendWarning(body,client,"Queue is not available. Please try again when the current build is finished")
        respond({
            "delete_original": "true"
        })
    else:

        global branch,project,profile
        print(project)
        print(body)
        if project=="":
            client.chat_postEphemeral(
            text= "Select a Project Fist",
            channel=body['channel']['id'],
            user=body['user']['id'],
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You need to select a project first :alert:"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Delete"
                        },
                        "value": "delete",
                        "action_id": "delete_2"
                    }
                }
            ]

        )
        else:
            server.build_job("nid_build",[('project',project),('branch',branch),('profile',profile),('user_name',body['user']['id'])],108060)
        project = ""
        branch = ""
        profile = ""
        respond({
        "delete_original": "true"
    })


@app.action("select_1")
def selectProject(ack,payload):
    ack()
    global project,branch,profile
    project = payload['selected_option']['value']
    print(project)

@app.action("select_2")
def selectBranch(ack,payload):
    ack()
    global project,branch,profile
    branch = payload['selected_option']['value']
    print(branch)

@app.action("select_3")
def selectProfile(ack,payload):
    ack()
    global project,branch,profile
    profile = payload['selected_option']['value']
    print(profile)


""" jarvis slash command from the workplace will trigger this function.
In response it will send a interactive block kit message.
Note that, chat_postEphemeral() is used so that only the respective user can see this message. 
"""
@app.command('/jarvis')
def startJarvis(ack,payload,client):
    ack()
	#server._request()
    print(payload)
    global project, branch, profile
    project = ""
    branch = ""
    profile = ""

    client.chat_postEphemeral(
        channel=payload['channel_id'],
        text="JARVIS says hello",
        user=payload['user_id'],
        blocks= [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Hello <@{}>.\n I am *J.A.R.V.I.S* :jarvis: (Just A Rather Very Intelligent System).\n \nPlease select the following options to deploy your project sir. ".format(payload['user_id'])
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Which project you want to deploy? :thinking_face:"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"

				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Parter Service"
						},
						"value": "service"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "CMS-Portal"
						},
						"value": "cms"
					}
				],
				"action_id": "select_1"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Can you tell me the branch name?"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Master"
						},
						"value": "master"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Release"
						},
						"value": "release"
					}
				],
				"action_id": "select_2"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "One last thing. Choose profile."
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Test"
						},
						"value": "test"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Dev"
						},
						"value": "dev"
					}
				],
				"action_id": "select_3"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",

						"text": "Build & Deploy"
					},
					"style": "primary",
					"value": "build",
					"action_id": "button_1"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",

						"text": "Delete"
					},
					"style": "danger",
					"value": "delete",
					"action_id": "delete_1"
				}
			]
		}
	]


    )




# Start your app
if __name__ == "__main__":
    print(os.environ.get("SLACK_BOT_TOKEN"))
    app.start(port=int(os.environ.get("PORT", 3000)))