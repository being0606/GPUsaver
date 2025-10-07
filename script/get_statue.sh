#!/bin/bash

# get_statue.sh 스크립트에 전달된 모든 인자를 get_statue.py로 전달합니다.
# 사용 예시:
# 1. 기본값(A6000)으로 실행:
#    ./script/get_statue.sh
# 2. 머신 이름 'H100'으로 지정하여 실행:
#    ./script/get_statue.sh --machine-name H100
# 3. 머신 이름과 인터벌을 함께 지정하여 실행:
#    ./script/get_statue.sh --machine-name H100 --interval 30

echo "Starting GPU monitoring..."
python src/get_statue.py --machine-name A6000