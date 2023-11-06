import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
)


class VpcStack(cdk.Stack):
    def __init__(self, scope: "VpcSetup", id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        self.vpc = ec2.Vpc(
            self,
            "WebAppVPC",
            max_azs=3,
        )
        # Create a flow log for VPC
        log_group = logs.LogGroup(self, "MyCustomLogGroup")
        flow_logs_role = iam.Role(
            self,
            "MyCustomRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        )
        ec2.FlowLog(
            self,
            "FlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                log_group, flow_logs_role
            ),
        )
