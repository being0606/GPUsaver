# 🚦 GPUsaver

공용 서버 환경에서 GPU 상태를 모니터링하고, 변경 사항을 Slack으로 알리고, 사용 현황을 시각화하는 경량 도구입니다.


## ✨ 핵심 기능

- **GPU 상태 로깅**: `gpustat`을 사용하여 주기적으로 GPU 상태(사용률, 메모리, 온도 등)를 JSONL 형식으로 기록합니다.
- **Slack 알림**: 사용 가능한 GPU 개수에 변동이 생길 때마다 지정된 사용자에게 Slack DM으로 알림을 보냅니다.
- **실시간 시각화**: Weights & Biases (wandb)와 연동하여 GPU 사용 현황을 실시간 그래프로 시각화합니다.
- **다중 머신 지원**: `--machine-name` 인자를 통해 여러 서버의 GPU 상태를 개별적으로 모니터링할 수 있습니다.


## 🖼️ 시각화 예시

<p align="center">
  <img src="asset/visualize_memory.png" alt="GPU 메모리 사용량" width="600"/>
  <br/><em>GPU 메모리 사용량</em>
</p>

<p align="center">
  <img src="asset/visualize_power.png" alt="GPU 전력 소비량" width="600"/>
  <br/><em>GPU 전력 소비량</em>
</p>

<p align="center">
  <img src="asset/visualize_utilization.png" alt="GPU 사용률" width="600"/>
  <br/><em>GPU 사용률</em>
</p>




## 💿 설치

1.  **저장소 복제**
```bash
git clone https://github.com/isl-hjlim/GPUsaver.git
cd GPUsaver
```


2.  **Create and activate the Conda environment.**
```bash
conda create -n GPUsaver python=3.11 -y
conda activate GPUsaver
```

3. **Install required packages**
```bash
pip install -r requirements.txt
```


## 🚀 Usage

```bash
script/get_statue.sh # GPU 상태 로깅 시작 (e.g., ./script/get_statue.sh --machine-name A6000)
script/run_guardian.sh # GPU 상태 변경 알림 시작 (e.g., ./script/run_guardian.sh --machine-name A6000)
script/run_visualize.sh # GPU 상태 시각화 (e.g., ./script/run_visualize.sh --logfile logs/log_gpustat_A6000.jsonl)
```

### ⚠️ Make sure you are logged into Weights & Biases if you want to use visualization:
```bash
wandb login
```

### 📁 Directory Structure

```
GPUsaver/
├── script/
│   ├── get_status.sh
│   └── run_visualize.sh
├── requirements.txt
└── README.md
```