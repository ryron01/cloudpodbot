import json
import os
import pytest

from slack_listener import app as slackapp
from rss_feed import app as rssapp
from update_show_notes import app as snapp


@pytest.fixture()
def get_events(app):
    events = []
    """Gets appropriate test events from events folder"""
    for event in os.listdir('../events'):
            if event.startsswith(app):
                events.append(event)
    return events


def test_lambda_handler(get_events, mocker):
    slackevents = get_events("slack")
    for event in slackevents:
        slackret = slackapp.lambda_handler(event, "")
        # data = json.loads(ret["body"])
        assert slackret["statusCode"] == 200
        assert "text" in slackret["body"]

    rssevents = get_events("rss")
    for event in rssevents:
        rssret = rssapp.lambda_handler(event, "")
        assert rssret["statusCode"] == 200
        assert "text" in rssret["body"]

    snevents = get_events("sn")
    for event in snevents:
        snret = snapp.lambda_handler(event, "")
        assert snret["statusCode"] == 200
        assert "text" in snret["body"]