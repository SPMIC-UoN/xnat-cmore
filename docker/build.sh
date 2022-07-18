#!/bin/bash

cp Dockerfile.in Dockerfile
python scripts/cmd2label.py cmore_preproc_cmd.json >> Dockerfile

tag=0.0.2
docker build -t martincraig/xnat-cmore .
docker tag martincraig/xnat-cmore martincraig/xnat-cmore:$tag 
docker push martincraig/xnat-cmore:$tag
docker push martincraig/xnat-cmore:latest
