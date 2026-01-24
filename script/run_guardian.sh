#!/bin/bash

# 이 스크립트는 call_guardian.py를 실행하고 모든 명령줄 인자를 전달합니다.
# 사용 예시:
# 1. 기본값(A6000)으로 실행:
#    ./script/run_guardian.sh
# 2. 머신 이름 'H100'으로 지정하여 실행:
#    ./script/run_guardian.sh --machine-name H100

echo "Starting GPU Guardian..."
python src/call_guardian.py --machine-name 3090
