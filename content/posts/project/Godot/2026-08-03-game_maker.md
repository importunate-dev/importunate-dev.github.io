---
title: "게임 만들기 - Godot 주가 이력·Scene 분리·선 그래프 구현하기"
date: "2026-08-03"
description: "Godot에서 주가 이력을 상태로 저장하고 장소별 Scene을 분리한 뒤 Control과 draw_polyline으로 주가 그래프를 구현하는 과정"
categories:
  - "project"
tags:
  - "game_maker"
  - "project"
  - "Godot"
  - "game-data"
  - "scene"
  - "stock-chart"
series:
  - "Godot"
ShowToc: true
TocOpen: false
---

## 오늘 한 것

- 주별 주가 이력을 `StockState.price_history`에 저장
- 현재가, 주간 등락액, 주간 등락률을 가격 이력에서 계산
- 기존 `Game` 화면에 섞여 있던 도박장, 주식시장, 은행을 장소별 Scene으로 분리
- 장소 선택 화면에 현재 시간과 보유 현금을 표시
- Godot의 `Control`과 `Node2D`가 각각 어떤 역할을 맡는지 학습
- 가격 이력을 화면 좌표로 변환하고 `draw_polyline()`으로 종목별 선 그래프를 그림

오늘은 앞서 배운 정의 데이터·가변 상태·파생 데이터 분류를 주가 이력에 적용한 뒤,
Godot의 Scene 분리와 사용자 정의 UI 그리기라는 새로운 개념으로 확장했다.

## 1. 주가 이력은 가변 상태다

기존에는 종목별 현재 가격 하나만 저장했다.

```
삼성전자 현재가 = 10,300원
```

하지만 현재가만으로 지난주 가격을 복원할 수는 없다. 지난주 대비 등락과 선 그래프를
만들려면 매주 가격을 스냅샷으로 보관해야 한다.

```
price_history = [10,000, 10,300, 9,900]
                                      ↑ 현재 가격
                              ↑ 지난주 가격
```

각 가격은 기록된 뒤 수정하지 않는 스냅샷이지만, 배열에는 매주 새 값이 추가된다.
따라서 `price_history` 전체는 가변 상태이며 세이브 대상이다.

현재 구현에서는 현재 가격도 별도 필드로 중복 저장하지 않는다.

```
var current_price: int:
	get:
		return price_history.back()
```

데이터 분류는 다음과 같이 바뀌었다.

| 값 | 분류 |
| --- | --- |
| `StockDef.initial_price` | 정의 데이터 |
| `StockState.price_history` | 가변 상태 |
| `StockState.current_price` | 이력의 마지막 값인 파생 데이터 |
| 주간 등락액 | 마지막 두 가격으로 계산하는 파생 데이터 |
| 주간 등락률 | 마지막 두 가격으로 계산하는 파생 데이터 |

```
주간 등락액 = 현재 가격 - 지난주 가격
주간 등락률 = 주간 등락액 / 지난주 가격 × 100
```

### 이력이 계속 길어지는 문제

모든 이력을 영원히 저장하는 것이 항상 최선은 아니다. 그러나 현재 규모에서는
구조를 단순하게 유지하는 이득이 더 크다.

```
회사 3개 × 100년 × 52주 = 15,600개의 가격
```

회사 수와 플레이 기간이 실제로 커지면 다음 중 하나를 선택할 수 있다.

- 최근 52주 또는 104주만 저장
- 최근 데이터는 주별, 오래된 데이터는 월별·연도별로 압축
- 전체 이력은 저장하되 화면에는 최근 구간만 전달
- `PackedInt32Array`나 원형 버퍼로 메모리 구조 최적화

현재의 `Array[int]`는 영구적인 최종 설계라기보다 현재 프로젝트 규모에 충분하고
학습하기 쉬운 설계다.

## 2. 장소별 Scene 분리

기존 `Game` Scene에는 도박 기계, 주식 가격, 다음 주 버튼, 은행 이동이 한 화면에
모여 있었다. 오늘은 장소 선택 화면을 중심으로 역할을 분리했다.

```
Title
  └─ 게임 시작
       ↓
Game — 장소 선택
  ├─ Casino — 도박장
  ├─ StockMarket — 주식시장
  └─ Bank — 은행

Casino / StockMarket / Bank
  └─ 장소 선택으로 → Game
```

각 Scene의 역할은 다음과 같다.

| Scene | 책임 |
| --- | --- |
| `Title` | 새 게임 상태 초기화 |
| `Game` | 현재 시간·보유 현금 표시, 다음 주 진행, 장소 선택 |
| `Casino` | 베팅 기계, 성공·실패, 연승·연패, 파산 처리 |
| `StockMarket` | 현재가, 주간 등락, 가격 이력 그래프 표시 |
| `Bank` | 대출과 보유 현금 표시 |

### Scene과 상태의 수명

`change_scene_to_file()`을 호출하면 현재 Scene은 제거되고 새로운 Scene이 생성된다.
따라서 `Casino`의 노드와 지역 변수는 도박장을 떠날 때 사라진다.

반면 Autoload인 `GameState`는 Scene보다 오래 살아 있다.

```
Casino Scene 제거
    ↓
GameState.money 유지
GameState.current_turn 유지
GameState.stock_states 유지
    ↓
Game Scene 생성 후 최신 상태를 다시 화면에 표시
```

백엔드에 비유하면 각 Scene은 요청마다 새로 만들어지는 화면 컨트롤러에 가깝고,
`GameState`는 여러 화면이 공유하는 애플리케이션 상태 저장소에 가깝다.

### 보유 현금과 총자산

주식을 도입하면 현금과 총자산은 더 이상 같은 값이 아니다.

```
보유 현금 = 당장 사용할 수 있는 돈
총자산 = 보유 현금 + 보유 주식 평가액 + 다른 자산
```

따라서 기존의 `자산: 500원` 표기를 `보유 현금: 500원`으로 수정했다. 총자산은
매수·매도와 보유 주식이 구현된 뒤 파생 데이터로 표시한다.

## 3. `Node2D`와 `Control`

Godot의 주요 2D 표시 클래스 구조는 다음과 같다.

```
Node
└─ CanvasItem
   ├─ Node2D
   │  ├─ Sprite2D
   │  ├─ CharacterBody2D
   │  ├─ RigidBody2D
   │  └─ Area2D
   └─ Control
      ├─ Label
      ├─ Button
      ├─ TextureRect
      └─ Container
         ├─ VBoxContainer
         └─ HBoxContainer
```

### `Node2D`

`Node2D`는 2D 게임 세계의 좌표, 회전, 확대·축소를 다루는 기반 클래스다.

- 캐릭터
- 몬스터
- 맵
- 아이템
- 투사체

`Node2D`라고 해서 자동으로 물리 객체가 되는 것은 아니다. `Sprite2D`도
`Node2D`지만 중력이나 충돌이 없다. Godot의 내장 2D 물리에 직접 참여하려면
목적에 맞는 물리 클래스를 사용한다.

| 목적 | 클래스 |
| --- | --- |
| 중력과 힘으로 움직임 | `RigidBody2D` |
| 코드로 움직이며 충돌 | `CharacterBody2D` |
| 움직이지 않는 벽과 바닥 | `StaticBody2D` |
| 영역 진입과 겹침 감지 | `Area2D` |

따라서 정확한 관계는 다음과 같다.

> Godot의 내장 2D 물리에 직접 참여하는 객체는 `Node2D` 계열이지만, 모든
`Node2D`가 물리 객체인 것은 아니다.
>

### `Control`

`Control`은 화면 UI의 사각형 영역과 레이아웃을 다루는 기반 클래스다.
Godot만의 독특한 아이디어라기보다 Qt의 `QWidget`, 웹의 UI 요소처럼 대부분의
UI 프레임워크에 있는 개념을 Godot가 `Control`이라고 부르는 것이다.

`Control`은 다음 기능을 제공한다.

- 위치와 가로·세로 크기
- 최소 크기
- 앵커와 여백
- `Container`에 의한 자동 배치
- 마우스 입력과 포커스
- `_draw()`와 각종 직접 그리기 함수
- `queue_redraw()`를 통한 다시 그리기 요청

```
Node2D의 중심  = 게임 세계의 Transform
Control의 중심 = UI의 사각형 레이아웃
```

RPG에서는 일반적으로 캐릭터와 맵은 `Node2D` 계열, 메뉴와 인벤토리와 스킬
아이콘은 `Control` 계열로 만든다. 카메라와 무관하게 화면에 고정할 HUD는 보통
`CanvasLayer` 아래에 `Control`들을 둔다.

```
CanvasLayer
└─ Control
   ├─ HealthBar
   ├─ SkillButtons
   └─ MenuButton
```

몬스터 머리 위 체력바처럼 게임 세계의 물체를 따라다니는 `Control`도 만들 수 있다.
다만 체력바가 물리 객체가 되는 것은 아니며 몬스터의 위치를 따라갈 뿐이다.

## 4. 사용자 정의 `StockChart` Control

주가 그래프는 UI 레이아웃 안에 배치되고 물리 기능이 필요하지 않으므로
`Control`을 상속한다.

```
class_name StockChart
extends Control
```

이 상속으로 `StockChart`는 다음 기능을 직접 사용할 수 있다.

```
size
custom_minimum_size
_draw()
queue_redraw()
draw_rect()
draw_polyline()
draw_circle()
```

GDScript에서는 Godot 엔진의 `Control` 클래스를 별도로 import하지 않는다.
`extends Control` 한 줄로 상속 관계를 선언하면 `Control`과 그 조상 클래스의
속성과 메서드를 모두 사용할 수 있다.

그리기 함수들은 정확히는 `Control`에 직접 정의된 것이 아니라 부모 클래스인
`CanvasItem`에 정의되어 있다.

```
CanvasItem
├─ _draw()
├─ queue_redraw()
├─ draw_rect()
└─ draw_polyline()
    ↓ 상속
Control
    ↓ 상속
StockChart
```

따라서 사용하는 입장에서는 `Control`을 상속했을 때 제공되는 기본 내장 API로
보이지만, 실제 상속 경로는 `CanvasItem → Control → StockChart`다.

`_draw()`와 `queue_redraw()`의 성격도 서로 다르다.

| 함수 | 정의와 구현 | `StockChart`의 역할 |
| --- | --- | --- |
| `_draw()` | `CanvasItem`이 호출 규칙을 제공하는 가상 콜백 | 그리기 내용을 재정의 |
| `queue_redraw()` | `CanvasItem`에 동작이 구현된 엔진 메서드 | 상속받은 함수를 그대로 호출 |
| `draw_polyline()` | `CanvasItem`에 구현된 그리기 메서드 | `_draw()` 안에서 호출 |
| `set_prices()` | Godot에 없는 함수 | `StockChart`가 새로 정의 |

우리 코드에서 `_draw()`를 정의하는 것은 이름이 우연히 같은 일반 함수를 만드는 것이
아니라 Godot이 마련한 콜백을 재정의하는 것이다. 반면 `queue_redraw()`의 정의는
우리 프로젝트에 없으며 `extends Control`을 통해 상속받아 사용한다.

`StockMarket`은 각 종목마다 라벨과 그래프를 묶은 행을 생성한다.

```
StockPrices (VBoxContainer)
├─ 삼성전자 행 (VBoxContainer)
│  ├─ Label
│  └─ StockChart
├─ SK하이닉스 행
│  ├─ Label
│  └─ StockChart
└─ 현대자동차 행
   ├─ Label
   └─ StockChart
```

`custom_minimum_size`는 정확한 크기를 강제하는 값이 아니라 부모 Container에
요청하는 최소 크기다. 실제 크기는 `VBoxContainer`가 남는 공간과 레이아웃 규칙에
따라 결정한다.

## 5. 가격을 화면 좌표로 변환하기

가격 배열을 `draw_polyline()`에 그대로 전달할 수는 없다. `draw_polyline()`은
가격이 아니라 `Vector2(x, y)` 화면 좌표의 배열을 받는다.

### x 좌표

x 좌표는 이력에서 몇 번째 가격인지를 그래프 너비에 고르게 배치한다.

```
x = 왼쪽 여백 + 사용 가능한 너비 × index / (가격 개수 - 1)
```

```
가격 4개

●────────●────────●────────●
0        1        2        3
```

가격이 하나뿐이면 나눗셈을 할 수 없고 선도 만들 수 없으므로 그래프 중앙에 점 하나를
표시한다.

### y 좌표

각 가격이 최저가와 최고가 사이에서 어느 위치에 있는지 0부터 1 사이로 정규화한다.

```
가격 비율 = (현재 가격 - 최저가) / (최고가 - 최저가)
```

화면 좌표는 아래로 갈수록 y가 커진다. 높은 가격을 화면 위쪽에 표시하려면 방향을
뒤집어야 한다.

```
y = 아래쪽 위치 - 그래프 높이 × 가격 비율
```

```
최고가 120원 ── 화면 위쪽
중간값 110원 ── 화면 중앙
최저가 100원 ── 화면 아래쪽
```

모든 가격이 같으면 `최고가 - 최저가`가 0이므로 나눗셈을 하지 않고 모든 점을
그래프 중앙에 놓는다. 결과는 중앙의 수평선이 된다.

### 그래프 업데이트하기

`_draw()`는 우리가 필요할 때 실행하는 일반 함수가 아니라 Godot이 호출하는
콜백 함수다. `_ready()`를 직접 호출하지 않고 Scene Tree에 들어왔을 때 Godot이
호출하는 것과 같다.

`StockChart`가 화면에 처음 나타나면 Godot이 `_draw()`를 호출한다. Godot은 그때
생성된 사각형, 선, 점 등의 그리기 명령을 기억하고 이후 프레임에서 재사용한다.
따라서 가격 배열만 변경해도 Godot이 자동으로 `_draw()`를 다시 호출하지는 않는다.
Godot은 평범한 배열인 `prices`가 그래프 모양에 영향을 준다는 사실을 알 수 없기
때문이다.

가격이 전달되면 그래프는 `_draw()`를 직접 호출하는 대신 다시 그리기를 요청한다.

```
func set_prices(new_prices: Array[int]) -> void:
	prices = new_prices.duplicate()
	queue_redraw()
```

`queue_redraw()`는 즉시 그래프를 그리는 함수가 아니다. 이 `Control`에
"표시 내용이 바뀌었으므로 다시 그려야 한다"는 표시를 남기는 예약 함수다.
그러면 현재 함수가 끝난 뒤 Godot이 적절한 그리기 프레임에 `_draw()`를 호출한다.

```
set_prices() 호출
    ↓
prices 변경
    ↓
queue_redraw() — 다시 그리기 예약
    ↓
set_prices() 종료
    ↓
Godot의 다음 그리기 단계
    ↓
Godot이 StockChart._draw() 호출
    ↓
최저가·최고가와 화면 좌표 계산
    ↓
draw_rect() + draw_polyline() + draw_circle()
```

#### 어떤 그래프를 업데이트하는지 식별하는 방법

`set_prices()`는 `StockChart` 클래스 안에 정의된 인스턴스 메서드다. `StockMarket`은
`stock_charts`라는 `Dictionary`에 `StockState → StockChart` 관계를 보관한다.

```
stock_charts
├─ 삼성전자 StockState → 삼성전자 StockChart
├─ SK하이닉스 StockState → SK하이닉스 StockChart
└─ 현대자동차 StockState → 현대자동차 StockChart
```

가격을 갱신할 때는 먼저 Dictionary에서 특정 종목의 실제 `StockChart` 객체를 꺼낸
다음 그 객체를 대상으로 `set_prices()`를 호출한다.

```
stock_charts[stock_state].set_prices(stock_state.price_history)
```

삼성전자를 처리하는 반복이라면 위 코드는 개념적으로 다음과 같다.

```
samsung_chart.set_prices(samsung_price_history)
```

인스턴스 메서드가 실행될 때 `self`는 메서드 앞에 지정한 실행 대상 객체가 된다.
GDScript에서는 같은 객체의 속성과 메서드에 접근할 때 `self`를 생략할 수 있다.

```
func set_prices(new_prices: Array[int]) -> void:
	self.prices = new_prices.duplicate()
	self.queue_redraw()

# 현재 프로젝트에서는 self를 생략해 다음처럼 작성했다.
func set_prices(new_prices: Array[int]) -> void:
	prices = new_prices.duplicate()
	queue_redraw()
```

| 역할 | 삼성전자 처리 시 객체 |
| --- | --- |
| 호출자 | `StockMarket` |
| 메서드 실행 대상(receiver) | 삼성전자 `StockChart` |
| `set_prices()` 내부의 `self` | 삼성전자 `StockChart` |

따라서 `queue_redraw()`가 호출자를 검색해 갱신 대상을 알아내는 것이 아니다.
처음부터 삼성전자 그래프를 대상으로 `set_prices()`가 호출되었기 때문에 내부의
`queue_redraw()`는 `self.queue_redraw()`, 즉 삼성전자 그래프의 갱신 요청이다.

```
StockMarket
    ↓ 삼성전자 StockChart.set_prices(...)
self = 삼성전자 StockChart
    ↓ self.queue_redraw()
삼성전자 StockChart만 그래프 업데이트 예약
```

세 종목의 그래프가 모두 업데이트되는 이유도 한 번의 `queue_redraw()`가 Scene
전체로 전파되기 때문이 아니다. `StockMarket`이 모든 종목을 순회하며 각
`StockChart`에서 `set_prices()`와 `queue_redraw()`를 각각 호출하기 때문이다.

Godot의 한 프레임에는 입력 처리, 게임 상태 변경, 물리 처리, UI 레이아웃 계산,
화면 그리기 같은 단계가 있다. 실제 그리기를 엔진에 맡기면 `Control.size`와 위치가
확정된 뒤 다른 UI와 올바른 순서로 그릴 수 있다. 같은 프레임 안에서
`queue_redraw()`를 여러 번 호출해도 Godot은 다시 그리기 요청을 모아 한 번만
처리할 수 있다.

`draw_polyline()`과 같은 함수는 Godot이 제공한 그리기 단계 안에서 사용해야 한다.
따라서 `set_prices()`에서 직접 그리거나 `_draw()`를 수동 호출하지 않는다.

```
# 잘못된 흐름: 지금은 Godot의 그리기 단계가 아니다
func set_prices(new_prices: Array[int]) -> void:
	prices = new_prices
	draw_polyline(...)

# 올바른 흐름: 데이터 변경과 그리기 시점을 분리한다
func set_prices(new_prices: Array[int]) -> void:
	prices = new_prices.duplicate()
	queue_redraw()

func _draw() -> void:
	draw_polyline(...)
```

`Label.text`나 `Button.text` 같은 내장 UI 속성은 값이 바뀔 때 해당 클래스 내부에서
자동으로 다시 그리기를 요청한다. `StockChart`는 직접 만든 UI이므로 가격이 바뀌면
`queue_redraw()`도 직접 호출해야 한다.

웹 브라우저에서 DOM을 변경하면 브라우저가 다음 렌더링 시점에 레이아웃과 페인트를
수행하는 것과도 비슷하다.

```
웹:   DOM 변경     → 브라우저의 다음 paint
Godot: prices 변경 → queue_redraw() → 다음 _draw()
```

따라서 `queue_redraw()`는 "다시 그린다"보다 **"다시 그리도록 예약한다"**로
이해하는 것이 정확하다.

그래프 좌표를 별도 상태로 저장하지 않는다는 점이 중요하다.

| 값 | 분류 |
| --- | --- |
| 가격 이력 | 가변 상태 |
| 최저가·최고가 | 파생 데이터 |
| 그래프의 `Vector2` 좌표들 | 파생 데이터 |
| 화면에 그려진 선과 점 | 파생된 UI 표현 |

## 6. 구현 위치

```
tutorials/
├── scenes/
│   ├── Game.tscn          # 장소 선택, 시간, 보유 현금, 다음 주
│   ├── Casino.tscn        # 도박장
│   ├── StockMarket.tscn   # 주식 목록과 그래프 Container
│   └── Bank.tscn          # 은행
└── scripts/
    ├── Game.gd            # 장소 이동과 허브 UI 갱신
    ├── Casino.gd          # 도박 로직
    ├── StockMarket.gd     # 종목별 라벨과 StockChart 생성
    ├── StockChart.gd      # 가격→좌표 변환과 직접 그리기
    ├── StockState.gd      # 가격 이력과 등락 계산
    └── GameState.gd       # 턴 진행과 종목별 새 가격 기록
```

## 7. 실습

1. 턴에 따라 변하는 주가

    ![턴에 따라 종목별 주가가 변하는 모습](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/godot/2026-08-03/stock-change.gif)

2. 화면 정리를 위해 장소 이동 화면 추가

    ![도박장, 주식시장, 은행을 선택하는 장소 이동 화면](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/godot/2026-08-03/location-selection.gif)

3. 주식 변화를 그래프로 표시

    ![주가 이력을 종목별 선 그래프로 표시한 모습](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/godot/2026-08-03/stock-chart.gif)
