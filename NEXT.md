# 다음에 이어서 할 일

> 이 파일은 "며칠/몇 주 뒤에 돌아왔을 때 3분 안에 다시 시작하기" 위한 파일입니다.
> 작업을 마칠 때마다 이 파일을 갱신하세요.

**마지막 작업일: 2026-09-18** (ACT 학습·평가 완료 + 데모 생성 구조 개념 정리)
**중단 지점: 🎉 파이프라인 전체 검증 완료. 성공률 94%(agg 끔) / 98%(agg 켬)로 기대치 달성.
다음은 "무엇을 더 해볼까"를 고르는 단계 — 아래 1번 참고.**

> 💡 "시뮬 안에서 팔이 어떻게 움직이고, 코드가 만든 데모로 학습하는 게 왜 의미가 있는가"는
> [docs/01-act-sim.md](docs/01-act-sim.md)의 **"⭐ 개념 정리"** 섹션에 정리해둠.

---

## 0. 돌아왔을 때 워밍업 (2분)

```bash
# 1) 환경 활성화
conda activate act

# 2) 데이터 경로 환경변수 (수정한 constants.py가 이 변수를 읽음)
export ALOHA_DATA_DIR=~/aloha_project/aloha_data

# 3) 상태 점검 — 아래 3개가 다 통과해야 정상
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"          # → True
ls ~/aloha_project/aloha_data/sim_transfer_cube_scripted/*.hdf5 | wc -l       # → 50
cd ~/aloha_project/act && git status --short                                  # → constants.py, record_sim_episodes.py 2개만 M
```

`git status`에 수정 파일이 안 보이면 패치가 날아간 것이므로 아래로 복구:

```bash
cd ~/aloha_project/act && git apply ~/aloha_project/aloha-study-log/patches/act.patch
```

---

## 1. ▶ 바로 할 일: 다음 실험 고르기

**기본 파이프라인(데이터 생성 → 학습 → 평가)은 끝까지 검증됐습니다.** 기준 성공률도 확보했으니
이제부터는 "무엇을 바꾸면 어떻게 되는가"를 보는 단계입니다. 아래 셋 중 하나를 고르세요.

| 선택지 | 무엇을 배우나 | 비용 | 추가 디스크 |
|--------|--------------|------|------------|
| **A. `_human` 데이터 비교** (→ 4-2) | 멀티모달 데모가 왜 어려운지, CVAE가 왜 필요한지 | 다운로드 + 학습 40분 | +18 GB |
| **B. Diffusion Policy** (→ 3번 2항) | ACT 대비 다른 알고리즘의 성능 | 학습 시간 미지 | 없음 (데이터 재사용) |
| **C. `inject_noise` 비교** (→ 4-1) | 데이터 다양성과 복원력의 트레이드오프 | 코드 수정 + 재생성 + 학습 | +18 GB |

> 💡 **추천은 A.** 지금 기준값(scripted 94/98%)이 있는 상태에서 `_human`을 붙이면
> "코드가 만든 데모 vs 사람이 만든 데모"라는 [docs/01-act-sim.md](docs/01-act-sim.md) 개념 정리의
> 핵심 주장을 **숫자로 직접 확인**할 수 있습니다. 코드 수정도 필요 없습니다
> (`SIM_TASK_CONFIGS`에 `sim_transfer_cube_human` 항목이 이미 있음).

---

## 2. 완료: ACT 학습 + 평가 (2026-09-18) 🎉

### 학습

| 항목 | 값 |
|------|-----|
| 소요 | **38분 10초** (2000 epoch, 1 epoch 1.15초) |
| best val loss | **0.045839 @ epoch 1995** |
| 최대 VRAM | 4,840 MiB / 11,264 MiB (`batch_size 8`로 여유 있음) |
| 산출물 | `~/aloha_project/ckpt/sim_transfer_cube_scripted_act/` (23개, 7.2 GB) |
| 로그 | `~/aloha_project/ckpt/train.log` |

현재 `~/aloha_project/ckpt/`에 남아 있는 것 (총 7.9 GB, 디스크 여유 892 GB):

```
ckpt/
├── sim_transfer_cube_scripted_act/   체크포인트 23개 + rollout 영상 100개
├── train.log                          학습 로그 (val loss 추이 분석에 사용)
├── eval_no_agg.log                    평가 1회차
└── eval_temporal_agg.log              평가 2회차
```

> 💡 중간 체크포인트(`policy_epoch_*.ckpt`, 21개 ≈ 7 GB)는 학습 곡선 비교용이 아니면
> 지워도 된다. 평가는 `policy_best.ckpt`만 쓴다.

### 평가 — 기대치(≈90%) 달성 ✅

| | temporal_agg 끔 | temporal_agg 켬 |
|---|---|---|
| **Success rate** | **0.94** (47/50) | **0.98** (49/50) |
| Average return | 592.66 | **669.04** |
| 소요 시간 | 9분 32초 | 15분 19초 |
| 영상 | `rollouts_no_agg/` | `rollouts_temporal_agg/` |
| 로그 | `ckpt/eval_no_agg.log` | `ckpt/eval_temporal_agg.log` |

- 실패는 거의 전부 **파지(grasp) 단계**. 집기만 하면 전달은 사실상 따라온다.
- **val loss가 수렴하지 않았는데도 94~98%가 나왔다** → 예정했던 `--num_epochs 5000`
  재학습은 **불필요**. "loss를 더 낮춰야 성공률이 오른다"가 항상 맞지는 않음.
- ⚠️ 평가 2회 돌릴 땐 rollout 영상이 덮어써지므로 1회차를 먼저 옮길 것.

재현 명령은 [docs/01-act-sim.md](docs/01-act-sim.md)에, 과정은 [logs/2026-09-18.md](logs/2026-09-18.md)에 있습니다.

**정리할 것** — 전부 완료 ✅
- [x] ~~스모크 테스트 산출물 삭제~~ (2.6 GB, 2026-09-18 처리)
- [x] ~~잘못 생성된 `~/aloha_project/act/dataset/` 삭제~~ (352 MB, 2026-09-18 처리)
- [x] ~~`act/play_video.py`, `act/model_test.py` 백업~~ → [patches/act-extra/](patches/act-extra/) (2026-09-18 처리)
- [x] ~~`~/.bashrc`의 렌더링 export 3줄을 `docs/00-environment.md`에 옮겨 적기~~ (2026-09-18)
- [x] ~~OpenGL 오류 항목을 `docs/90-troubleshooting.md`에 추가~~ → #5, #6, #7 추가 (2026-09-18)
- [x] ~~루트의 `video.md` 정리~~ → 잘못된 명령 수정 + 경고 추가 (2026-09-18)

---

## 3. 이후 후보 (우선순위 순)

1. **`sim_insertion_scripted` 태스크도 해보기**
   - 데이터 생성부터 다시: `--task_name sim_insertion_scripted`
   - 기대 성공률 약 50% (transfer cube보다 어려움)
   - ⚠️ 디스크 주의: 50 에피소드 ≈ 18 GB 추가로 필요
2. **act-plus-plus로 Diffusion Policy 학습** → [docs/02-act-plus-plus.md](docs/02-act-plus-plus.md)
   - `conda activate aloha` (env가 다름!)
   - import 버그는 이미 고쳐둠, 아직 한 번도 실행 안 해봄
   - ACT vs Diffusion Policy 성능 비교가 목표
3. **하이퍼파라미터 실험**: `chunk_size`(100 → 50/200), `kl_weight` 변화에 따른 성공률 비교
4. **mobile-aloha 코드 읽기** → [docs/03-mobile-aloha.md](docs/03-mobile-aloha.md)

---

## 4. 나중에 할 것 — 데모 데이터의 "질"을 바꿔보는 실험

> 배경: 지금 쓰는 `sim_transfer_cube_scripted`는 **코드가 만든 데모**라
> 파이프라인(데이터 생성 → 학습 → 평가) 검증에는 충분하지만,
> 알고리즘의 어려운 부분(**멀티모달 데모 처리**)은 잘 드러나지 않는다.
> 개념 정리는 [docs/01-act-sim.md](docs/01-act-sim.md)의 "⭐ 개념 정리" 섹션 5번 참고.
>
> ✅ 기준 성공률 확보 완료 (`_scripted` 94% / 98%, 2026-09-18). 이제 비교 실험을 해도 된다.

### 4-1. `inject_noise=True`로 데이터를 다시 만들어 비교

`record_sim_episodes.py:31`에 `inject_noise = False`가 **하드코딩**되어 있다.
`scripted_policy.py:54-58`에는 EE 위치에 `±0.01` 균일 노이즈를 주는 코드가 이미 있는데 안 쓰이는 상태.

```python
# record_sim_episodes.py:31 — 하드코딩된 값을 인자로 빼거나 직접 True로 변경
inject_noise = False   # → True
```

- [ ] `record_sim_episodes.py`에 `--inject_noise` 플래그 추가 (지금은 하드코딩이라 코드 수정 필요)
      → 수정하면 **`patches/act.patch`도 다시 뜰 것**
- [ ] 별도 디렉터리에 50 에피소드 재생성
      (`$ALOHA_DATA_DIR/sim_transfer_cube_scripted_noise`) ⚠️ **+18 GB 디스크 필요**
- [ ] `constants.py`의 `SIM_TASK_CONFIGS`에 태스크 항목 추가 필요
- [ ] 같은 하이퍼파라미터로 학습 → 성공률 비교 (`--ckpt_dir`을 꼭 분리)
- **관찰 포인트**: 노이즈가 들어가면 궤적이 매번 달라져 데이터가 어려워지는데,
  그 대신 **분포 밖 상태에서의 복원력**이 생겨 성공률이 오를 수 있다.
  둘 중 어느 쪽이 이기는지 직접 확인하는 게 목적.

### 4-2. `_human` 데이터셋(실제 teleoperation)으로 같은 학습 돌려 비교

저자가 공개한 **사람이 직접 조작한 데모**. `constants.py`의 `SIM_TASK_CONFIGS`에
`sim_transfer_cube_human`(50 ep / 400 step), `sim_insertion_human`(50 ep / 500 step) 항목이
**이미 정의되어 있다** — `dataset_dir`도 `$ALOHA_DATA_DIR/sim_transfer_cube_human`으로 잡혀 있어
**데이터만 그 경로에 갖다 놓으면 코드 수정 없이 바로 돌아간다.**

- [ ] 저자 배포 데이터 내려받기 (`sim_transfer_cube_human` 50 에피소드)
      → https://drive.google.com/drive/folders/1gPR03v05S1xiInoVJn7G7VJ9pDCnxq9O (act README 기재)
- [ ] `$ALOHA_DATA_DIR/sim_transfer_cube_human/`에 그대로 배치 (⚠️ 여기도 +18 GB 수준)
- [ ] `--task_name sim_transfer_cube_human`으로 동일 하이퍼파라미터 학습 → 성공률 비교
- **관찰 포인트**:
  - 사람 데모는 **멀티모달**(같은 상황에서 매번 다른 궤적)이라 일반적으로 `_scripted`보다
    성공률이 낮게 나온다. 논문 수치와 대조해볼 것.
  - ACT의 **CVAE(style variable `z`, `kl_weight`)가 여기서 비로소 일을 한다.**
    `_human`에서 `kl_weight`를 바꿔가며(예: 10 → 1 → 100) 성공률 변화를 보면
    CVAE의 역할을 체감할 수 있다 → 위 3번 하이퍼파라미터 실험과 묶어서 하면 효율적
  - 가능하면 `_scripted` / `_scripted+noise` / `_human` **3자 비교표**로 정리

| 데이터셋 | 데모 생성 주체 | 멀티모달리티 | 성공률 |
|---|---|---|---|
| `sim_transfer_cube_scripted` | 코드 (waypoint 보간) | 없음 | **94% / 98%** ← 기준 |
| `..._scripted` + `inject_noise` | 코드 + ±0.01 노이즈 | 약간 | (미실행) |
| `sim_transfer_cube_human` | 사람 (teleoperation) | 있음 | (미실행) |

---

## 열린 질문 / 알아볼 것

- [ ] 에피소드 하나가 368 MB인 이유 → 압축 없이 저장되기 때문. `--compress` 같은 옵션이 있는지,
      또는 hdf5 gzip 압축으로 용량을 줄일 수 있는지 확인 (18 GB는 태스크 추가 시 부담)
- [ ] `act`와 `act-plus-plus`의 ACT 구현 차이가 정확히 뭔지 (diff 떠서 비교해보기)
- [ ] 실기(하드웨어) 없이 Mobile ALOHA에서 해볼 수 있는 범위가 어디까지인지
