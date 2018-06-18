#!/bin/bash

set -eu

# Login to ECR
eval $(aws ecr get-login --no-include-email --region ap-northeast-1)

registry="648688992032.dkr.ecr.ap-northeast-1.amazonaws.com"

docker pull "$registry/talk4u/treadmill-builder-gcc:0.1.0"
docker pull "$registry/talk4u/treadmill-builder-go110:0.1.0"
docker pull "$registry/talk4u/treadmill-builder-jdk8:0.1.0"
docker pull "$registry/talk4u/treadmill-sandbox-native:0.1.0"
docker pull "$registry/talk4u/treadmill-sandbox-jre8:0.1.0"
docker pull "$registry/talk4u/treadmill-sandbox-py36:0.1.1"
