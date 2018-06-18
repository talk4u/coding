#!/bin/bash

if [[ $# -ne 2 ]]; then
  echo "Usage: ./build.sh DIRECTORY VERSION"
  echo "       will build image with DIRECTORY/Dockerfile and tag with VERSION"
  exit 0
fi

set -eu

# Login to ECR
eval $(aws ecr get-login --no-include-email --region ap-northeast-1)

registry="648688992032.dkr.ecr.ap-northeast-1.amazonaws.com"

function build_and_push() {
  dirname=$1
  version=$2
  tag="talk4u/treadmill-${dirname%%/}"
  dockerfile="${dirname%%/}/Dockerfile"

  echo "Build $tag:$version"
  
  docker build -f $dockerfile . -t $tag:$version
  docker tag $tag:$version $registry/$tag:$version

  echo "Pushing $tag:$version"

  docker push $registry/$tag:$version

  echo "Pushed successfully"
}

if [[ $# -ne 2 ]]; then
  echo "Usage: ./build.sh DIRECTORY VERSION"
  echo "  -> will build image with DIRECTORY/Dockerfile and tag with VERSION"
  exit 0
fi

build_and_push $1 $2
