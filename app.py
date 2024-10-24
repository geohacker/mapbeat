#!/usr/bin/env python3
import os
from aws_cdk import App

from mapbeat.mapbeat_stack import MapbeatStack

app = App()
sns_topic_arn = 'arn:aws:sns:us-west-2:877446169145:real-changesets-object_created'

MapbeatStack(app, "MapbeatStack", sns_topic_arn=sns_topic_arn)

app.synth()
