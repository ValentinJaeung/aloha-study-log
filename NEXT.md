# 다음에 이어서 할 일

> 이 파일은 "며칠/몇 주 뒤에 돌아왔을 때 3분 안에 다시 시작하기" 위한 파일입니다.
> 작업을 마칠 때마다 이 파일을 갱신하세요.

**마지막 작업일: 2026-09-17** (데이터 생성 완료)
**중단 지점: `sim_transfer_cube_scripted` 50 에피소드 생성까지 끝. ACT 학습은 아직 시작 안 함.**

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

## 1. ▶ 바로 할 일: ACT 학습 돌리기

```bash
conda activate act
export ALOHA_DATA_DIR=~/aloha_project/aloha_data
cd ~/aloha_project/act

python3 imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/sim_transfer_cube_scripted_act \
  --policy_class ACT \
  --kl_weight 10 \
  --chunk_size 100 \
  --hidden_dim 512 \
  --batch_size 8 \
  --dim_feedforward 3200 \
  --num_epochs 2000 \
  --lr 1e-5 \
  --seed 0
```

**시작 전 체크**
- [ ] `mkdir -p ~/aloha_project/ckpt` 먼저 만들어 두기
- [ ] 학습은 오래 걸리므로 `tmux` 안에서 실행 (WSL 터미널이 닫혀도 유지됨)
      → `tmux new -s act` 로 시작, `Ctrl+b` `d` 로 빠져나오기, `tmux attach -t act` 로 복귀
- [ ] 로그를 파일로도 남기기: 명령 끝에 `2>&1 | tee ~/aloha_project/ckpt/train.log`

**주의할 점 (2080 Ti / VRAM 11 GB)**
- `batch_size 8`은 저자 기본값. VRAM이 모자라면 `CUDA out of memory`가 나므로
  `--batch_size 4`로 낮춰서 재시도 (낮추면 수렴이 느려질 수 있음).
- 첫 1~2 epoch만 돌려보고 VRAM·속도를 먼저 확인한 뒤 2000 epoch를 거는 걸 권장.
  → `--num_epochs 2` 로 한 번 테스트 실행.

**끝나고 기록할 것** → `docs/01-act-sim.md`와 `logs/`에:
- [ ] 1 epoch당 소요 시간, 전체 소요 시간
- [ ] 최종/최소 validation loss, best checkpoint의 epoch
- [ ] `nvidia-smi`로 본 최대 VRAM 사용량
- [ ] 에러가 났다면 → `docs/90-troubleshooting.md`에 추가

---

## 2. 그다음: 학습한 정책 평가

학습이 끝나면 **같은 명령에 `--eval`만 추가**합니다 (best validation checkpoint를 불러옴).

```bash
python3 imitate_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --ckpt_dir ~/aloha_project/ckpt/sim_transfer_cube_scripted_act \
  --policy_class ACT \
  --kl_weight 10 --chunk_size 100 --hidden_dim 512 --batch_size 8 \
  --dim_feedforward 3200 --num_epochs 2000 --lr 1e-5 --seed 0 \
  --eval --temporal_agg
```

- `--temporal_agg`: temporal ensembling 켜기 (보통 성능이 올라감)
- rollout 영상은 `--ckpt_dir` 안에 저장됨
- **기대치**: transfer cube 성공률 약 **90%**. 많이 낮으면 저자 튜닝 팁 문서 참고
  (loss가 평평해진 뒤에도 더 오래 학습하면 성공률이 계속 오른다고 함)
- [ ] `--temporal_agg` 있을 때 / 없을 때 성공률을 둘 다 재서 비교 기록

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
