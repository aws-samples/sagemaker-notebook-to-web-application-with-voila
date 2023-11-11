import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as asset,
)
import logging
from constructs import Construct
from .vpc_stack import VpcStack


logging.basicConfig(level=logging.INFO)


class CdkStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if self.node.try_get_context("vpc_id"):
            # Import the VPC from context
            logging.info(f'Deploying in VPC {self.node.try_get_context("vpc_id")}')
            vpc = ec2.Vpc.from_lookup(
                self, "VPC", vpc_id=self.node.try_get_context("vpc_id")
            )

        else:
            # Create a new VPC
            vpc_stack = VpcStack(self, "VpcStack")
            vpc = vpc_stack.vpc

        # Create ECS cluster
        cluster = ecs.Cluster(self, "WebAppCluster", vpc=vpc, container_insights=True)

        # Add an Auto Scaling Group to the existing cluster
        cluster.add_capacity(
            "ClusterAutoScalingGroup",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=2,
            instance_type=ec2.InstanceType("c5.xlarge"),
            cooldown=cdk.Duration.minutes(5),
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset(
            directory="voila-app", platform=asset.Platform.LINUX_AMD64
        )

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "WebAppFargateService",
            cluster=cluster,
            cpu=2048,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,
                log_driver=ecs.AwsLogDriver(stream_prefix="voilapp"),
            ),
            memory_limit_mib=4096,
            public_load_balancer=True,
        )

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=10)
        scaling.scale_on_cpu_utilization(
            "AppCpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=cdk.Duration.seconds(60),
            scale_out_cooldown=cdk.Duration.seconds(60),
        )
