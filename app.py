#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import CdkStack


app = core.App()
CdkStack(app, "voila-app-sharing-dashboard")

app.synth()
