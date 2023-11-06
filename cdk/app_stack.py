import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as asset,
    aws_sns as sns,
    aws_autoscaling as autoscaling
)
import logging
import cdk_nag

from .vpc_stack import VpcStack


logging.basicConfig(level=logging.INFO)


class CdkStack(cdk.Stack):
    def __init__(self, scope: "VoilaApp", id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if self.node.try_get_context("vpc_id"):
            # Import the VPC from context
            logging.info(f'Deploying in VPC {self.node.try_get_context("vpc_id")}')
            vpc = ec2.Vpc.from_lookup(
                self, "VPC", vpc_id=self.node.try_get_context("vpc_id")
            )

        else:
            # Create a new VPC
            vpc_stack=VpcStack(self,"VpcStack")
            vpc = vpc_stack.vpc
            
        # Create ECS cluster
        cluster = ecs.Cluster(self, "WebAppCluster", vpc=vpc, container_insights=True)

        # Add an AutoScalingGroup with spot instances to the existing cluster
        cluster.add_capacity(
            "ClusterAutoScalingGroup",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=2,
            instance_type=ec2.InstanceType("c5.xlarge"),
            cooldown=cdk.Duration.minutes(5)
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
                log_driver= ecs.AwsLogDriver(stream_prefix="voilapp"),  
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
        

        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/InstanceRole/DefaultPolicy/Resource", 
            suppressions=[
            {"id": "AwsSolutions-IAM5", "reason":"Condition on ECS Cluster ARN matching is inplace"}
            ]
        ),
        
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/DrainECSHook/Function/ServiceRole/Resource", 
            suppressions=[
            {"id": "AwsSolutions-IAM4", "reason":"Condition on ECS Cluster ARN matching is inplace"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/DrainECSHook/Function/ServiceRole/DefaultPolicy/Resource", 
            suppressions=[
            {"id": "AwsSolutions-IAM5", "reason":"Condition on ECS Cluster ARN matching is inplace"}
            ]
        ), 
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppFargateService/TaskDef/ExecutionRole/DefaultPolicy/Resource", 
            suppressions=[
            {"id": "AwsSolutions-IAM5", "reason":"Condition on ECS Cluster ARN matching is inplace"}
            ]
        ),     
        
        
        cdk_nag.NagSuppressions.add_resource_suppressions(construct=cluster, 
            suppressions=[
            {"id": "AwsSolutions-ECS7", "reason":"awslogs logging anable at ApplicationLoadBalancedTaskImageOptions level"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/ASG", 
            suppressions=[
            {"id": "AwsSolutions-AS3", "reason":"ASG notifications in this particular use case for desplaying a Voilà App is not needed"}
            ]
        ),
 
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/ASG", 
            suppressions=[
            {"id": "AwsSolutions-SNS2", "reason":"SNS Topic does not need SSE"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/ASG", 
            suppressions=[
            {"id": "AwsSolutions-SNS3", "reason":"SNS Topic does not need requests to use SSL"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/LifecycleHookDrainHook/Topic/Resource", 
            suppressions=[
            {"id": "AwsSolutions-SNS2", "reason":"SNS Topic does not need SSE"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppCluster/ClusterAutoScalingGroup/LifecycleHookDrainHook/Topic/Resource", 
            suppressions=[
            {"id": "AwsSolutions-SNS3", "reason":"SNS Topic does not need requests to use SSL"}
            ]
        ),
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppFargateService/LB/Resource", 
            suppressions=[
            {"id": "AwsSolutions-ELB2", "reason":"Enabling logs requires a S3 bucket. The application is not critical logs from the ELB is not necessary."}
            ]
        ),
        
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppFargateService/LB/SecurityGroup/Resource", 
            suppressions=[
            {"id": "AwsSolutions-EC26", "reason":"Default configuration of the construct. No restrictions are specifically needed for the inbound access"}
            ]
        ),

        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(stack=self, path="/Voila-app-from-Notebook/WebAppFargateService/LB/SecurityGroup/Resource", 
            suppressions=[
            {"id": "AwsSolutions-L1", "reason":"Default configuration of the construct. No restrictions are specifically needed for the inbound access"}
            ]
        ),