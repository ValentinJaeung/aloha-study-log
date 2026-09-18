# 00. 환경 구축

작업일: **2026-09-16** · 상태: ✅ 완료

## 하드웨어 / OS

| 항목 | 값 |
|------|-----|
| GPU | NVIDIA GeForce RTX 2080 Ti (VRAM **11,264 MiB ≈ 11 GB**) |
| NVIDIA 드라이버 | 610.62 |
| OS | WSL2 (Linux 6.18.33.2-microsoft-standard-WSL2) |
| 작업 루트 | `~/aloha_project/` |

> ✅ **VRAM 실측 (2026-09-18)**: ACT 기본 설정(`batch_size 8`)에서 **4,840 MiB**만 사용.
> 11 GB로 충분하며 `--batch_size 4`로 낮출 필요 없음. (당초 "빠듯할 수 있음" 우려는 해소됨)
> ✅ **WSLg 렌더링도 해결됨 (2026-09-18)**: 아래 [환경변수](#환경변수) 3줄로 on-screen rendering과
> GPU 가속 오프스크린 렌더링 모두 정상 동작. → [90-troubleshooting.md](90-troubleshooting.md) #5

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

### WSLg 렌더링 설정 ⭐ (2026-09-18 추가)

**이 3줄이 없으면** MuJoCo viewer가 OpenGL 오류로 안 뜨고, 떠도 CPU 소프트웨어 렌더링(llvmpipe)으로
떨어져 **4.7배 느려짐**. 현재 `~/.bashrc:135-137`에 들어가 있음.

```bash
export MUJOCO_GL=glfw
export PYOPENGL_PLATFORM=glx
export GALLIUM_DRIVER=d3d12
```

| 변수 | 역할 |
|------|------|
| `MUJOCO_GL=glfw` | MuJoCo가 on-screen(GLFW) 백엔드를 쓰도록 명시 |
| `PYOPENGL_PLATFORM=glx` | PyOpenGL이 WSLg의 `WAYLAND_DISPLAY`를 보고 EGL로 잘못 추측하는 것을 막음 |
| `GALLIUM_DRIVER=d3d12` | WSLg의 GPU 가속 드라이버(`d3d12_dri.so`)를 강제 선택 |

확인:

```bash
echo $GALLIUM_DRIVER                              # → d3d12
glxinfo -B | grep "OpenGL renderer"               # → D3D12 (NVIDIA GeForce RTX 2080 Ti)
```

`llvmpipe`가 나오면 소프트웨어 렌더링 중이라는 뜻. 자세한 원인과 벤치마크는
[90-troubleshooting.md](90-troubleshooting.md) #5 참고.

> 평가(`--eval`)와 데이터 생성은 렌더링을 하므로 이 설정의 영향을 크게 받음.
> **학습(train)은 렌더링을 하지 않아 무관.**
