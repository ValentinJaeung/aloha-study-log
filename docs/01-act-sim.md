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
| 개념 정리 (데모 생성 구조 / 무엇을 학습하는가) | ✅ | 2026-09-18 |
| 평가 (eval) | ✅ **성공률 94% / 98%** | 2026-09-18 |

> 코드를 돌리기 전에 **"시뮬에서 팔은 누가 움직이고, 정책은 무엇을 배우는가"**가 궁금하다면
> 맨 아래 [⭐ 개념 정리](#-개념-정리-시뮬에서-데모는-누가-만들고-정책은-무엇을-배우는가) 섹션부터 읽을 것.

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
| 평가 성공률 (temporal_agg 끔) | **94%** (47/50) |
| 평가 성공률 (temporal_agg 켬) | **98%** (49/50) |

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

> ✅ **후속**: 실제로 평가해보니 **94% / 98%** 로 기대치를 넘겼다.
> val loss가 수렴하지 않았는데도 충분한 성능이 나왔으므로 **5000 epoch 재학습은 불필요**해졌다.
> "loss를 더 낮춰야 성공률이 오른다"는 직관이 항상 맞지는 않는다는 사례.

---

## 평가 결과 (2026-09-18)

```bash
conda activate act
# ⚠️ 비대화형 셸에서는 ~/.bashrc가 적용 안 되므로 렌더링 변수를 명시적으로 export
export ALOHA_DATA_DIR=~/aloha_project/aloha_data \
       MUJOCO_GL=glfw PYOPENGL_PLATFORM=glx GALLIUM_DRIVER=d3d12
cd ~/aloha_project/act

python3 -u imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/sim_transfer_cube_scripted_act \
  --policy_class ACT --kl_weight 10 --chunk_size 100 --hidden_dim 512 \
  --batch_size 8 --dim_feedforward 3200 --num_epochs 2000 --lr 1e-5 --seed 0 \
  --eval                    # 2회차는 여기에 --temporal_agg 추가
```

`policy_best.ckpt`(epoch 1995)를 불러와 **50회 rollout** (`imitate_episodes.py:198`).

| | temporal_agg 끔 | temporal_agg 켬 |
|---|---|---|
| **Success rate** | **0.94** (47/50) | **0.98** (49/50) |
| Average return | 592.66 | **669.04** |
| 소요 시간 | 9분 32초 | 15분 19초 |

**temporal ensembling이 +4%p, average return은 +13%.** 대신 시간이 1.6배.
매 스텝 추론하기 때문이다 (끄면 `chunk_size`=100 스텝마다 1회, 즉 rollout당 4회).

### 보상 단계별 분포 — 실패가 어디서 나는가

`sim_transfer_cube`의 최대 보상은 4이고 단계마다 1씩 오른다.

| 도달 보상 | 의미 | agg 끔 | agg 켬 |
|---|---|---|---|
| ≥ 1 | 오른팔이 큐브에 접촉 | 48/50 (96%) | **50/50 (100%)** |
| ≥ 2 | 큐브를 집어 듦 | 48/50 (96%) | 49/50 (98%) |
| ≥ 3 | 왼팔로 전달 시도 | 47/50 (94%) | 49/50 (98%) |
| ≥ 4 | **전달 성공(= 성공 판정)** | 47/50 (94%) | 49/50 (98%) |

- **실패는 거의 전부 파지(grasp) 단계에 몰려 있다.** 일단 집으면 전달은 사실상 따라온다
  (agg 끔 48→47, agg 켬 49→49).
- temporal_agg가 개선한 지점도 정확히 거기다. 접촉 실패 2건이 0건이 됐다.
  여러 chunk의 예측을 가중 평균하므로 **접근 궤적이 매끄러워져** 초기 정렬이 좋아진 것으로 보인다.

### ⚠️ 평가를 두 번 돌릴 때 주의

`eval_bc(save_episode=True)`가 rollout 영상을 `ckpt_dir`에 **`video0.mp4` ~ `video49.mp4` 고정 이름**으로
저장한다. 2회차를 그냥 돌리면 1회차 영상이 전부 덮어써진다.

```bash
cd ~/aloha_project/ckpt/sim_transfer_cube_scripted_act
mkdir -p rollouts_no_agg && mv *.mp4 rollouts_no_agg/     # 2회차 돌리기 전에
```

현재 `rollouts_no_agg/`(310 MB), `rollouts_temporal_agg/`(309 MB)로 분리 보관 중.

---

## ⭐ 개념 정리: 시뮬에서 데모는 누가 만들고, 정책은 무엇을 배우는가

> 2026-09-18 정리. "teleoperation으로 사람이 직접 조작하는 것도 아닌데 시뮬 안에서 팔이
> 어떻게 움직이는 거지? 코드가 움직인 거면 학습에 의미가 있나?"라는 의문을 코드로 확인한 내용.

### 0. 대전제 — ACT는 강화학습이 아니라 지도학습이다

ACT는 **행동 복제(behavior cloning)** 다. 보상을 받아가며 스스로 시행착오하는 게 아니라,
이미 만들어진 (관측 → 행동) 쌍을 **지도학습으로 회귀**할 뿐이다.
`policy.py`의 손실 함수가 그 증거다.

```python
all_l1 = F.l1_loss(actions, a_hat, reduction='none')     # 정답 action과의 L1 거리
loss_dict['loss'] = loss_dict['l1'] + loss_dict['kl'] * self.kl_weight
```

보상 항이 없다. 시뮬의 `reward`는 **데모가 성공했는지 판정하고 eval 성공률을 재는 용도**로만
쓰이고 학습에는 전혀 들어가지 않는다 (`record_sim_episodes.py`에서 `episode_max_reward`를
성공/실패 출력에만 쓰는 것으로 확인).

→ 따라서 **데모를 사람이 만들든 코드가 만들든 학습 구조는 완전히 동일하다.** 바뀌는 건
데이터의 "질"뿐이다.

### 1. 시뮬에서 팔이 움직이는 원리 — mocap body가 "사람 손" 역할

실기 teleoperation은 *사람이 leader 팔을 손으로 끌면 → follower 팔이 따라가는* 구조다.
시뮬에서는 이 **사람 손 자리에 MuJoCo의 mocap body**가 들어간다.

`assets/bimanual_viperx_ee_transfer_cube.xml:6-7`:

```xml
<weld body1="mocap_left"  body2="vx300s_left/gripper_link"  solref="0.01 1" solimp=".25 .25 0.001" />
<weld body1="mocap_right" body2="vx300s_right/gripper_link" solref="0.01 1" solimp=".25 .25 0.001" />
```

mocap body는 **물리법칙을 무시하고 지정 좌표로 순간이동하는 "유령 손잡이"** 이고,
그게 로봇 손목(`gripper_link`)에 **weld(용접) 구속**으로 붙어 있다.
`ee_sim_env.py:58-74`가 매 스텝 이 손잡이를 옮긴다.

```python
def before_step(self, action, physics):
    np.copyto(physics.data.mocap_pos[0],  action_left[:3])    # 위치 xyz
    np.copyto(physics.data.mocap_quat[0], action_left[3:7])   # 자세 quaternion
```

여기서 action은 **관절각이 아니라 엔드이펙터의 xyz + quaternion (7차원 × 2팔 = 14)** 이다.
손잡이를 끌면 weld 구속을 만족시키려고 **물리 솔버가 알아서 관절을 풀어준다.**

> 즉 **IK를 직접 푸는 코드가 없다.** 물리 시뮬레이터가 대신 풀어주는 것이고,
> 이게 사람이 leader 팔을 손으로 끄는 것과 물리적으로 같은 상황이다.

### 2. 그 손잡이를 끄는 건 `scripted_policy.py`의 waypoint 테이블

`scripted_policy.py:88-98` (`PickAndTransferPolicy`) — 시간축 키프레임 몇 개가 전부다.

```python
{"t": 90,  "xyz": box_xyz + np.array([0, 0, 0.08]),   ..., "gripper": 1},  # 큐브 위로 접근
{"t": 130, "xyz": box_xyz + np.array([0, 0, -0.015]), ..., "gripper": 1},  # 내려감
{"t": 170, "xyz": box_xyz + np.array([0, 0, -0.015]), ..., "gripper": 0},  # 그리퍼 닫기
{"t": 200, "xyz": meet_xyz + np.array([0.05, 0, 0]),  ..., "gripper": 0},  # 만나는 지점으로
```

`BasePolicy.interpolate()` (`scripted_policy.py:23-36`)가 키프레임 사이를 **선형보간**해서
매 스텝 명령을 만든다. 사람이 손으로 그리던 궤적을 코드가 직선 몇 개로 대신 그리는 셈.

| | 실기 ALOHA | 시뮬 |
|---|---|---|
| 궤적을 만드는 주체 | 사람 (teleoperation) | `scripted_policy.py`의 waypoint |
| 팔에 전달되는 매개 | leader 팔 (사람이 손으로 잡음) | mocap body (weld 구속) |
| 관절각을 푸는 주체 | 실제 물리 (사람 팔 → 링크) | MuJoCo 물리 솔버 |
| 저장되는 데이터 | 이미지 + qpos + action | **동일** |

### 3. 데이터 수집이 왜 2단계인가 (`record_sim_episodes.py`의 핵심)

`record_sim_episodes.py`는 한 에피소드를 만들 때 시뮬을 **두 번** 돌린다.
처음 봤을 때 제일 헷갈렸던 부분인데 이유가 명확하다.

```
[1단계] ee_sim_env + scripted policy 실행  →  결과로 나온 관절 궤적 qpos 를 기록
                                               (record_sim_episodes.py:74-82)
              ↓  EE 궤적을 관절 궤적으로 "번역"
[2단계] sim_env 에서 그 관절 궤적을 action 으로 재생 → 이미지/qpos 를 기록
                                               (record_sim_episodes.py:96-110)
```

**이유**: 실제 ALOHA에서 기록되는 데이터는 EE pose가 아니라
**leader 팔의 관절각 = follower에게 내려가는 목표 관절각**이다.
1단계의 EE 제어는 데모를 *만들기 위한 수단*일 뿐이고, 저장되는 데이터 포맷은
**실기 teleoperation 데이터와 1:1로 같아야** 한다. 그래서 굳이 관절 궤적으로 바꿔
다시 돌려서 기록한다.

2단계에서 `BOX_POSE[0] = subtask_info`로 1단계와 **같은 물체 배치를 강제**하는 것도 이 때문
(`sim_env.py:18`의 전역 변수를 밖에서 세팅하는 구조).

결과적으로 hdf5에 남는 건 이것뿐이다 — **EE pose도, 물체 좌표도 안 들어간다.**

| 키 | 내용 |
|---|---|
| `observations/images/top` | 카메라 픽셀 (400, 480, 640, 3) uint8 |
| `observations/qpos` | 현재 관절각 (400, 14) |
| `observations/qvel` | 관절 속도 (400, 14) |
| `action` | 다음 목표 관절각 (400, 14) |

### 4. ⭐ "코드가 움직인 건데 학습에 의미가 있나?" → 있다

**핵심은 스크립트와 정책이 보는 정보가 완전히 다르다는 것.**

스크립트는 `scripted_policy.py:73-74`에서 대놓고 커닝을 한다.

```python
box_info = np.array(ts_first.observation['env_state'])
box_xyz  = box_info[:3]      # 시뮬레이터 내부에서 큐브 정답 좌표를 그냥 꺼내옴
```

이건 **특권 정보(privileged information)** — 실제 로봇에는 존재하지 않는, 시뮬레이터만
아는 정답이다. 반면 학습되는 ACT 정책은 `policy.py:19`에서 보듯 **이미지와 qpos만** 받는다.

```python
def __call__(self, qpos, image, actions=None, is_pad=None):
    env_state = None      # ← 물체 좌표를 정책에는 주지 않는다
```

그리고 큐브 위치는 **에피소드마다 랜덤**이다 (`ee_sim_env.py:162` → `utils.py:133` `sample_box_pose()`,
`x ∈ [0.0, 0.2]`, `y ∈ [0.4, 0.6]`). 스크립트는 그 좌표를 받아서 풀지만,
정책은 **픽셀만 보고 큐브가 어디 있는지 추론해야** 한다.

> 즉 이 학습은 "코드가 시킨 대로 따라하기"가 아니라
> **정답을 아는 스크립트 → 카메라만 보는 신경망으로의 증류(distillation)** 다.

정책이 실제로 새로 획득하는 능력:

1. **시각적 물체 위치 추정** — 이미지에서 큐브가 어디 있는지 (ResNet18 backbone)
2. **visuomotor 매핑** — 시각 정보 + 현재 관절각 → 목표 관절각
3. **action chunking** — 한 번에 `num_queries`(= `chunk_size` 100) 스텝을 통째로 예측
   (`detr/models/detr_vae.py:54`의 `query_embed`)

스크립트는 이 중 **어느 것도 갖고 있지 않다.** 그래서 eval 성공률이 나온다는 건
네트워크가 스크립트 코드를 외운 게 아니라 시각-운동 정책을 새로 배웠다는 증거다.

### 5. 단, scripted 데이터의 한계

사람 데모에 있는 두 가지가 없다.

- **멀티모달리티** — 사람은 같은 상황에서 매번 조금씩 다른 궤적을 그리지만,
  스크립트는 큐브 좌표가 같으면 **항상 동일한 직선 보간 궤적**을 낸다.
  게다가 `record_sim_episodes.py:31`에 `inject_noise = False`가 **하드코딩**되어 있어
  변동성이 아예 0이다 (`scripted_policy.py`에는 `±0.01` 노이즈 주입 코드가 있는데 안 쓰임).
- **비정형성** — 사람 특유의 멈칫거림, 재시도, 속도 변화가 없다.

ACT의 CVAE 구조(style variable `z`, `policy.py:26-33`의 KL 항)는 원래 이 **멀티모달리티를
다루려고** 있는 건데, scripted 데이터는 거의 결정적이라 그 효용이 잘 드러나지 않는다.
논문에서 `sim_transfer_cube_scripted`가 `_human`보다 성공률이 높게 나오는 이유도 이것.

**정리**: 지금 하는 실습은 파이프라인 전체(데이터 생성 → 학습 → 평가)를 검증하는 데는 충분하다.
다만 알고리즘의 어려운 부분(멀티모달 데모 처리)은 덜 드러난다.
→ 이를 체감해 보는 실험은 [NEXT.md](../NEXT.md)의 "이후 후보"에 적어둠.
