#!/bin/bash

cp Dockerfile.in Dockerfile
python ../cmd2label.py ukat_t2star_cmd.json ukat_b0_cmd.json cmore_preproc_cmd.json >> Dockerfile

tag=0.0.1
docker build -t martincraig/xnat-cmore .
docker tag martincraig/xnat-cmore martincraig/xnat-cmore:$tag 
docker push martincraig/xnat-cmore:$tag
