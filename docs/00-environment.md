# 00. 환경 구축

작업일: **2026-09-16** · 상태: ✅ 완료

## 하드웨어 / OS

| 항목 | 값 |
|------|-----|
| GPU | NVIDIA GeForce RTX 2080 Ti (VRAM **11,264 MiB ≈ 11 GB**) |
| NVIDIA 드라이버 | 610.62 |
| OS | WSL2 (Linux 6.18.33.2-microsoft-standard-WSL2) |
| 작업 루트 | `~/aloha_project/` |

> 💡 VRAM 11 GB는 ACT 기본 설정(`batch_size 8`)에 빠듯할 수 있음. OOM 시 `--batch_size 4`로.
> ⚠️ WSL2에서는 on-screen rendering(`--onscreen_render`)이 X 서버/WSLg 설정에 따라 실패할 수 있으니,
> 렌더링 없이 돌리는 걸 기본으로 하고 결과는 저장된 mp4로 확인하는 편이 안전함.

## conda 환경 2개

용도가 다르므로 **섞어 쓰지 말 것**.

| env | 용도 | Python |
|-----|------|--------|
| `act` | `act` repo (ACT 원본) 실행용 | 3.8.10 |
| `aloha` | `act-plus-plus` (Diffusion Policy, robomimic 필요) 실행용 | 3.8.10 |

```bash
conda activate act     # ACT 실습할 때
conda activate aloha   # act-plus-plus 실습할 때
```

## 설치된 주요 패키지 버전 (양쪽 공통)

| 패키지 | 버전 |
|--------|------|
| torch | 2.4.1+cu121 (CUDA 12.1, `cuda.is_available() == True`) |
| torchvision | 0.19.1+cu121 |
| mujoco | 2.3.7 |
| dm-control | 1.0.14 |
| numpy | 1.24.4 |
| h5py | 3.11.0 |
| einops | 0.8.1 |
| packaging | 26.2 |

`aloha` env에만 추가로:

| 패키지 | 버전 |
|--------|------|
| robomimic | 0.5.0 (`~/aloha_project/robomimic`에서 **editable** 설치) |
| diffusers | 0.11.1 |
| wandb | 0.24.2 |

> `mujoco==2.3.7`, `dm_control==1.0.14`는 원본 README가 지정한 버전. 시뮬 환경이 이 버전에 맞춰져
> 있으니 함부로 올리지 말 것.

전체 목록은 [`patches/requirements-act.txt`](../patches/requirements-act.txt),
[`patches/requirements-aloha.txt`](../patches/requirements-aloha.txt)에 `pip freeze`로 보관되어 있음.

## 처음부터 다시 만들어야 할 때

원본 README(`act/README.md`)의 설치 순서 + 실제 설치된 버전을 합친 것:

```bash
conda create -n act python=3.8.10 -y
conda activate act

pip install torch torchvision          # CUDA 12.1 빌드 사용
pip install pyquaternion pyyaml rospkg pexpect
pip install mujoco==2.3.7
pip install dm_control==1.0.14
pip install opencv-python matplotlib einops packaging h5py ipython

cd ~/aloha_project/act/detr && pip install -e .
```

`aloha` env (act-plus-plus용)는 위에 더해서:

```bash
conda create -n aloha python=3.8.10 -y
conda activate aloha
# ... 위와 동일하게 설치 후 ...
pip install diffusers==0.11.1 wandb
cd ~/aloha_project/robomimic && pip install -e .    # editable 설치
cd ~/aloha_project/act-plus-plus/detr && pip install -e .
```

정확한 버전 그대로 복원하려면:

```bash
pip install -r ~/aloha_project/aloha-study-log/patches/requirements-act.txt
```

## 환경변수

원본 코드의 하드코딩된 데이터 경로를 환경변수로 바꿔뒀음
(→ [90-troubleshooting.md](90-troubleshooting.md) #1, #2 참고).

```bash
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
```

매번 치기 귀찮으면 `~/.bashrc`에 추가:

```bash
echo 'export ALOHA_DATA_DIR=$HOME/aloha_project/aloha_data' >> ~/.bashrc
```

설정 안 해도 기본값이 `~/aloha_project/aloha_data`라서 동작하지만, 데이터를 다른 디스크로
옮길 경우를 대비해 명시적으로 잡아두는 걸 권장.
