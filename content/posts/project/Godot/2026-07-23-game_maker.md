---
title: "게임 만들기 - Godot 시그널 배우기"
date: "2026-07-23"
description: "Godot 시그널(발행/구독)·커스텀 시그널·await 개념 학습 정리"
categories:
  - "project"
tags:
  - "game_maker"
  - "project"
  - "Godot"
  - "signal"
  - "autoload"
  - "await"
series:
  - "Godot"
ShowToc: true
TocOpen: false
---

## 오늘 한 것

- 시그널 개념 학습 (발행/구독, 관찰자 패턴)
- 타이틀 씬 추가: 게임 시작 / 게임 종료 버튼, 시작 씬을 Title로 변경
- 기존 Main 씬 → Game 씬으로 이름 변경
- `GameState`에 커스텀 시그널 2개 추가 (`money_changed`, `went_bankrupt`)
- 돈 변화 반응 구현: 라벨 색상 변화, 연승/연패 표시, 파산 게임오버
- `make editor` / `make run` 명령어(Makefile) 추가

## 1. 시그널이란

- **"어떤 일이 일어났을 때, 구독하고 있는 쪽에 알려주는 방송"** (관찰자 패턴).
- 백엔드 비유: Django의 `post_save` 시그널, SNS의 발행/구독 구조와 개념이 같음.
- 발행자는 구독자가 누군지/몇 명인지 모름. 구독자 0명이어도 발행은 성립.
- **목적**: 결합도 낮추기. 버튼은 "나 눌렸어!"만 외치고, 누가 듣는지 모름
→ 버튼이 재사용 가능한 독립 부품이 됨.

## 2. 동작은 동기적 직접 호출

- 게임 전체는 **하나의 프로세스다.**
- `emit()`은 connect된 함수 리스트를 **그 자리에서 순서대로 즉시 실행**하는 메서드
- 전부 끝나야 다음 줄로 넘어감. "던져놓고 각자 처리"가 아니라 "즉시 전화 돌리기".
- 시그널: 호출할 함수들의 리스트

예) 화면에 "동전 줍기" 버튼(`CoinButton`)이 하나 있다고 하자.

```
$CoinButton.pressed.connect(f)       # 구독      (≈ list.append)
$CoinButton.pressed.disconnect(f)    # 구독 해제  (≈ list.remove)
my_signal.emit(args)                 # 발행      (≈ for f in list: f(args))
```

- `CoinButton`이라는 노드의 `pressed`라는 시그널 객체에 넣는다
    - 파이썬에서 list 내장 타입에 `append`라는 메서드가 있듯, `connect`는 시그널 내장 타입의 메서드임

## 3. 실행 순서

- connect한 순서대로 실행되지만, **순서에 의존하는 설계는 금지**
    - 각 노드의 `_ready` 타이밍에 따라 달라지는 실행 순서로 인해 암묵적 결합이 발생하기 때문이다.
- 순서가 중요하면 핸들러 하나가 받아서 명시적으로 순서대로 호출할 것.
    - 호출해야 하는 함수들을 순서대로 호출하는 하나의 함수를 구현

## 4. 지역 시그널 vs 전역 시그널

- 시그널 자체에 스코프는 없고, **시그널의 주인이 어디 사느냐**가 전부.
- 일반 노드의 시그널: 참조를 알아야 구독 가능. 씬과 함께 파괴됨.
- Autoload의 시그널: 어디서든 해당 시그널에 `connect`가능.
    - 전역이므로 게임이 살아있는 동안 계속 존재 (= 이벤트 버스 패턴).

## 5. 씬 교체 구조에서의 통신 규칙

- 씬은 `change_scene_to_file`에서는 **통째로 교체**됨 (웹의 페이지 이동과 동일).
- 이전 씬의 노드는 파괴되므로 다른 씬의 버튼 시그널을 직접 구독하는 건 불가능.
    - 항상 1개의 씬만 동작하고 있으므로 다른 씬은 구성되어 있지 않아서 전파할 수도, 받을 수도 없다.
    - **버튼 시그널은 그 씬 안에서 소비**하고, 씬 바깥과 공유할 정보는 Autoload에 상태나 시그널로 둔다.
    - 예) 주인공이 죽었다는 시그널은 주인공의 생존 사실을 표시하는 전역 변수를 통해 다른 씬이 로드되었을 때 알게한다.

### 씬 교체구조가 아니라면?

- 팝업처럼 씬을 겹치는 구조에서는 동시에 살아있으므로 직접 구독도 가능.
- 단, 남의 내부 버튼이 아니라 그 씬이 공개한 커스텀 시그널을 구독하는 게 관례 ("call down, signal up")
- 너무 깊어져서 나중에 더 공부하기로!

## 6. 커스텀 시그널 만들기

- 내장 시그널(`pressed` 등)만 있는 게 아니라 직접 선언할 수도 있다.

### 예시

- 잔액 데이터를 관리하는 전역 객체 `Wallet`(지갑)과, 잔액을 화면에
표시하는 라벨이 있다고 하자.
- 잔액이 바뀐 값에 따라 잔액 표시 문자의 색깔을 바꾸는 함수를 시그널을 통해 구현

```python
# Wallet.gd (Autoload) — 발행자
signal balance_changed(new_amount: int, delta: int)   # 시그널 선언

var balance: int = 0:
	set(value):                      # 파이썬 @property.setter와 동일
		var delta := value - balance
		balance = value
		balance_changed.emit(balance, delta)   # 값이 바뀔 때마다 방송
```

```python
# BalanceLabel.gd — 잔액 표시 라벨 (구독자)
extends Label

func _ready() -> void:
# 잔액 변동이라는 시그널 객체에 잔액변동시 실행될 함수 추가
	Wallet.balance_changed.connect(_on_balance_changed)

# 잔액 표시 텍스트의 색깔을 변화량이 양수면 초록색, 음수면 빨강색으로 바꾸는 함수
func _on_balance_changed(new_amount: int, delta: int) -> void:
	text = "잔액: %d원" % new_amount
	modulate = Color.GREEN if delta > 0 else Color.RED   # 벌면 초록, 잃으면 빨강
```

- 잔액을 바꾸는 쪽은 어디에 있든 `Wallet.balance += 100` 한 줄이면 끝.
- 라벨 갱신은 구독자가 알아서 처리한다.
- **하나의 시그널, 여러 구독자**. 효과음, 애니메이션, 파산 체크 등 반응을
추가할 때 발행자(`Wallet`)는 한 글자도 안 바뀌고 구독자만 붙이면 된다.

### 오늘 프로젝트에 적용한 것

- `GameState`(Autoload)에 위와 같은 구조로 시그널 2개 추가:
`money_changed(new_amount, delta)`, `went_bankrupt`(돈이 0원 미만이 되는 순간).
- 구독자: `Game.gd`(라벨 갱신 + 색상 + 연승/연패 + 파산 처리), `Bank.gd`(라벨 갱신).
- 돈을 바꾸는 쪽은 `GameState.money += 100` 한 줄만
하면 라벨 갱신 등은 구독자들이 알아서 처리 → 버튼 핸들러가 홀쭉해짐.
- `win_streak`은 Game 씬의 지역 변수라 은행에 다녀오면 리셋됨
    - 씬이 파괴되면 그 안의 상태도 사라진다는 것의 실례.

## 7. `await` — 시그널을 일회성으로 기다리기

```
await get_tree().create_timer(2.0).timeout
```

- "2초 타이머의 `timeout` 시그널이 올 때까지 **이 함수만** 일시정지".
- `time.sleep`과 달리 게임 전체는 멈추지 않음.
- `connect`(계속 구독) 대신 `await`(한 번만 수신)로 시그널을 받는 패턴.

## 실습

1. 시그널 적용
    1. 유저가 돈을 얻으면 초록색, 잃으면 빨간색
    2. 연속된 상태 표시
    3. 기존 잔액 변동을 시그널을 이용하도록 변경

![시그널 적용 동작](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/6.gif)

2. `await` 적용
    1. 유저의 잔액이 바닥나면 2초 후 초기 화면으로 돌아감

![파산 처리 동작](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/7.gif)

## 프로젝트 구조

```
tutorials/
├── scenes/
│   ├── Title.tscn   # 게임 시작 / 게임 종료 버튼 (시작 씬)
│   ├── Game.tscn    # (구 Main) 자산 표시, 슬롯머신, 은행가기 버튼
│   └── Bank.tscn    # 자산 표시, 대출받기, 돌아가기 버튼
└── scripts/
    ├── Title.gd
    ├── Game.gd
    ├── Bank.gd
    └── GameState.gd   # Autoload 전역 상태 + money_changed / went_bankrupt 시그널
Makefile               # make editor / make run
```

## 다음에 이어서 볼 것 (아이디어)

- `win_streak`을 GameState로 옮겨서 씬을 오가도 유지되게 만들기 (연습용)
- `@onready var` 문법으로 `$이름` 대신 타입 안전하게 노드 참조하기
- Tween으로 자산 변동 애니메이션 (이번에 선택 안 한 후보)
- 주식/회사 데이터 구조 설계 시작

---

> 이전 글: [게임 만들기 - Godot 기초 배우기](/posts/2026-07-16-game_maker/)
