# `act/`에 새로 추가한 스크립트

`act.patch`는 **원본에 이미 있던 파일의 수정분**만 담고 있습니다 (`constants.py`,
`record_sim_episodes.py`). 아래 두 개는 원본에 없는 **새 파일**이라 diff에 안 잡히므로
여기에 원본 그대로 백업해 둡니다.

복구:

```bash
cp ~/aloha_project/aloha-study-log/patches/act-extra/*.py ~/aloha_project/act/
```

| 파일 | 용도 |
|------|------|
| `play_video.py` | 저장된 mp4를 재생. 레포에 재생 코드가 없어서 직접 만듦 |
| `model_test.py` | `dm_control` viewer로 시뮬 환경을 띄워보는 4줄짜리 확인용 |

## `play_video.py`

```bash
cd ~/aloha_project/act
python3 play_video.py ../aloha_data/sim_transfer_cube_scripted/episode_33_video.mp4
```

`q`를 누르면 종료됩니다. mp4의 FPS를 읽어 그 속도로 재생합니다.

> `act-plus-plus/replay_episodes.py`는 이름과 달리 재생 스크립트가 아닙니다.
> 저장된 action을 시뮬에서 다시 실행해 *새* mp4를 만드는 스크립트라 용도가 다릅니다.

## `model_test.py`

```bash
cd ~/aloha_project/act
python3 model_test.py
```

viewer 창이 안 뜨고 OpenGL 오류가 나면 `~/.bashrc`의 렌더링 export 3줄이 적용됐는지 확인하세요
(→ [docs/00-environment.md](../../docs/00-environment.md), [docs/90-troubleshooting.md](../../docs/90-troubleshooting.md)).
