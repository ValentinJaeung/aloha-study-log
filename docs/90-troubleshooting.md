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

## 아직 겪지 않았지만 대비해둘 것

### `CUDA out of memory` (학습 시)
RTX 2080 Ti는 VRAM 11 GB. 저자 기본값 `--batch_size 8`에서 터지면 `--batch_size 4`로.
(배치를 줄이면 수렴이 느려지므로 epoch 수를 늘려야 할 수 있음)

### WSL2에서 `--onscreen_render` 실패
MuJoCo 렌더링이 X 서버/OpenGL 설정을 타므로 WSL에서는 실패할 수 있음.
렌더링 없이 실행하고 저장된 mp4로 확인하는 쪽이 안전. 필요 시 `MUJOCO_GL=egl` 또는
`MUJOCO_GL=osmesa` 환경변수를 시도해볼 것.

### 디스크 부족
에피소드 1개 = 368 MB, 태스크 1개(50 ep) = 18 GB.
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
