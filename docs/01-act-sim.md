# 01. ACT 시뮬레이션 실습 (`act` repo)

- upstream: https://github.com/tonyzhaozh/act
- 로컬 경로: `~/aloha_project/act`
- clone한 커밋: `742c753` (2024-01-28, "Update README.md")
- conda env: **`act`**

## 진행 상태

| 단계 | 상태 | 날짜 |
|------|------|------|
| repo clone | ✅ | 2026-09-16 |
| 코드 수정 (데이터 경로, `--start_idx`) | ✅ | 2026-09-16 |
| 데이터 생성 50 에피소드 | ✅ | 2026-09-16 ~ 09-17 |
| 데이터 시각화 확인 | ✅ | 2026-09-16 |
| **학습 (train)** | ⬜ **미시작** | — |
| 평가 (eval) | ⬜ 미시작 | — |

---

## 내가 수정한 부분

diff 원본: [`patches/act.patch`](../patches/act.patch)
(복원: `cd ~/aloha_project/act && git apply ~/aloha_project/aloha-study-log/patches/act.patch`)

### 1) `constants.py` — 데이터 경로를 환경변수로

원본은 `DATA_DIR = '<put your data dir here>'` 라는 **플레이스홀더**여서 그대로 두면 동작하지 않음.

```python
import os
DATA_DIR = os.environ.get('ALOHA_DATA_DIR', os.path.expanduser('~/aloha_project/aloha_data'))
```

경로를 직접 박아넣지 않고 환경변수 + 기본값 형태로 둔 이유: 나중에 데이터를 다른 디스크로
옮겨도 코드를 안 고쳐도 되고, git diff가 내 홈 경로로 더러워지지 않기 때문.

### 2) `record_sim_episodes.py` — `--start_idx` 옵션 추가

원본은 항상 `episode_0`부터 다시 생성함. 생성이 중간에 끊기면 **처음부터 다시 돌려야 해서**
시작 인덱스를 지정할 수 있게 인자를 추가했음.

```python
parser.add_argument('--start_idx', type=int, default=0,
                    help='episode index to start from')
...
for episode_idx in range(start_idx, start_idx + num_episodes):
```

사용 예 — 30번까지 만들었고 나머지 20개를 이어서 만들 때:

```bash
python3 record_sim_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted \
  --num_episodes 20 --start_idx 30
```

---

## 실행한 명령

### 데이터 생성

```bash
conda activate act
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
cd ~/aloha_project/act

python3 record_sim_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted \
  --num_episodes 50
```

### 데이터 시각화

```bash
python3 visualize_episodes.py \
  --dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted \
  --episode_idx 0
```

→ `episode_0_video.mp4`, `episode_0_qpos.png`가 데이터 폴더에 생성됨. 큐브를 한쪽 팔이 집어서
반대쪽 팔로 넘기는 동작이 나오면 정상.

---

## 결과: 생성된 데이터셋

| 항목 | 값 |
|------|-----|
| 태스크 | `sim_transfer_cube_scripted` |
| 에피소드 수 | **50개** (`episode_0.hdf5` ~ `episode_49.hdf5`) |
| 파일 1개 크기 | 368,740,832 B ≈ **368 MB** (전부 동일) |
| 총 용량 | **약 18 GB** |
| 생성 기간 | 2026-09-16 16:05 ~ 2026-09-17 10:41 |
| 위치 | `~/aloha_project/aloha_data/sim_transfer_cube_scripted/` |

**파일 크기가 전부 똑같은 이유**: 에피소드 길이(400 스텝)와 이미지 해상도가 고정이고 압축 없이
저장되기 때문. `400 × 480 × 640 × 3 = 368,640,000 B`로 실제 파일 크기와 거의 정확히 일치함
→ 카메라 1대(`top`), 480×640 RGB, 400 스텝짜리 uint8 배열이 원본 그대로 들어 있다는 뜻.

> ⚠️ 태스크를 하나 더 추가할 때마다 18 GB씩 늘어남. 디스크 여유 확인 필요.
> 압축 저장 방법은 [NEXT.md](../NEXT.md)의 "열린 질문"에 적어둠.

---

## 다음 단계

학습/평가 명령어는 [NEXT.md](../NEXT.md)에 복붙할 수 있게 정리해둠.

## 학습 결과 기록란 (실행 후 채우기)

| 항목 | 값 |
|------|-----|
| 실행 날짜 | |
| 하이퍼파라미터 | `kl_weight=10, chunk_size=100, hidden_dim=512, batch_size=?, dim_feedforward=3200, num_epochs=?, lr=1e-5, seed=0` |
| 1 epoch 소요 시간 | |
| 전체 소요 시간 | |
| 최소 validation loss / 해당 epoch | |
| 최대 VRAM 사용량 | |
| 평가 성공률 (temporal_agg 끔) | |
| 평가 성공률 (temporal_agg 켬) | |
| 메모 | |
