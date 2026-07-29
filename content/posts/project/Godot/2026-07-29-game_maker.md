---
title: "게임 만들기 - Godot 데이터 설계 배우기"
date: "2026-07-29"
description: "게임 데이터의 3분류(정의/가변/파생)·Resource·데이터 주도 설계 개념 학습 정리"
categories:
  - "project"
tags:
  - "game_maker"
  - "project"
  - "Godot"
  - "resource"
  - "data-driven"
  - "game-data"
series:
  - "Godot"
ShowToc: true
TocOpen: false
---

## 오늘 한 것

- 게임 데이터의 3분류 학습: **정의 데이터 / 가변 상태 / 파생 데이터**
- `Resource` 개념 학습 (직렬화 가능한 데이터 객체, `.tres` 파일)
- **데이터 주도 설계(data-driven design)** 개념 학습
- 슬롯머신을 **베팅 기계 3대**로 확장: `MachineDef` 리소스 + `.tres` 3개
- 버튼을 씬에 그리지 않고 데이터 개수만큼 코드로 생성 → `.tres` 추가만으로 기계가 늘어남

## 1. 웹 백엔드와의 근본적 차이

|  | 웹 백엔드 | 게임 |
| --- | --- | --- |
| SSOT | DB | **메모리** |
| 프로세스 | 요청마다 생성·소멸 (stateless) | 시작~종료까지 계속 살아있음 |
| 영속화 | 매 요청마다 자동 | **명시적으로 저장할 때만** |
| 스키마 | 마이그레이션으로 강제 | 없음. 내가 지키는 규약이 전부 |
| 조회 | `SELECT ... WHERE` | 배열/딕셔너리 직접 순회 |
| 관계 | FK, JOIN | 객체 참조 또는 id 문자열 |
- 모든 데이터가 메모리에 객체로 떠 있다. 그래서 DB도 커밋도 없이 `Wallet.balance += 100` 한 줄로 상태가 바뀐다.
- 세이브 파일은 그 메모리를 **어느 시점에 찍어둔 스냅샷(snapshot)** 일 뿐이다.
- 스키마를 강제해주는 장치가 없으므로, **데이터를 어떻게 분류할지 스스로 정해야 한다.**

## 2. 게임 데이터의 3가지 종류

핵심 질문은 "테이블 몇 개?"가 아니라 **"이 값은 어느 종류인가?"** 다.

|  | **정의 데이터** | **가변 상태** | **파생 데이터** |
| --- | --- | --- | --- |
| 영어 | static data, definition, master data | runtime state, save data, mutable state | derived state, computed value, view state |
| 다른 이름 | 기획 데이터, 데이터 테이블, 밸런스 데이터 | 런타임 상태, 세이브 데이터 | 계산값 |
| 성격 | 만들 때 정하고 **플레이 중 안 바뀜** | 플레이하면서 **변함** | 다른 데이터로부터 **계산됨** |
| 예 | 포션 회복량, 몬스터 스탯, 아이템 가격 | 현재 HP, 인벤토리, 보유 현금, 현재 턴 | 총 자산, 등락률, 라벨 텍스트 |
| 백엔드 비유 | 마이그레이션 시드, 상품 마스터 테이블 | 실제 DB 레코드 | 응답 DTO, 템플릿 렌더링 결과, `@property` |
| 세이브 | X (게임 파일에 이미 있음) | **O — 이게 곧 세이브 파일** | X (매번 계산) |
| 저장 위치 | `.tres` 등 파일 | Autoload / 노드 필드 | 어디에도 저장 안 함 (함수) |

### 판별 표

값을 하나 놓고 위에서부터 물어본다.

| # | 질문 | 정의 데이터 | 가변 상태 | 파생 데이터 |
| --- | --- | --- | --- | --- |
| 1 | **다른 값으로 계산할 수 있나?** | X | X | **O** |
| 2 | 플레이 중에 값이 바뀌나? | X | **O** | 원본에 따라 |
| 3 | 세이브 파일에 넣어야 하나? | X | **O** | X |
| 4 | 새 게임을 시작하면 초기화되나? | X | **O** | 원본에 따라 |
- **1번이 가장 강한 기준.** 계산할 수 있으면 나머지를 볼 필요 없이 파생 데이터다.
총 자산은 2·4번만 보면 가변 상태로 오판하게 되므로, 계산 가능성을 먼저 물어야 한다.

### 왜 이 분류가 결정적인가

초보가 겪는 데이터 버그 대부분이 **파생 데이터를 필드로 저장해서** 생긴다.

```python
# ❌ 총자산은 파생 데이터인데 필드로 들고 있다
var cash: int = 1000
var total_asset: int = 1000

# → 현금을 바꾸는 코드가 3곳으로 늘어나면?
#   한 곳이라도 total_asset 갱신을 빼먹는 순간 화면과 실제가 어긋난다.
#   "자산 1200원인데 왜 1500원짜리를 못 사?" 같은 버그.

# ✅ 필요할 때 계산한다
var cash: int = 1000

func get_total_asset() -> int:
	return cash + _holdings_value()
```

캐시는 느려질 때 넣는 최적화지, 처음부터 넣을 구조가 아니다.
**설계 목표는 "가변 상태를 최대한 줄이고 나머지를 전부 파생으로 만드는 것".** 값이 두 곳에 있으면 어긋날 수 있고, 한 곳에 있으면 어긋날 수 없다.

## 3. `Resource` — 직렬화 가능한 데이터 객체

먼저 데이터를 담는 그릇의 선택지:

| 그릇 | 파이썬 비유 | 언제 쓰나 |
| --- | --- | --- |
| `Dictionary` / `Array` | `dict` / `list` | 임시 데이터. 오타가 런타임에야 터져서 구조용으론 비추천 |
| `RefCounted` 상속 클래스 | 일반 클래스 | 가벼운 런타임 객체. 파일 저장이 필요 없을 때 |
| `Resource` | `BaseModel` **+ JSON 파일** | **파일로 저장/로드하는 데이터. 에디터에서 편집 가능** |
| `Node` | — (게임 고유 개념) | 씬 트리에 붙는 것. **데이터 그릇으로 쓰면 무겁다.** 화면·서비스용 |

`Resource` **= 값 묶음에 이름·타입을 붙인 클래스 + 그것을 파일(**`.tres`**)로 저장할 수 있는 능력.**

```python
# item_def.gd — 아이템의 "정의 데이터" 스키마
class_name ItemDef
extends Resource

# @export를 붙인 변수만 파일에 저장되고, 에디터 인스펙터에 나타난다
@export var display_name: String = ""
@export var price: int = 0

# @export_range는 인스펙터에 슬라이더를 그려주고 범위를 강제한다 (≈ pydantic Field(ge=, le=))
@export_range(0.0, 1.0, 0.01) var drop_rate: float = 0.5

# 파생 데이터는 필드가 아니라 함수로. 원본이 바뀌면 자동으로 따라온다
func expected_price() -> float:
	return price * drop_rate
```

에디터에서 값을 채워 `res://data/items/포션.tres`로 저장하면 `load()`로 읽어 쓴다.

### 강한 이유 4가지

| # | 이유 | 설명 |
| --- | --- | --- |
| 1 | **값을 코드에서 분리** | 밸런스를 고칠 때 스크립트가 아니라 `.tres` 파일만 수정한다 (≈ 하드코딩 상수를 YAML로 빼는 것) |
| 2 | **스키마 1개 : 파일 N개** | `ItemDef` 하나로 아이템 100종을 코드 한 줄 안 늘리고 추가한다 |
| 3 | **폼 편집** | 인스펙터가 타입에 맞는 입력칸을 그려준다. YAML은 오타가 런타임에 터지지만 `Resource`는 편집 시점에 막힌다 |
| 4 | **노드에 꽂아 넣기** | `@export var item: ItemDef` → 에디터에서 `.tres`를 드래그. 연결 정보가 씬 파일에 저장되므로 `load("경로")` 하드코딩이 사라진다 |

```python
item_def.gd              ← 스키마 (클래스)
res://data/items/
├── 무기.tres            ← 인스턴스
├── 포션.tres
└── 잡화.tres
```

`ItemDef.new()`로 파일 없이 메모리에만 만들어 쓰고 버려도 된다. 그래서 "파일 형식"이 아니라 **"저장할 수도 있는 데이터 클래스"** 다.

### `res://` vs `user://`

| 용도 | 위치 | 성격 |
| --- | --- | --- |
| 정의 데이터 | `res://` — 빌드에 포함, **런타임 쓰기 불가** | 아이템 스탯, 종목 정의 |
| 세이브 데이터 (가변 상태) | `user://` — 유저 PC에 쓰기 가능 | 현금, 인벤토리, 현재 턴 |

```python
ResourceSaver.save(save_data, "user://slot1.tres")   # 저장
var loaded = load("user://slot1.tres")               # 불러오기
```

- macOS에서 `user://`의 실제 경로는 `~/Library/Application Support/Godot/app_userdata/{프로젝트명}/`
- 백엔드 비유: 정적 애셋 디렉터리와 업로드 디렉터리를 나누는 것과 같은 이유.
- ⚠️ 세이브를 `.tres`로 쓰면 파일 안에 **스크립트 경로가 기록**되어, 스크립트를 옮기거나 필드를 지우면 옛 세이브가 안 열릴 수 있다. 그래서 세이브를 JSON으로 쓰는 프로젝트도 많다.

## 4. 데이터 주도 설계 (data-driven design)

게임 동작을 코드가 아니라 외부 데이터로 기술하는 방식.

```python
# 데이터 개수만큼 UI를 생성한다. .tres를 추가하면 코드 수정 없이 버튼이 늘어난다.
@export var items: Array[ItemDef] = []

func _ready() -> void:
	for item in items:
		var button := Button.new()
		button.text = "%s (%d원)" % [item.display_name, item.price]
		# bind는 "이 버튼이 어떤 아이템인지"를 핸들러 인자로 미리 묶어둔다 (≈ functools.partial)
		button.pressed.connect(_on_item_pressed.bind(item))
		$ItemButtons.add_child(button)

func _on_item_pressed(item: ItemDef) -> void:
	print("%s 구매" % item.display_name)
```

- 목적: **기획자가 프로그래머 없이 밸런스를 조정**하고, **코드가 아니라 데이터로 게임 분량을 늘리는** 것.
- 업계 격언: **코드는 동사, 데이터는 명사.**

### 코드 / 데이터 / 애셋의 실제 분할

"구조는 코드, 내용은 데이터"가 아니다. **구조도 데이터로 빠진다.** 코드에 남는 건 **규칙·동작**이다.

| 파일 | 담당 | 정식 용어 |
| --- | --- | --- |
| `.tscn` | 화면 **구조·배치** (좌표, 폰트 크기) | 씬(scene) |
| `.gd` | **규칙·동작** | 스크립트, 로직 |
| `.tres` | **수치·문자열** | 정의 데이터(static data) |
| `.png` / `.ogg` / `.ttf` | **이미지·사운드·폰트** | **애셋(asset)** |
- 데이터와 애셋을 합쳐 **콘텐츠(content)** 라 한다. 이미지는 "static data"라 하지 않고 **애셋**이라 한다.
- Godot은 이걸 통합했다. `.tres`**,** `.png`**,** `.ogg`**,** `.tscn`**이 전부** `Resource`**다**
(이미지 = `Texture2D`, 사운드 = `AudioStream`, 씬 = `PackedScene`).

```python
@export var icon: Texture2D           # 인스펙터에 .png를 드래그
@export var use_sound: AudioStream
```

수치와 애셋을 같은 방식으로 다룬다. `load("res://icons/potion.png")` 같은 경로가 코드에 없다는 게 핵심.

### 어디까지 데이터로 뺄 것인가

과하게 적용하면 **오버엔지니어링**이 된다.

| 빼는 게 맞다 | 코드에 두는 게 맞다 |
| --- | --- |
| 같은 모양이 여러 개 반복되는 것 (아이템 100종) | 한 번만 등장하는 로직 (파산 처리 흐름) |
| 밸런스 조정 대상 — 값을 바꿔가며 자주 시험할 것 | 조건 분기와 규칙 자체 |
| 번역 대상 문자열 | 데이터로 빼면 오히려 읽기 어려워지는 것 |
| 프로그래머가 아닌 사람이 만질 것 |  |

"성공하면 돈을 더한다"는 **규칙**까지 데이터로 빼려 하면 결국 `.tres` 안에 스크립트 언어를 새로 만들게 된다. 디버거도 못 쓰고 타입 검사도 없어진다.
→ **로직은 코드에, 값은 데이터에.**

## 5. 자주 밟는 함정 3개

### 5-1. 정의 데이터를 런타임에 고치려는 것 → `base_` 패턴

**게임 규칙이 바뀌면 값의 분류도 바뀐다.** "돈을 써서 드롭률을 올리는 업그레이드"를 넣으면 드롭률은 가변 상태가 되어야 한다.
그런데 `.tres`의 값을 직접 고치면 안 된다.

- 모든 인스턴스가 **같은** `Resource` **객체를 참조**하므로 다른 곳까지 오염된다.
(이 공유 구조가 **Flyweight 패턴**. 공유되는 불변 부분을 **intrinsic state**, 개별 가변 부분을 **extrinsic state**라 한다)
- 새 게임을 시작해도 값이 안 돌아오고, `res://`는 런타임 쓰기가 불가능하다.

세 종류를 조합하는 것이 정석이다.

```python
base_drop_rate = 0.5                    # 정의 데이터 (.tres) — 기본값, 불변
upgrade_level = { "potion": 2 }         # 가변 상태 (세이브 대상)

func actual_drop_rate(item: ItemDef, level: int) -> float:   # 파생 데이터 — 매번 계산
	return minf(item.base_drop_rate + 0.02 * level, 1.0)
```

`baseAttack`, `basePrice`처럼 `base_` **접두사는 "여기에 보정값이 더해진다"는 신호**다.

### 5-2. 파생 데이터가 노드에 저장된다 — 보관형 UI

> **단방향 데이터 흐름(unidirectional data flow)**: 화면은 상태의 함수다. (`UI = f(state)`)
백엔드 비유: Django 템플릿. 렌더링 결과를 DB에 저장하지 않고 컨텍스트에서 매번 렌더링한다.
> 

그런데 `$MoneyLabel.text`는 개념적으로 파생 데이터지만 **실제로는 Label 노드 안에 저장된다.**
Godot·Unity UI·Qt·DOM은 **보관형 UI(retained mode GUI)** 라서 위젯이 값을 들고 있다 (반대는 매 프레임 다시 그리는 **즉시 모드 UI**, 예: Dear ImGui).

즉 DB 용어로 정확히 **구체화된 뷰(materialized view)** 다. 캐시이므로 **원본과 어긋날(stale) 수 있고, 갱신 배선을 직접 해줘야 한다.**

```python
[node name="BalanceLabel" type="Label" parent="."]
text = "잔액: 0원"        ← 씬을 열면 실제 잔액과 무관하게 일단 이게 그려진다
```

```python
func _ready() -> void:
	Wallet.balance_changed.connect(_on_balance_changed)
	_update_label()   # 씬 파일에 굳어있는 낡은 값을 실제 상태로 덮어쓴다
```

이 한 줄이 빠지면 **상태는 멀쩡한데 화면만 거짓말하는** 버그가 된다.

### 5-3. 캐시를 원본으로 읽는 것

```python
# ❌ 라벨 텍스트를 파싱해서 값을 얻는다 (캐시를 원본으로 착각)
var balance = int($BalanceLabel.text.trim_prefix("잔액: ").trim_suffix("원"))

# ✅ 항상 단일 진실 공급원(single source of truth)에서 읽는다
var balance = Wallet.balance
```

그리고 **갱신 경로를 하나로 만든다.** `$BalanceLabel.text`를 수정하는 코드는 `_update_label()` 한 곳이어야 한다.
→ 시그널을 쓰는 진짜 이유가 이것이다. 원본이 바뀌면 발행 → 구독자가 각자 파생값 갱신. 갱신을 빼먹을 구멍이 구조적으로 막힌다.

### 참고: 코드에 박힌 포맷 문자열은 무엇인가

`button.text = "%s (%d원)" % [...]` 에서 포맷 문자열은 **입력이지 출력이 아니므로 정의 데이터** 성격이고, 더 정확히는 **뷰 템플릿(view template)** 이다.

```python
ItemDef (.tres)  →  컨텍스트 데이터  |  "%s (%d원)"  →  템플릿  |  button.text  →  렌더링 결과 (파생 데이터)
```

**재료는 정의 데이터, 결과물은 파생 데이터.** 재료가 파일에 있든 코드에 있든 재료는 재료다.
다만 **다국어 지원(localization)** 때문에 결국 코드 밖 **문자열 테이블(string table)** 로 빼게 된다 (Godot은 `tr()` + 번역 CSV).
지금 할 일은 아니고, 습관 하나만 들이면 된다 → **화면에 보이는 문자열은 한 곳에 모아둔다.**

## 6. 오늘 프로젝트에 적용한 것

슬롯머신 1대를 **베팅 기계 3대**로 확장했다. 주식의 "종목별 위험 대비 수익"과 같은 구조 연습.

- `tutorials/scripts/MachineDef.gd` — 기계 1대의 정의 데이터 스키마 (`Resource` 상속).
`display_name`, `success_chance`(`@export_range` 슬라이더), `payout`, `loss` + 기대값은 `expected_value()` 함수로
- `tutorials/data/machines/{coin,silver,gold}.tres` — 인스턴스 3개
- `tutorials/scenes/Game.tscn` — 루트 `Game` 노드의 `machines` 배열에 `.tres` 3개 연결. `EarnButton` 제거, `MachineButtons`(`VBoxContainer`) 추가
- `tutorials/scripts/Game.gd` — `machines`를 순회해 버튼을 **런타임 생성**

| 기계 | 성공 확률 | 성공 | 실패 | 기대값 |
| --- | --- | --- | --- | --- |
| 동전 기계 | 70% | +40 | -50 | **+13** (안전, 조금 이득) |
| 은 기계 | 35% | +150 | -80 | **+0.5** (본전) |
| 황금 기계 | 8% | +1200 | -150 | **-42** (손해지만 대박 가능) |

### 데이터 분류 전수 조사

**정의 데이터** — `MachineDef`의 4개 필드 × 기계 3대 (`.tres`)

**가변 상태** — 3개뿐

| 값 | 위치 | 세이브 대상 |
| --- | --- | --- |
| `money` | `GameState.gd:8` (Autoload) | **O** |
| `win_streak` | `Game.gd:7` (Game 씬) | X |
| `lose_streak` | `Game.gd:8` (Game 씬) | X |

**어느 노드에 사는지가 수명과 세이브 여부를 결정한다.** `money`는 Autoload에 있어 게임이 켜져 있는 동안 유지되지만, `win_streak`은 Game 씬 소속이라 은행에 다녀오면 씬이 새로 만들어지며 0으로 초기화된다.

**파생 데이터** — 전부 함수 안에서 계산되고 어디에도 저장되지 않는다

| 파생값 | 위치 | 무엇으로부터 |
| --- | --- | --- |
| 기대값 | `MachineDef.gd:19` | 정의 데이터 |
| 버튼 문구 / 개수 | `Game.gd:22~24` | 정의 데이터, `machines` 길이 |
| 자산 라벨 | `Game.gd:73`, `Bank.gd:25` | `money` |
| 연승/연패 문구 | `Game.gd:78~82` | `win_streak`, `lose_streak` |
| 라벨 색상 | `Game.gd:52`, `56` | `money_changed`의 `delta` |
| 버튼 비활성화 | `Game.gd:66~67` | 파산 여부 |

파생값을 담는 **변수가 하나도 없다**는 게 핵심.

### 세 종류가 맞물려 도는 흐름

```python
[정의 데이터]  silver.tres 의 success_chance=0.35, payout=150
                        ↓  읽기만 함
[판정]         randf() < 0.35  →  성공
                        ↓
[가변 상태]    GameState.money += 150      ← 유일하게 "쓰기"가 일어나는 곳
                        ↓  money_changed 시그널
[파생 데이터]  MoneyLabel.text, StatusLabel 색상, win_streak++ → StreakLabel
```

**쓰기가 일어나는 지점이** `money` **한 곳**이라는 게 이 구조의 핵심. `Bank.gd`도 같은 시그널을 구독해 코드 수정 없이 동기화된다.

### 경계에 있는 것 — `win_streak`

지금은 `win_streak += 1`로 **결과만 누적**하므로 가변 상태다. 만약 승패 기록 배열을 보관하면 연승은 그 배열로부터 **계산**되므로 파생 데이터가 된다.

**가변 상태와 파생 데이터의 경계는 "원본 기록을 보관하는지"에 달려 있다.**
주식에서는 가격 이력을 보관하는 쪽이 정답이다. 그러면 등락률·이동평균·차트가 전부 파생 데이터로 계산된다.

## 프로젝트 구조

```
Makefile               # make editor(에디터 열기) / make run(게임 실행)
tutorials/
├── scenes/
│   ├── Title.tscn   # 타이틀: 게임 시작(초기 자금 500원), 게임 종료
│   ├── Game.tscn    # 베팅 기계 3대(런타임 생성), 은행가기, 색상/연승연패/파산
│   └── Bank.tscn    # 은행: 대출받기, 돌아가기
├── scripts/
│   ├── Title.gd
│   ├── Game.gd        # machines 순회 → 버튼 생성, 베팅 판정
│   ├── Bank.gd
│   ├── GameState.gd   # Autoload. money(가변 상태) + money_changed/went_bankrupt 시그널
│   └── MachineDef.gd  # Resource. 기계 1대의 정의 데이터 스키마
└── data/
    └── machines/      # 정의 데이터 인스턴스
        ├── coin.tres    # 70% / +40 / -50
        ├── silver.tres  # 35% / +150 / -80
        └── gold.tres    # 8%  / +1200 / -150
```

## 실습

1. 3개의 슬롯머신을 생성하고, 각 슬롯머신의 성공확률과 성공 및 실패시의 변화 금액을 정의 데이터로 관리

![베팅 기계 3대 런타임 생성 동작](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/8.gif)

2. 버그: 연승기록은 항상 유지되어야 하나, 씬 내에서만 관리되어 은행에 다녀온 후 초기화 되는 모습

![은행에 다녀오면 연승 기록이 초기화되는 버그](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/9.gif)

---

> 이전 글: [게임 만들기 - Godot 시그널 배우기](/posts/2026-07-23-game_maker/)