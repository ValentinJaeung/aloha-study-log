# 다음에 이어서 할 일

> 이 파일은 "며칠/몇 주 뒤에 돌아왔을 때 3분 안에 다시 시작하기" 위한 파일입니다.
> 작업을 마칠 때마다 이 파일을 갱신하세요.

**마지막 작업일: 2026-09-18** (ACT 학습 2000 epoch 완료)
**중단 지점: 학습 끝(38분, best val loss 0.0458 @ epoch 1995). 평가(eval)는 아직 안 돌림.**

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

## 1. ▶ 바로 할 일: 학습한 정책 평가하기

**학습 명령에 `--eval`만 추가**합니다 (`policy_best.ckpt`를 자동으로 불러옴).
하이퍼파라미터는 학습 때와 **완전히 같아야** 모델 구조가 맞습니다.

```bash
conda activate act
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
cd ~/aloha_project/act

# (1) temporal_agg 끄고
python3 imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/sim_transfer_cube_scripted_act \
  --policy_class ACT \
  --kl_weight 10 --chunk_size 100 --hidden_dim 512 --batch_size 8 \
  --dim_feedforward 3200 --num_epochs 2000 --lr 1e-5 --seed 0 \
  --eval

# (2) temporal_agg 켜고
#     위와 동일 + 맨 끝에 --temporal_agg
```

**주의**
- ⚠️ 평가는 **렌더링을 하므로** `GALLIUM_DRIVER=d3d12`가 적용된 터미널에서 실행할 것.
  적용 안 되면 소프트웨어 렌더링(llvmpipe)으로 떨어져 4.7배 느려짐
  → [logs/2026-09-18.md](logs/2026-09-18.md) 2부 참고. `~/.bashrc`에 넣어뒀으므로 새 터미널이면 자동 적용.
  확인: `echo $GALLIUM_DRIVER` → `d3d12`
- rollout 영상과 성공률은 `--ckpt_dir` 안에 저장됨
- **기대치**: transfer cube 성공률 약 **90%**
- [ ] `--temporal_agg` 있을 때 / 없을 때 성공률을 둘 다 재서 비교 기록

**성공률이 기대치보다 많이 낮다면** → 하이퍼파라미터를 건드리기 전에 **학습을 더 돌리는 것부터**:

```bash
--num_epochs 5000 --ckpt_dir ~/aloha_project/ckpt/sim_transfer_cube_scripted_act_5000
```

2000 epoch 학습에서 **val loss가 끝까지 내려가는 중이었음**(best @ epoch 1995, 마지막 500구간에서 27% 추가 개선).
즉 아직 수렴 전이고, 1 epoch = 45 샘플뿐이라 5000 epoch도 약 96분이면 끝납니다.
근거 데이터는 [docs/01-act-sim.md](docs/01-act-sim.md) 참고. `--ckpt_dir`을 꼭 분리해야 기존 결과가 안 덮어써집니다.

---

## 2. 완료: ACT 학습 (2026-09-18)

| 항목 | 값 |
|------|-----|
| 소요 | **38분 10초** (2000 epoch, 1 epoch 1.15초) |
| best val loss | **0.045839 @ epoch 1995** |
| 최대 VRAM | 4,840 MiB / 11,264 MiB (`batch_size 8`로 여유 있음) |
| 산출물 | `~/aloha_project/ckpt/sim_transfer_cube_scripted_act/` (23개, 7.2 GB) |
| 로그 | `~/aloha_project/ckpt/train.log` |

재현이 필요하면 명령은 [docs/01-act-sim.md](docs/01-act-sim.md)에, 과정은 [logs/2026-09-18.md](logs/2026-09-18.md)에 있습니다.

**정리할 것**
- [ ] 스모크 테스트 산출물 삭제: `rm -rf ~/aloha_project/ckpt/smoke_test ~/aloha_project/ckpt/smoke_test20` (2.6 GB)
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

## 열린 질문 / 알아볼 것

- [ ] 에피소드 하나가 368 MB인 이유 → 압축 없이 저장되기 때문. `--compress` 같은 옵션이 있는지,
      또는 hdf5 gzip 압축으로 용량을 줄일 수 있는지 확인 (18 GB는 태스크 추가 시 부담)
- [ ] `act`와 `act-plus-plus`의 ACT 구현 차이가 정확히 뭔지 (diff 떠서 비교해보기)
- [ ] 실기(하드웨어) 없이 Mobile ALOHA에서 해볼 수 있는 범위가 어디까지인지
