# 02. act-plus-plus (Diffusion Policy)

- upstream: https://github.com/MarkFzp/act-plus-plus
- 로컬 경로: `~/aloha_project/act-plus-plus`
- clone한 커밋: `26bab07` (2024-01-10, "fix sim demo generation issue")
- conda env: **`aloha`** ← `act` env가 아님, 주의!

## 이게 뭔가

Mobile ALOHA 논문과 함께 공개된 ACT의 확장판. 원본 `act` repo와 달리 **ACT 외에 Diffusion
Policy와 CNNMLP 같은 다른 정책 클래스**를 함께 제공해서 비교 실험이 가능함.
Diffusion Policy 구현이 `robomimic`과 `diffusers`에 의존하기 때문에 env를 따로 팠음.

## 진행 상태

| 단계 | 상태 |
|------|------|
| repo clone | ✅ 완료 |
| `aloha` env 구성 (robomimic editable + diffusers) | ✅ 완료 |
| 데이터 경로 수정 | ✅ 완료 |
| `policy.py` import 에러 수정 | ✅ 완료 |
| 데이터 생성 | ⬜ 미시작 (`act` repo에서 만든 데이터 재사용 검토 중) |
| 학습 / 평가 | ⬜ **한 번도 실행 안 해봄** |

---

## 내가 수정한 부분

diff 원본: [`patches/act-plus-plus.patch`](../patches/act-plus-plus.patch)

### 1) `constants.py` — 저자 개인 경로 제거

원본이 **저자의 개인 머신 경로가 하드코딩**되어 있었음:

```python
DATA_DIR = '/home/zfu/interbotix_ws/src/act/data' if os.getlogin() == 'zfu' else '/scr/tonyzhao/datasets'
```

내 환경에서는 어느 쪽이든 존재하지 않는 경로라 그대로는 못 씀. `act` repo와 동일하게 환경변수로 통일:

```python
DATA_DIR = os.environ.get('ALOHA_DATA_DIR', os.path.expanduser('~/aloha_project/aloha_data'))
```

> 참고: `os.getlogin()`은 실행 환경(cron, 일부 컨테이너, tmux 등)에 따라 예외를 던지는 경우가 있어서
> 어차피 걷어내는 게 맞음.

### 2) `policy.py` — robomimic 최신 버전 import 경로 변경 대응

```python
# 원본 (robomimic 구버전 기준)
from robomimic.algo.diffusion_policy import replace_bn_with_gn, ConditionalUnet1D

# 수정 — ConditionalUnet1D가 다른 모듈로 이동함
from robomimic.algo.diffusion_policy import replace_bn_with_gn
from robomimic.models.diffusion_policy_nets import ConditionalUnet1D
```

설치된 robomimic이 0.5.0(2026-08 커밋)이라 2024년 당시 구조와 달라졌음.
자세한 내용은 [90-troubleshooting.md](90-troubleshooting.md) #3.

---

## 실행할 때 (아직 안 해봄)

```bash
conda activate aloha                       # ← act 아님!
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
cd ~/aloha_project/act-plus-plus
```

ACT 정책 (원본 README 기준):

```bash
python3 imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/app_act \
  --policy_class ACT --kl_weight 10 --chunk_size 100 \
  --hidden_dim 512 --batch_size 8 --dim_feedforward 3200 \
  --num_epochs 2000 --lr 1e-5 --seed 0
```

Diffusion Policy로 바꾸려면 `--policy_class Diffusion`.
정확한 인자 이름과 기본값은 **실행 전에 `imitate_episodes.py`의 argparse 부분을 직접 확인**할 것
(act repo와 인자가 다를 수 있음).

## 확인 필요 사항

- [ ] `act` repo에서 만든 hdf5 데이터를 act-plus-plus에서 그대로 읽을 수 있는지
      (포맷이 같아 보이지만 검증 안 함) → 안 되면 여기서 다시 생성해야 함
- [ ] wandb가 깔려 있는데 자동으로 로그를 보내려 하는지 → 원하지 않으면 `wandb offline` 또는
      `WANDB_MODE=disabled` 설정
- [ ] Diffusion Policy는 ACT보다 VRAM을 더 쓸 가능성이 높음 → 11 GB에서 batch size 조정 필요할 듯

## 결과 기록란 (실행 후 채우기)

| 정책 | 성공률 | 학습 시간 | 메모 |
|------|--------|-----------|------|
| ACT (act-plus-plus) | | | |
| Diffusion Policy | | | |
| CNNMLP | | | |
