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
| 학습 스모크 테스트 (2 / 20 epoch) | ✅ | 2026-09-18 |
| 학습 (train, 2000 epoch) | ✅ | 2026-09-18 |
| **평가 (eval)** | ⬜ **미시작** | — |

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

> ⚠️ `--dataset_dir`에 `dataset` 같은 상대경로를 주면 `act/dataset/`에 **새로 생성**된다.
> 2026-09-18에 이걸로 368 MB짜리 `episode_0.hdf5`를 잘못 만들었다 (삭제함).
> 항상 `$ALOHA_DATA_DIR/...` 또는 `../aloha_data/...`로 지정할 것.

### 3) 새로 추가한 스크립트 2개

원본에 없던 파일이라 `act.patch`(diff)에는 안 잡힌다.
→ 원본을 [`patches/act-extra/`](../patches/act-extra/)에 따로 백업해 둠.

| 파일 | 용도 |
|------|------|
| `play_video.py` | 저장된 mp4 재생 (레포에 재생 코드가 없음). `q`로 종료 |
| `model_test.py` | `dm_control` viewer로 시뮬 환경 띄워보기 |

```bash
cp ~/aloha_project/aloha-study-log/patches/act-extra/*.py ~/aloha_project/act/   # 복구
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

## 학습 스모크 테스트 (2026-09-18)

2000 epoch를 바로 걸기 전에 짧게 돌려서 VRAM과 속도를 먼저 확인함.
전체 과정은 [logs/2026-09-18.md](../logs/2026-09-18.md).

```bash
conda activate act
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
mkdir -p ~/aloha_project/ckpt/smoke_test20
cd ~/aloha_project/act

python3 -u imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/smoke_test20 \
  --policy_class ACT --kl_weight 10 --chunk_size 100 \
  --hidden_dim 512 --batch_size 8 --dim_feedforward 3200 \
  --num_epochs 20 --lr 1e-5 --seed 0
```

| 항목 | 값 |
|------|-----|
| GPU | RTX 2080 Ti (11,264 MiB) |
| 최대 VRAM | **4,840 MiB** (베이스라인 913 MiB 포함 → 학습 순수 사용 ≈ 3.9 GB) |
| 여유 | 약 6.4 GB → **`batch_size 8`에서 OOM 없음. 낮출 필요 없음** |
| 1 epoch 소요 | **약 1.09 초** (정상 상태). 초기 2~3 epoch는 워밍업으로 2~3.5초 |
| 2000 epoch 환산 | **약 37~40분** |
| CPU RAM 최대 | 1.7 GB |
| 파라미터 수 | 83.92 M |
| 20 epoch 후 val loss | 0.854 (@ epoch 19), 시작 67.9 → 학습 정상 동작 |

### ⭐ epoch 1회 = 데이터 전체 1회가 아님

`utils.py`의 `EpisodicDataset.__len__`이 **에피소드 개수(50)** 를 반환하고,
`__getitem__`은 에피소드당 **랜덤 타임스텝 1개만** 뽑는다.

```python
def __len__(self):
    return len(self.episode_ids)      # 50 (스텝 수 400×50 = 20,000이 아님)
```

→ 1 epoch = 45 샘플 ≈ 6 배치뿐이라 1초 남짓에 끝난다. 2000 epoch를 다 돌려도
각 (에피소드, 타임스텝) 조합을 전부 보는 것과는 거리가 멀다.
저자 튜닝 문서의 "loss가 평평해진 뒤에도 더 학습하면 성공률이 계속 오른다"는 말과
일치하는 구조 → **성공률이 기대치(≈90%)보다 낮으면 epoch를 늘리는 게 가장 싼 선택지**
(5000 epoch ≈ 100분).

### 체크포인트 저장 주기

`imitate_episodes.py:380`에서 **100 epoch마다** 저장한다 (`if epoch % 100 == 0`).

| | |
|---|---|
| 체크포인트 1개 | 336 MB |
| 2000 epoch 시 | 21개 + `policy_best` / `policy_last` ≈ **약 7 GB** |

평가는 `policy_best.ckpt`를 불러오므로 중간 체크포인트는 학습 곡선 비교용이 아니면
나중에 지워도 된다.

### 기타

- ResNet18 pretrained 가중치(44.7 MB)를 최초 실행 시 1회 다운로드함
  (`~/.cache/torch/hub/checkpoints/`). 이후 실행에서는 생략됨.
- torchvision `pretrained` deprecated 경고가 뜨지만 동작에는 무해.

---

## 다음 단계

학습/평가 명령어는 [NEXT.md](../NEXT.md)에 복붙할 수 있게 정리해둠.

## 학습 결과 (2000 epoch)

| 항목 | 값 |
|------|-----|
| 실행 날짜 | **2026-09-18** (14:55 ~ 15:33) |
| 하이퍼파라미터 | `kl_weight=10, chunk_size=100, hidden_dim=512, batch_size=8, dim_feedforward=3200, num_epochs=2000, lr=1e-5, seed=0` (전부 저자 기본값) |
| 1 epoch 소요 시간 | **1.15초** (스모크 테스트 예상 1.09초) |
| 전체 소요 시간 | **38분 10초** (예상 37~40분 — 적중) |
| 최소 validation loss / 해당 epoch | **0.045839 @ epoch 1995** |
| 최종 train loss | 0.136 (l1 0.041 / kl 0.010) |
| 최대 VRAM 사용량 | 4,840 MiB / 11,264 MiB |
| 체크포인트 | 23개, 7.2 GB, `~/aloha_project/ckpt/sim_transfer_cube_scripted_act/` |
| 평가 성공률 (temporal_agg 끔) | (미측정) |
| 평가 성공률 (temporal_agg 켬) | (미측정) |

### ⚠️ val loss가 아직 수렴하지 않았음

200 epoch 구간별 최소 val loss (`train.log` 파싱, 스크립트는 [logs/2026-09-18.md](../logs/2026-09-18.md)):

| 구간 | 최소 val loss | | 구간 | 최소 val loss |
|------|------|---|------|------|
| 0–199 | 0.19662 | | 1000–1199 | 0.06958 |
| 200–399 | 0.10798 | | 1200–1399 | 0.06262 |
| 400–599 | 0.12046 | | 1400–1599 | 0.06335 |
| 600–799 | 0.10186 | | 1600–1799 | 0.04663 |
| 800–999 | 0.08426 | | **1800–1999** | **0.04584** |

best epoch가 **1995**로 거의 마지막이고, 마지막 500구간이 직전 대비 27% 더 내려갔다
(0.06262 → 0.04584). **2000 epoch는 부족했을 가능성이 크다.**

→ 평가 성공률이 기대치(≈90%)에 못 미치면 **하이퍼파라미터보다 `--num_epochs 5000`을 먼저** 시도.
1 epoch = 45 샘플뿐이라 5000 epoch도 약 96분이면 끝난다.
저자 튜닝 문서의 "loss가 평평해진 뒤에도 더 학습하면 성공률이 계속 오른다"와 방향이 일치한다.
