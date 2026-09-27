import boto3
import subprocess
import sys


def get_ecr_login(region: str) -> str:
    """Get ECR login token."""
    ecr = boto3.client("ecr", region_name=region)
    token = ecr.get_authorization_token()
    return token["authorizationData"][0]["proxyEndpoint"]


def push_image(region: str, account_id: str, repo_name: str, tag: str = "latest"):
    """Build and push Docker image to ECR."""
    ecr_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
    image = f"{ecr_url}/{repo_name}:{tag}"

    print(f"Building image: {image}")
    subprocess.run(["docker", "build", "-t", image, "."], check=True)

    print("Logging into ECR...")
    login_cmd = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {ecr_url}"
    subprocess.run(login_cmd, shell=True, check=True)

    print(f"Pushing image: {image}")
    subprocess.run(["docker", "push", image], check=True)
    print("Done!")
    return image


def update_eks_deployment(cluster_name: str, image: str, region: str):
    """Update EKS deployment with new image."""
    eks = boto3.client("eks", region_name=region)

    # Update kubeconfig
    subprocess.run([
        "aws", "eks", "update-kubeconfig",
        "--name", cluster_name,
        "--region", region
    ], check=True)

    # Update deployment image
    subprocess.run([
        "kubectl", "set", "image",
        "deployment/aml-api",
        f"aml-api={image}"
    ], check=True)
    print(f"Deployment updated with {image}")


def validate_deployment(api_url: str):
    """Check if the deployed API is healthy."""
    import requests
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print("Deployment healthy!")
            return True
        else:
            print(f"Unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"Validation failed: {e}")
        return False


if __name__ == "__main__":
    REGION = "eu-west-1"
    ACCOUNT_ID = "123456789012"  # Replace with your AWS account ID
    REPO_NAME = "aml-fraud-detection"
    CLUSTER_NAME = "aml-mlops-cluster"
    API_URL = "http://aml-api.example.com"

    image = push_image(REGION, ACCOUNT_ID, REPO_NAME)
    update_eks_deployment(CLUSTER_NAME, image, REGION)
    validate_deployment(API_URL)