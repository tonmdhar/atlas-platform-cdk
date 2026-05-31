from constructs import Construct
from aws_cdk import (
    aws_cloudwatch as cw,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_cloudwatch_actions as cw_actions,
    aws_eks as eks,
    Duration,
)

class MonitoringConstruct(Construct):

    def __init__(
            self,
            scope: Construct,
            id: str,
            env_name: str,
            cluster: eks.Cluster,
    ) -> None:
        super().__init__(scope, id)

        # SNS topic for alerts
        self.alert_topic = sns.Topic(
            self,
            "AlertTopic",
            topic_name=f"atlas-platform-{env_name}-alerts",
            display_name=f"Atlas Platform {env_name.capitalize()} Alerts"
        )

        # CloudWatch Dashboard
        self.dashboard = cw.Dashboard(
            self,
            "Dashboard",
            dashboard_name=f"atlas-platform-{env_name}"
        )

        # EKS Cluster CPU Alarm
        cpu_alarm = cw.Alarm(
            self,
            "ClusterCpuAlarm",
            alarm_name=f"atlas-{env_name}-cluster-cpu-high",
            metric=cw.Metric(
                namespace="ContainerInsights",
                metric_name="node_cpu_utilization",
                dimensions_map={"ClusterName": cluster.cluster_name},
                period=Duration.minutes(5),
                statistic="Average",
            ),
            threshold=80,
            evaluation_periods=3,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )
        cpu_alarm.add_alarm_action(cw_actions.SnsAction(self.alert_topic))

        # EKS Cluster Memory Alarm
        memory_alarm = cw.Alarm(
            self,
            "ClusterMemoryAlarm",
            alarm_name=f"atlas-{env_name}-cluster-memory-high",
            metric=cw.Metric(
                namespace="ContainerInsights",
                metric_name="node_memory_utilization",
                dimensions_map={"ClusterName": cluster.cluster_name},
                period=Duration.minutes(5),
                statistic="Average",
            ),
            threshold=80,
            evaluation_periods=3,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
        )
        memory_alarm.add_alarm_action(cw_actions.SnsAction(self.alert_topic))

        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cw.GraphWidget(
                title="Cluster CPU Utilization",
                left=[cpu_alarm.metric],
                width=12,
            ),
            cw.GraphWidget(
                title="Cluster Memory Utilization",
                left=[memory_alarm.metric],
                width=12
            )
        )