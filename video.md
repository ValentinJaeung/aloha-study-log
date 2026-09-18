# 영상 관련 명령 메모

정식 문서는 [docs/01-act-sim.md](docs/01-act-sim.md)와
[patches/act-extra/README.md](patches/act-extra/README.md)에 있음. 여기는 복붙용 메모.

## 영상 생성 (기존 hdf5 → mp4)

```bash
cd ~/aloha_project/act
python3 visualize_episodes.py \
  --dataset_dir ../aloha_data/sim_transfer_cube_scripted --episode_idx 33
```

- `--episode_idx`에는 파일명이 아니라 **숫자만** (`episode_{idx}.hdf5`로 조립됨)
- 결과는 `--dataset_dir` 안에 `episode_33_video.mp4`로 저장됨

## 영상 재생

```bash
cd ~/aloha_project/act
python3 play_video.py ../aloha_data/sim_transfer_cube_scripted/episode_33_video.mp4
```

`q`로 종료.

## 데이터 생성하며 화면으로 보기

```bash
cd ~/aloha_project/act
python3 record_sim_episodes.py \
  --task_name sim_transfer_cube_scripted \
  --dataset_dir $ALOHA_DATA_DIR/sim_transfer_cube_scripted \
  --num_episodes 50 --onscreen_render
```

> ⚠️ `--dataset_dir dataset`처럼 **상대경로를 주면 `act/dataset/`에 데이터를 새로 만들기 시작한다.**
> 2026-09-18에 이걸로 368 MB를 날렸음 → [docs/90-troubleshooting.md](docs/90-troubleshooting.md) #7
>
> ⚠️ 인자 이름은 `--onscreen`이 아니라 **`--onscreen_render`**
>
> ⚠️ 이 명령은 **기존 데이터를 처음부터 다시 생성**한다. 이미 50개가 있으므로
> 화면으로 보기만 할 거라면 위의 "영상 생성 → 재생"을 쓸 것.
