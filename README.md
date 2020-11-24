# slack_sensor
Slack sensor for Home Assistant that retrieves messages from a Slack Channel

## Installation
1. Clone the repo under your custom_components directory in Home Assistant
2. Add the following configuration to your configuration.yaml
```
sensor:
  - platform: slack_sensor
    # Bot User OAuth Access Token
    token: !secret slack_alexa_commands_api_token
    # Channel ID to retrieve messages from (NOT the channel name)
    # Use https://api.slack.com/methods/conversations.list if you don't know the channel id
    channel: !secret slack_alexa_commands_channel 
    # Friendly name for the sensor in Home Assistant
    name: YOUR_SLACK_SENSOR
    # Optional, how often to poll slack for a new message
    scan_interval: 3
```    
## Attributes
- text: 'the text of the message'
- timestamp: '1606177147.000100'
  - The timestamp of the latest message
- sender: U12ABCDEF
  - The ID of the sender
- channel: 1234ABCDEF
  - The ID of the channel the message was from
- friendly_name: YOUR_SLACK_SENSOR

