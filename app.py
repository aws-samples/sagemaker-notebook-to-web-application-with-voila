#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks

from cdk.cdk_stack import CdkStack


app = cdk.App()
CdkStack(app, "Voila-app-from-Notebook")

Aspects.of(app).add(AwsSolutionsChecks())
app.synth()
