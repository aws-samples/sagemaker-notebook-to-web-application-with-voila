#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from cdk.app_stack import CdkStack

app = cdk.App()
stack = CdkStack(app, "Voila-app-from-Notebook")

Aspects.of(app).add(AwsSolutionsChecks())

NagSuppressions.add_stack_suppressions(stack, [
    {"id": "AwsSolutions-IAM4", "reason":"Condition on ECS Cluster ARN matching is inplace"},
    {"id": "AwsSolutions-IAM5", "reason":"Condition on ECS Cluster ARN matching is inplace"},
    {"id": "AwsSolutions-IAM5", "reason":"Condition on ECS Cluster ARN matching is inplace"},
    {"id": "AwsSolutions-ECS7", "reason":"awslogs logging anable at ApplicationLoadBalancedTaskImageOptions level"},
    {"id": "AwsSolutions-AS3", "reason":"ASG notifications in this particular use case for desplaying a Voilà App is not needed"},
    {"id": "AwsSolutions-SNS2", "reason":"SNS Topic does not need SSE"},
    {"id": "AwsSolutions-SNS3", "reason":"SNS Topic does not need requests to use SSL"},
    {"id": 'AwsSolutions-EC26', "reason": "lorem ipsum" },
    {"id": "AwsSolutions-SNS2", "reason":"SNS Topic does not need SSE"},
    {"id": "AwsSolutions-SNS3", "reason":"SNS Topic does not need requests to use SSL"},
    {"id": "AwsSolutions-ELB2", "reason":"Enabling logs requires a S3 bucket. The application is not critical logs from the ELB is not necessary."},
    {"id": "AwsSolutions-EC26", "reason":"Default configuration of the construct. No restrictions are specifically needed for the inbound access"},
    {"id": "AwsSolutions-L1", "reason":"Default configuration of the construct. No restrictions are specifically needed for the inbound access"}
])

app.synth()
