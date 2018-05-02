#!/bin/bash

docker build -f builder-gcc/Dockerfile . -t talk4u/treadmill-builder-gcc:v0.1.0
docker build -f builder-go110/Dockerfile . -t talk4u/treadmill-builder-go110:v0.1.0
docker build -f builder-jdk8/Dockerfile . -t talk4u/treadmill-builder-jdk8:v0.1.0
docker build -f sandbox/Dockerfile . -t talk4u/treadmill-sandbox:v0.1.0
docker build -f sandbox-jre8/Dockerfile . -t talk4u/treadmill-sandbox-jre8:v0.1.0
docker build -f sandbox-py36/Dockerfile . -t talk4u/treadmill-sandbox-py36:v0.1.0
