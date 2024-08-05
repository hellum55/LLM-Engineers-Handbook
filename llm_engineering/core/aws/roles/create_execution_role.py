import json

import boto3

from llm_engineering.settings import settings


def create_sagemaker_execution_role(role_name, region_name="eu-central-1"):
    # Create IAM client
    iam = boto3.client(
        "iam",
        region_name=region_name,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    # Define the trust relationship policy
    trust_relationship = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"Service": "sagemaker.amazonaws.com"}, "Action": "sts:AssumeRole"}
        ],
    }

    try:
        # Create the IAM role
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship),
            Description="Execution role for SageMaker",
        )

        # Attach necessary policies
        policies = [
            "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
        ]

        for policy in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)

        print(f"Role '{role_name}' created successfully.")
        print(f"Role ARN: {role['Role']['Arn']}")

        return role["Role"]["Arn"]

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"Role '{role_name}' already exists. Fetching its ARN...")
        role = iam.get_role(RoleName=role_name)
        return role["Role"]["Arn"]


if __name__ == "__main__":
    role_arn = create_sagemaker_execution_role("SageMakerExecutionRoleLLM")
    print(role_arn)

    # Save the role ARN to a file
    with open("sagemaker_execution_role.json", "w") as f:
        json.dump({"RoleArn": role_arn}, f)

    print("Role ARN saved to 'sagemaker_execution_role.json'")
