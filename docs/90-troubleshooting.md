# 90. 트러블슈팅 모음

막혔던 것과 해결 방법. **새로 에러를 만나면 아래 템플릿 형식으로 계속 추가할 것.**

---

## #1. `act`의 `DATA_DIR`이 플레이스홀더라 동작하지 않음

**증상** — 데이터 경로를 못 찾음. `act/constants.py`가 이 상태:

```python
DATA_DIR = '<put your data dir here>'
```

**원인** — 사용자가 직접 채우도록 비워둔 자리. 안 채우면 `<put your data dir here>/...`라는
존재하지 않는 경로를 그대로 사용하게 됨.

**해결** — 환경변수 + 기본값으로 교체 (`patches/act.patch`)

```python
import os
DATA_DIR = os.environ.get('ALOHA_DATA_DIR', os.path.expanduser('~/aloha_project/aloha_data'))
```

```bash
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
```

---

## #2. `act-plus-plus`에 저자 개인 경로가 하드코딩됨

**증상** — `act-plus-plus/constants.py`의 원본:

```python
DATA_DIR = '/home/zfu/interbotix_ws/src/act/data' if os.getlogin() == 'zfu' else '/scr/tonyzhao/datasets'
```

내 계정은 `zfu`가 아니므로 `/scr/tonyzhao/datasets`를 보게 되는데 그런 경로는 없음.

**원인** — 저자들이 자기 머신 두 대를 구분하려고 넣은 코드가 그대로 릴리스됨.

**해결** — #1과 똑같이 환경변수로 통일. 두 repo가 같은 `ALOHA_DATA_DIR`을 보게 되어
데이터를 공유할 수 있다는 부수 효과도 있음.

**추가 메모** — `os.getlogin()`은 제어 터미널이 없는 환경(cron, 일부 컨테이너, 특정 tmux 상황)에서
`OSError`를 던지는 경우가 있음. 경로 문제와 별개로 걷어내는 게 안전함.

---

## #3. `ImportError: cannot import name 'ConditionalUnet1D'` (act-plus-plus)

**증상** — `act-plus-plus/policy.py`를 import하는 순간 실패:

```python
from robomimic.algo.diffusion_policy import replace_bn_with_gn, ConditionalUnet1D
```

**원인** — act-plus-plus는 2024년 1월 기준 robomimic에 맞춰 작성됐는데, 설치된 robomimic은
0.5.0 (커밋 `d309eae`, 2026-08). 그 사이에 `ConditionalUnet1D`가
`robomimic.algo.diffusion_policy` → `robomimic.models.diffusion_policy_nets`로 **이동**했음.
`replace_bn_with_gn`은 원래 자리에 그대로 있어서, 두 개를 한 줄로 import하던 게 통째로 깨진 것.

**해결** — import를 두 줄로 쪼개서 각각 올바른 모듈에서 가져옴 (`patches/act-plus-plus.patch`)

```python
from robomimic.algo.diffusion_policy import replace_bn_with_gn
from robomimic.models.diffusion_policy_nets import ConditionalUnet1D
```

**교훈** — 오래된 연구 코드 + 최신 의존성 조합에서는 이런 이동/삭제가 계속 나옴.
`ImportError`가 나면 먼저 설치된 패키지에서 심볼의 현재 위치를 찾아볼 것:

```bash
grep -rn "class ConditionalUnet1D" ~/aloha_project/robomimic/
```

---

## #4. 데이터 생성이 중간에 끊기면 처음부터 다시 시작됨

**증상** — `record_sim_episodes.py`는 항상 `episode_0`부터 생성. 50 에피소드 생성에 오래 걸리는데
(실제로 2026-09-16 16:05 ~ 09-17 10:41 소요) 중간에 멈추면 이미 만든 것도 덮어쓰며 처음부터 다시 함.

**원인** — 원본 코드가 `for episode_idx in range(num_episodes)`로 0부터 고정.

**해결** — `--start_idx` 인자를 추가 (`patches/act.patch`)

```python
parser.add_argument('--start_idx', type=int, default=0)
...
for episode_idx in range(start_idx, start_idx + num_episodes):
```

이어서 생성하는 법 — 먼저 몇 개까지 됐는지 확인:

```bash
ls $ALOHA_DATA_DIR/sim_transfer_cube_scripted/*.hdf5 | wc -l
```

30개까지 됐다면 나머지 20개:

```bash
python3 record_sim_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted \
  --num_episodes 20 --start_idx 30
```

> ⚠️ 마지막 에피소드는 생성 도중에 끊겨 **깨져 있을 수 있음**. 이어서 만들기 전에 마지막 파일을
> 지우고 그 번호부터 다시 만드는 게 안전함 (파일 크기가 368 MB가 아니면 미완성).

---

## #5. WSL에서 MuJoCo viewer가 안 뜸 — `Attempt to retrieve context when no valid context`

**증상** — `model_test.py`처럼 `dm_control` viewer를 띄우려 하면:

```
OpenGL.error.Error: Attempt to retrieve context when no valid context
```

**원인** — WSLg는 `WAYLAND_DISPLAY`를 자동으로 설정해둔다. PyOpenGL이 이 변수를 보고
백엔드를 **EGL**로 추측하는데(`OpenGL/platform/__init__.py:36`), 정작 GLFW는
**X11/GLX** 컨텍스트를 만든다. 서로 어긋나서 `eglGetCurrentContext()`가 `None`을 반환.

**해결** — `~/.bashrc`에 3줄 추가 (→ [00-environment.md](00-environment.md) "WSLg 렌더링 설정")

```bash
export MUJOCO_GL=glfw
export PYOPENGL_PLATFORM=glx
export GALLIUM_DRIVER=d3d12
```

**교훈** — WSL에서 GUI/OpenGL이 이상하면 "렌더링을 포기"하기 전에 백엔드 불일치를 먼저 의심할 것.
`MUJOCO_GL`(MuJoCo용)과 `PYOPENGL_PLATFORM`(PyOpenGL용)은 **별개 변수**라 둘 다 맞춰줘야 한다.

---

## #6. 렌더링이 GPU가 아니라 CPU(llvmpipe)로 돌고 있었음

**증상** — 에러는 안 나지만 렌더링이 유난히 느림. 확인해보니:

```bash
glxinfo -B | grep "OpenGL renderer"
# → OpenGL renderer string: llvmpipe (LLVM 20.1.2, 256 bits)
```

**원인** — CUDA는 정상인데(`torch.cuda.is_available() == True`) **OpenGL만** 소프트웨어
래스터라이저를 쓰고 있었다. WSLg용 하드웨어 드라이버 `d3d12_dri.so`는 설치돼 있는데 자동 선택이 안 됨.

**해결** — `export GALLIUM_DRIVER=d3d12`

| 백엔드 | RENDERER | MuJoCo 오프스크린 렌더링 (480×640) |
|--------|----------|-----------------------------------|
| 기본 | llvmpipe (LLVM 20.1.2) | 33.3 fps |
| `GALLIUM_DRIVER=d3d12` | D3D12 (NVIDIA GeForce RTX 2080 Ti) | **156.7 fps** |

약 **4.7배** 차이. 데이터 생성과 평가(`--eval`) 시간이 그만큼 줄어든다.

**교훈** — `MESA_LOADER_DRIVER_OVERRIDE=d3d12`는 효과가 없고 `GALLIUM_DRIVER=d3d12`만 동작했다.
그리고 **CUDA가 된다고 OpenGL도 GPU를 쓰는 건 아니다.** 둘은 완전히 다른 경로라 따로 확인해야 함.

---

## #7. `--dataset_dir`에 상대경로를 주면 엉뚱한 곳에 데이터가 생성됨

**증상** — 아래처럼 실행했더니 `act/dataset/episode_0.hdf5` (368 MB)가 새로 생성됨.

```bash
python3 record_sim_episodes.py --task_name sim_transfer_cube_scripted \
  --dataset_dir dataset --num_episodes 50 --onscreen_render
```

**원인** — `--dataset_dir`은 **읽는 곳이 아니라 쓰는 곳**이다. 없으면 만들어서 처음부터 생성한다.
`constants.py`의 `DATA_DIR`(= `ALOHA_DATA_DIR`)과는 별개 인자라 자동으로 이어지지 않는다.

**해결** — 항상 절대경로 또는 `$ALOHA_DATA_DIR` 기준으로 지정:

```bash
--dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted     # 어디서 실행하든 안전
--dataset_dir ../aloha_data/sim_transfer_cube_scripted       # act/ 안에서 실행할 때
```

**교훈** — 18 GB짜리 작업을 다루는 스크립트는 경로를 잘못 주면 조용히 새로 만들기 시작한다.
실행 직후 `ls -la` 로 **의도한 곳에 쓰이고 있는지** 한 번 확인하는 습관이 필요.

---

## 아직 겪지 않았지만 대비해둘 것

### ~~`CUDA out of memory` (학습 시)~~ → 해소됨 (2026-09-18)
실측 결과 `--batch_size 8`에서 **4,840 MiB / 11,264 MiB**만 사용. 여유 6.4 GB.
`--batch_size 4`로 낮출 필요 없음. 단, `chunk_size`나 `hidden_dim`을 키우면 다시 확인할 것.

### ~~WSL2에서 `--onscreen_render` 실패~~ → 해결됨, 위 #5 / #6 참고
(당시 메모였던 `MUJOCO_GL=egl` / `osmesa` 시도는 결과적으로 정답이 아니었음.
정답은 `glfw` + `PYOPENGL_PLATFORM=glx` + `GALLIUM_DRIVER=d3d12` 조합)

### 디스크 부족
에피소드 1개 = 368 MB, 태스크 1개(50 ep) = 18 GB. 체크포인트도 학습 1회당 7.2 GB.
새 태스크 시작 전에 `df -h ~` 확인.

---

## 새 항목 템플릿

```markdown
## #N. (한 줄 요약)

**증상** — (에러 메시지 원문 붙여넣기)

**원인** — (왜 그런지)

**해결** — (실제로 한 조치, 명령어/코드 포함)

**교훈** — (다음에 비슷한 걸 만나면 어떻게 할지)
```
