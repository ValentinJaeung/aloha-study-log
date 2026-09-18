# 03. mobile-aloha

- upstream: https://github.com/MarkFzp/mobile-aloha
- 로컬 경로: `~/aloha_project/mobile-aloha`
- clone한 커밋: `0e40324` (2024-01-03, "update README for init release")
- 로컬 수정: **없음** (원본 그대로)

## 상태

⬜ **미진행** — clone만 해두고 아직 실행하거나 깊게 읽지 않았음.

## 이 repo가 뭔가

Mobile ALOHA의 **하드웨어/실기(real robot) 쪽** 코드. 이동식 베이스 + 양팔 로봇을 whole-body
teleoperation으로 조작해서 데이터를 수집하고 재생하는 부분이 들어 있음.

역할 분담을 정리하면:

| repo | 역할 |
|------|------|
| `mobile-aloha` | 실기 하드웨어 제어 / 데이터 수집 (ROS, Interbotix 팔 필요) |
| `act-plus-plus` | 정책 학습·평가 (ACT / Diffusion Policy) |
| `act` | 원조 ACT + 시뮬 환경 |

즉 **학습 코드는 `act-plus-plus`에 있고, 이 repo는 로봇을 움직이는 쪽**이라 지금처럼
시뮬레이션만 하는 단계에서는 직접 쓸 일이 거의 없음.

> `act-plus-plus` README에도 "mobile-aloha 하드웨어 데이터를 시각화할 때는 이 repo의
> `visualize_episodes.py`를 쓰라"고 적혀 있음 — 실기 데이터를 다루게 되면 그때 필요.

## 실기 실행에 필요한 것 (현재 없음)

- ALOHA 하드웨어 (Interbotix ViperX / WidowX 팔, 이동식 베이스)
- ROS 환경 + Interbotix 드라이버
- 이 중 아무것도 준비되어 있지 않으므로 **당분간은 코드 읽기용**으로만 활용

## 하드웨어 없이 해볼 수 있는 것

- [ ] 데이터 수집 스크립트를 읽고, 실기 hdf5의 구조(카메라 개수, qpos 차원, 베이스 속도 등)가
      시뮬 데이터와 어떻게 다른지 정리
- [ ] 저자들이 공개한 실기 데이터셋을 받아서 `visualize_episodes.py`로 재생해보기
- [ ] whole-body teleoperation이 코드 상에서 어떻게 구현됐는지(베이스 + 팔 동시 제어) 확인

## 메모

(읽으면서 알게 된 내용을 여기에 추가)
