"""Slack Channel Sensor."""

import logging

from homeassistant.const import CONF_ID, CONF_TOKEN, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from slack import WebClient
from slack.errors import SlackApiError

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required("channel"): cv.string,
        vol.Required(CONF_NAME): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Slack Sensor based on config_config."""

    token = config.get(CONF_TOKEN)
    channel = config.get("channel")
    name = config.get(CONF_NAME)

    client = WebClient(
        token=token, run_async=True, session=async_get_clientsession(hass)
    )

    try:
        await client.auth_test()
    except SlackApiError:
        _LOGGER.error("Error setting up Slack Connection for channel %s", channel)
        return False

    async_add_entities([SlackMessage(client, channel, token, name)], True)


class SlackMessage(Entity):
    """ Slack Message."""

    def __init__(self, client, channel, token, name):
        """Initialize the sensor."""

        self._client = client
        self._channel = channel
        self._token = token
        self._name = name

        # Message info
        self._sender = None
        self._ts = None
        self._text = None

    async def async_update(self):
        """Retrieve latest state."""

        try:
            '''
            We want to avoid providing the same message twice the first time we get the time stamp of the latest message available.
            We don't save the message but we update the timestamp field and then check for any newer messages than that next time.
            '''
            if self._ts is None:
                response = await self._client.conversations_history(channel=self._channel, limit="1")
                messages = response.get("messages")
                if messages and len(messages) > 0:
                    self._ts = response.get("messages")[0].get("ts")
                else:
                    _LOGGER.warn("No messages available.")
                    return;
            else:
                response = await self._client.conversations_history(channel=self._channel, oldest=self._ts, limit="1")
                messages = response.get("messages")
                if messages and len(messages) > 0:
                    message = response.get("messages")[0] 
                    self._ts = message.get("ts")
                    self._sender = message.get("user")
                    self._text = message.get("text")

        except SlackApiError:
            _LOGGER.error("Error updating Slack Message %s", self._channel)
            return

    @property
    def text(self):
        return self._text

    @property
    def timestamp(self):
        return self._ts

    @property
    def sender(self):
        return self._sender

    @property
    def channel(self):
        return self._channel

    @property
    def name(self):
        return self._name

    @property 
    def state(self):
        return self._text

    @property
    def state_attributes(self):
        """Return entity attributes."""

        attrs = {
            "text": self._text,
            "timestamp": self._ts,
            "sender": self._sender,
            "channel": self._channel,
        }

        return {k: v for k, v in attrs.items() if v is not None}
