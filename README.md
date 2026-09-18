# ALOHA / ACT 스터디 로그

Mobile ALOHA와 ACT(Action Chunking with Transformers)를 따라 해보면서 남기는 **학습 기록 저장소**입니다.
코드나 데이터셋 자체는 올리지 않고, **어디까지 했는지 / 뭐가 막혔는지 / 다음에 뭘 할지**만 기록합니다.

> 🔖 **다음에 이어서 할 때는 [NEXT.md](NEXT.md)부터 읽으세요.**

---

## 현재 진행 상황

마지막 업데이트: **2026-09-18**

| # | 단계 | 상태 | 비고 |
|---|------|------|------|
| 0 | 환경 구축 (conda, CUDA, MuJoCo) | ✅ 완료 | env 2개: `act`, `aloha` → [docs/00-environment.md](docs/00-environment.md) |
| 1 | 원본 repo 4개 clone | ✅ 완료 | act, act-plus-plus, mobile-aloha, robomimic |
| 2 | 코드 경로/버그 수정 | ✅ 완료 | 수정본은 [patches/](patches/)에 diff로 보관 |
| 3 | 시뮬 데이터 생성 (`sim_transfer_cube_scripted` 50 ep) | ✅ 완료 | 18 GB, 2026-09-16 ~ 09-17 |
| 4 | 데이터 시각화 확인 | ✅ 완료 | `episode_0_video.mp4`, `episode_0_qpos.png` 생성 확인 |
| 5 | ACT 학습 (train) | ✅ 완료 | 2000 epoch / 38분 / best val loss 0.0458 @ epoch 1995 → [docs/01-act-sim.md](docs/01-act-sim.md) |
| 6 | ACT 평가 (eval, success rate) | ✅ 완료 | **94%** (agg 끔) / **98%** (agg 켬) — 목표 90% 달성 🎉 |
| 7 | **act-plus-plus (Diffusion Policy)** | 🟡 **준비만 완료 ← 여기부터** | import 버그 수정까지 끝, 아직 실행 안 함 → [NEXT.md](NEXT.md) |
| 8 | mobile-aloha (실기/하드웨어) | ⬜ 미진행 | 참고용으로 clone만 해둔 상태 |

범례: ✅ 완료 · 🟡 진행 중/부분 완료 · ⬜ 미시작

> 📘 **개념 정리**: "시뮬에서 팔은 누가 움직이고(mocap/weld), 왜 2단계로 데이터를 모으며,
> 코드가 만든 데모로 학습하는 게 어떤 의미인가(= 특권 정보의 증류)"는
> [docs/01-act-sim.md](docs/01-act-sim.md)의 **⭐ 개념 정리** 섹션에 있음. (2026-09-18 추가)

---

## 저장소 구성

```
aloha-study-log/
├── README.md              ← 지금 이 파일 (전체 진행 상황 대시보드)
├── NEXT.md                ← 다음에 이어서 할 작업 + 복붙용 명령어
├── video.md               ← 영상 생성/재생 명령 메모
├── docs/
│   ├── 00-environment.md  ← 환경 구축 (HW/SW 스펙, 설치 순서, 버전)
│   ├── 01-act-sim.md      ← ACT 시뮬레이션 실습 기록
│   ├── 02-act-plus-plus.md← act-plus-plus (Diffusion Policy) 기록
│   ├── 03-mobile-aloha.md ← mobile-aloha repo 관련 메모
│   └── 90-troubleshooting.md ← 에러 & 해결 모음 ⭐
├── patches/               ← 원본 repo에 가한 수정 diff + pip freeze
│   └── act-extra/         ← act/에 새로 추가한 스크립트 원본 (diff에 안 잡히는 신규 파일)
└── logs/                  ← 날짜별 작업 일지 (TEMPLATE.md 복사해서 사용)
```

## 작업 대상 원본 repo

로컬 경로는 `~/aloha_project/` 아래에 있으며, 이 저장소에는 포함되지 않습니다.

| repo | upstream | clone한 커밋 | 로컬 수정 |
|------|----------|--------------|-----------|
| `act` | [tonyzhaozh/act](https://github.com/tonyzhaozh/act) | `742c753` (2024-01-28) | ✅ 2개 파일 |
| `act-plus-plus` | [MarkFzp/act-plus-plus](https://github.com/MarkFzp/act-plus-plus) | `26bab07` (2024-01-10) | ✅ 2개 파일 |
| `mobile-aloha` | [MarkFzp/mobile-aloha](https://github.com/MarkFzp/mobile-aloha) | `0e40324` (2024-01-03) | 없음 |
| `robomimic` | [ARISE-Initiative/robomimic](https://github.com/ARISE-Initiative/robomimic) | `d309eae` (2026-08-09) | 없음 (editable 설치) |

## 로컬 디렉터리 구조 (참고)

```
~/aloha_project/
├── act/                  1.2 GB   ACT 원본 (수정됨)
├── act-plus-plus/        2.9 MB   ACT++ (수정됨)
├── mobile-aloha/         6.3 MB   Mobile ALOHA (원본 그대로)
├── robomimic/            110 MB   robomimic 0.5.0 (editable 설치됨)
├── aloha_data/            18 GB   생성한 시뮬 데이터셋 ⚠️ git에 올리지 않음
└── aloha-study-log/              ← 이 저장소
```

## 참고 링크

- Mobile ALOHA 프로젝트: https://mobile-aloha.github.io/
- ALOHA / ACT 프로젝트: https://tonyzhaozh.github.io/aloha/
- ACT 논문: [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/abs/2304.13705)
- Mobile ALOHA 논문: [Mobile ALOHA: Learning Bimanual Mobile Manipulation with Low-Cost Whole-Body Teleoperation](https://arxiv.org/abs/2401.02117)
- ACT 튜닝 팁 (저자 문서): https://docs.google.com/document/d/1FVIZfoALXg_ZkYKaYVh-qOlaXveq5CtvJHXkY25eYhs/edit
