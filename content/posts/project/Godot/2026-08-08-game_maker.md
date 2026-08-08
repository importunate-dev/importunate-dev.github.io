---
title: "게임 만들기 - Godot 주식 매매·뉴스 이벤트·해상도 설정 구현하기"
date: "2026-08-08"
description: "Godot에서 주식 매매와 평단가·수익률을 구현하고, 가중치 기반 뉴스 이벤트와 해상도 독립적인 화면 설정을 적용하는 과정"
categories:
  - "project"
tags:
  - "game_maker"
  - "project"
  - "Godot"
  - "stock-trading"
  - "weighted-random"
  - "resolution"
series:
  - "Godot"
ShowToc: true
TocOpen: false
---

## 오늘 한 것

- `StockDef`에 업종, CEO 이름, CEO 생년월일, 총 발행 주식 수 추가
- 업종을 `enum`으로 정의
- 주식 매수·매도와 지분율 계산 추가
- 회사 상세 정보 화면(`CompanyDetail`) 추가
- 장소 선택 화면에 보유 종목·평단가·평가손익 표 추가
- 주간 뉴스 이벤트 시스템 추가 (`EventDef`, 가중치 추첨, 업종별 주가 반영)
- 8개 업종을 모두 채우도록 종목 6개 추가
- 해상도 독립성 설정 적용 (스트레치 모드)
- 창 크기·전체화면 설정 화면과 영구 저장 추가 (`DisplaySettings`, `ConfigFile`)

## 1. 데이터 추가

회사와 주식 데이터를 확장하고, 이를 사용하는 상세 화면·보유 자산 표·뉴스 이벤트를
추가했다.

### 1.1. 회사·주식 데이터 추가

값 자체를 저장해야 하는 데이터만 `StockDef` 또는 `StockState`에 두고, 다른 값에서
구할 수 있는 데이터는 계산 함수로 만든다.

| 데이터 | 분류 | 처리 방식 | 이유 |
| --- | --- | --- | --- |
| 업종 | 정의 데이터 | `StockDef`에 `enum`으로 저장하고 한글 이름은 딕셔너리로 매핑 | 정해진 값만 선택하게 해 문자열 오타를 막을 수 있음 |
| CEO 이름·생년월일 | 정의 데이터 | `StockDef`에 저장 | 회사마다 고정된 정보임 |
| CEO 나이 | 파생 데이터 | 생년월일과 게임 내 날짜로 계산 | 턴마다 저장된 나이를 갱신할 필요가 없음 |
| 총 발행 주식 수 | 정의 데이터 | `StockDef`에 저장 | 회사마다 고정된 기준값임 |
| 보유 주식 수 | 가변 상태 | `StockState`에 저장하고 매수·매도 때 변경 | 플레이에 따라 계속 달라짐 |
| 지분율 | 파생 데이터 | `보유 주식 수 / 총 발행 주식 수 × 100`으로 계산 | 두 원본 값에서 언제든 구할 수 있음 |
| 매입 원가 합계 | 가변 상태 | `StockState`에 저장하고, 매수 시 더하고 매도 시 평단가 기준으로 차감 | 이동평균법으로 남은 주식의 평단가를 유지할 수 있음 |
| 평단가 | 파생 데이터 | `매입 원가 합계 / 보유 주식 수`로 계산 | 추가 매수 때 별도 필드를 다시 계산할 필요가 없음 |
| 시가총액·평가손익 | 파생 데이터 | 현재 주가와 주식 수·매입 원가로 계산 | 원본 값이 바뀌면 자동으로 최신 값이 됨 |

전량 매도할 때는 반올림 오차가 남지 않도록 보유 주식 수와 매입 원가 합계를 모두
0으로 초기화한다. 정수끼리 지분율이나 평단가를 나눌 때는 먼저 `float`로 변환한다.

### 1.2. 회사 상세 정보 화면 추가

회사 상세 화면은 목록에서 고른 종목 하나를 보여줘야 한다. 그런데
`change_scene_to_file()`은 파일 경로만 받고 인자를 넘길 방법이 없다. 새 씬은
이전 씬이 사라진 뒤에 만들어지기 때문이다.

그래서 어떤 종목을 골랐는지는 **씬보다 오래 사는 곳**에 남긴다. 여기서는 이미
autoload로 띄워 둔 `GameState`가 그 역할을 한다.

```
# 목록 화면: 고른 종목을 남기고 씬을 바꾼다
func _on_detail_pressed(stock_index: int) -> void:
	GameState.selected_stock_index = stock_index
	get_tree().change_scene_to_file("res://tutorials/scenes/CompanyDetail.tscn")
```

```
# 상세 화면: 남겨진 값을 읽어 온다
func _ready() -> void:
	var stock_state := GameState.selected_stock()
	if stock_state == null:
		_on_back_button_pressed.call_deferred()
		return
```

노드를 트리에 붙이면 `_ready()`는 트리 진입 과정에서 자동으로 호출된다. 다만
`_ready()`가 실행 중이라는 것은 부모가 자식 구성을 모두 끝냈다는 뜻이 아니다. 이때
바로 씬을 바꾸면 아직 트리를 구성 중인 부모에서 자식을 제거하려 하므로
`remove_child()`가 거부될 수 있다. `call_deferred()`로 현재 트리 변경 작업이 끝난
뒤까지 미루면 해결된다.

### 1.3. 보유 종목·평단가·평가손익 표 추가

보유 자산을 표처럼 보여줄 때 `Label` 하나에 공백으로 칸을 맞추면 어긋난다. 기본
폰트가 글자마다 폭이 다른 비례폭 폰트이기 때문이다.

`GridContainer`에 열 수를 정해 두고 셀마다 `Label`을 넣으면 열이 맞는다.

```
var grid := GridContainer.new()
grid.columns = 3

for text in ["종목", "보유", "평가액"]:
	var label := Label.new()
	label.text = text
	label.custom_minimum_size = Vector2(150, 0)   # 열 폭
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT   # 숫자는 우측 정렬
	grid.add_child(label)
```

`GridContainer`는 자식을 추가한 순서대로 왼쪽에서 오른쪽으로 채우고, 열 수를 넘기면
다음 줄로 내려간다. 즉 헤더와 데이터 행을 구분해서 넣는 게 아니라 셀을 순서대로
쭉 추가하면 된다.

보유 종목은 늘거나 줄기 때문에 갱신할 때마다 표를 처음부터 다시 그린다.

```
for child in grid.get_children():
	grid.remove_child(child)
	child.queue_free()
```

`queue_free()`만 호출하면 실제 삭제가 프레임 끝까지 미뤄져서, 바로 새 셀을 추가할 때
낡은 셀과 겹쳐 보인다. `remove_child()`로 즉시 떼어낸 뒤 해제해야 한다.

### 1.4. 매주 뉴스 무작위 발생

여러 후보 중 하나를 뽑되 후보마다 나올 확률이 달라야 할 때 쓰는 방법이다. 확률을
직접 적는 대신 **가중치**를 주고, 전체 합에서의 비중으로 확률이 결정된다.

```
# 후보마다 가중치를 갖는다. 합이 1이 아니어도 된다.
var candidates := [
	{"name": "흔한 일", "weight": 40},
	{"name": "가끔 있는 일", "weight": 8},
	{"name": "드문 일", "weight": 2},
]

func pick() -> Dictionary:
	var total_weight := 0
	for candidate in candidates:
		total_weight += candidate.weight

	# 1..total 중 하나를 굴리고 가중치를 순서대로 빼 나간다.
	# 0 이하가 되는 순간의 항목이 당첨이다.
	var roll := randi_range(1, total_weight)
	for candidate in candidates:
		roll -= candidate.weight
		if roll <= 0:
			return candidate
	return candidates.back()
```

총합 50에서 가중치 40이면 80%, 8이면 16%, 2면 4%다. 누적 구간을 만들어 그 안에
난수가 떨어지는지 보는 것과 같은 계산이며, 파이썬 `random.choices(population, weights=...)`가 하는 일이 이것이다.

"아무 일도 일어나지 않는 경우"를 별도 분기로 처리하지 않는 것이 요령이다. 가중치가
큰 "평온한 상태" 항목을 후보 목록에 하나 넣어 두면 같은 로직으로 해결된다.

#### 뉴스 이벤트 추첨 구현

`GameState._pick_event()`가 이 구조 그대로다. 후보는 `EventDef` 리소스이고,
`calm_week.tres`("특별한 소식 없는 한 주")가 가중치 40으로 들어가 있어 뉴스가 없는
주도 같은 추첨으로 처리된다.

### 1.5. 뉴스 효과를 업종별 주가에 반영

여러 효과가 한 값에 동시에 걸릴 때, 변화율을 **더하지 말고 배율로 바꿔 곱한다.**

```
# 나쁜 방법: 변화율을 더한다
var rate := base_rate + effect_a + effect_b     # -0.5 + -0.3 + -0.4 = -1.2
var value := original * (1.0 + rate)            # 음수가 된다

# 좋은 방법: 배율로 바꿔 곱한다
var multiplier := (1.0 + base_rate) * (1.0 + effect_a) * (1.0 + effect_b)
var value := original * multiplier              # 0.5 * 0.7 * 0.6 = 0.21
```

곱셈에는 두 가지 이점이 있다.

- **0 아래로 내려가지 않는다.** 양수끼리 곱하면 결과는 항상 양수라서, 효과가 몇 개
겹치든 가격이 음수가 되지 않는다. 덧셈은 `100%`를 뚫는다.
- **적용 순서가 결과를 바꾸지 않는다.** 곱셈은 교환법칙이 성립하므로 어떤 효과를
먼저 계산하든 같은 값이 나온다.

#### 주가 계산에 뉴스 배율 적용

`GameState._update_stock_prices()`에서 기본 변동(`randf_range(-0.1, 0.1)`)과 이벤트
보정을 각각 배율로 만들어 곱한다. 최악의 조합인 기본 −10%와 폭락 −20%가 겹쳐도
배율이 `0.9 × 0.8 = 0.72`라서 가격이 살아남는다.

### 1.6. 뉴스와 종목 정의 데이터 추가

새 기능을 붙일 때마다 데이터를 어디에 둘지 정해야 하는데, 기준은 계속 같다.

| 분류 | 이벤트 시스템에서 | 어디에 |
| --- | --- | --- |
| 정의 데이터 | 어떤 뉴스가 존재하는가 (제목, 대상, 영향률, 가중치) | `EventDef` (`.tres`) |
| 가변 상태 | 이번 판에서 무엇이 터졌는가 | `GameState.news_log` |
| 파생 데이터 | 이번 턴 각 종목의 최종 변동률 | 계산 |

`StockDef` / `StockState`와 똑같은 구도다. 정의 데이터는 모든 플레이가 공유하고,
가변 상태는 현재 플레이에만 속한다.

업종처럼 종류가 정해진 값을 `enum`으로 둔 이점이 여기서 드러난다. 뉴스의 대상 업종과
종목의 업종을 비교 한 번으로 판정할 수 있고, 문자열이었다면 오타로 매칭이 조용히
실패했을 자리다.

```
func applies_to(stock_definition: StockDef) -> bool:
	if is_zero_approx(price_impact):
		return false
	if affects_all:
		return true
	return stock_definition.industry == target_industry
```

#### 이벤트·종목 데이터 구성

이벤트 정의는 `tutorials/data/events/*.tres` 37건, 종목은
`tutorials/data/stocks/*.tres` 9건이다. 종목이 3개(반도체·자동차)뿐일 때는 뉴스의
61%가 아무 주가도 움직이지 못했다. 8개 업종을 모두 채우자 13.5%로 줄었고, 남은 것은
"평온한 한 주"뿐이다. **정의 데이터끼리도 서로 균형이 맞아야 한다**는 것을 확인한
지점이다.

## 2. 해상도 변경 기능 추가

기준 해상도와 실제 창 크기를 분리하고, 창 크기·전체화면 설정을 저장하도록 만들었다.

### 2.1. 해상도 설정에 필요한 화면 구조

앞서 주가 그래프를 만들며 `Control`이 `CanvasItem`을 상속한다는 것을 배웠다. 해상도
설정을 이해하려면 여기에 `Viewport`와 `Window`의 역할을 연결해야 한다.

```
Node
 ├─ Viewport              픽셀이 그려지는 대상
 │   ├─ Window            Viewport + OS 창
 │   │   └─ Popup, AcceptDialog, PopupMenu ...
 │   └─ SubViewport       게임 내부의 독립된 렌더 타깃
 │
 └─ CanvasItem            Viewport 위에 그려지는 내용
     ├─ Control           Label, Button, Container 같은 UI
     └─ Node2D            2D 게임 세계의 오브젝트
```

`Viewport`와 `CanvasItem`의 차이는 **도화지와 그 위에 그리는 내용**의 차이다.
`Viewport`는 렌더링 결과를 담는 도화지이고, `CanvasItem`은 그 도화지에 그려지는
노드다. `project.godot`의 `canvas_items` 스트레치 모드는 이름 그대로 이
`CanvasItem` 계층을 창 크기에 맞춰 확대한다.

`Viewport` 자체가 OS 창인 것은 아니다. `Viewport` 중 `Window`만 OS에 실제 창으로
노출된다. `SubViewport`는 미니맵이나 감시 카메라처럼 게임 내부에서 별도 화면을
렌더링하지만 OS는 그 존재를 모른다.

#### `Window`와 `Control`

`Window`는 자기 렌더 타깃을 가진 실제 창이고, `Control`은 부모 렌더 타깃 위에
그려지는 UI 사각형이다. 따라서 창처럼 보이는 설정 패널도 새 OS 창이 필요하지 않다면
`Control`로 만든다.

#### `SubViewport`와 `Control`

웹으로 비유하면 `Control`은 `<div>`, `SubViewport`는 `<iframe>`에 가깝다.

|  | `Control` | `SubViewport` |
| --- | --- | --- |
| 하는 일 | 부모 렌더 타깃에 그린다 | 별도로 렌더링한 결과를 넘긴다 |
| 좌표계 | 부모와 공유 | 독립 |
| 해상도 | 부모를 따라감 | 따로 정함 |
| 결과물 | 화면의 픽셀 | 텍스처 |
| 카메라 | 없음 | 자체 카메라 가능 |
| 비용 | 그리기 명령 | 렌더 패스 하나 추가 |

판단 기준은 **이 영역을 독립된 이미지 한 장으로 뽑아야 하는가**이다. 미니맵, 다른
시점의 화면, 화면 전체 후처리에는 `SubViewport`가 필요하지만 현재 설정 화면은 일반
UI이므로 `Control`이면 충분하다. `SubViewport`는 별도 렌더링 비용이 들고 좌표계가
독립적이라 입력도 변환해서 전달해야 한다.

#### `get_window()`가 찾는 창

`get_window()`는 항상 최상단 창을 반환하는 함수가 아니다. 현재 노드에서 부모 방향으로
올라가며 가장 가까운 `Window`를 반환한다. 지금 프로젝트에는 서브 윈도우가 없고
`DisplaySettings`도 루트 바로 아래의 autoload라 결과적으로 루트 창이 반환된다.
최상단 창을 명시적으로 가리킬 때는 `get_tree().root`를 사용한다.

### 2.2. 기준 해상도 1024×600 적용

게임은 화면에 좌표를 직접 지정한다. 그런데 실행될 화면 크기는 사용자마다 다르므로,
좌표를 물리 픽셀로 해석하면 큰 모니터에서는 UI가 구석에 작게 몰린다.

**해상도 독립성**은 좌표를 물리 픽셀이 아니라 고정된 가상 좌표계로 정의하고, 실제
화면에 맞추는 변환을 엔진에 맡기는 개념이다. 이를 위해 크기를 둘로 나눈다.

| 이름 | 정체 | 성질 |
| --- | --- | --- |
| **기준 해상도** (뷰포트) | 좌표의 눈금. 씬의 모든 좌표가 이 기준 | 개발 시 정하고 바꾸지 않음 |
| **창 크기** | OS가 화면에 띄우는 실제 창 | 실행할 때마다 다름 |

`offset_left = 40`은 "화면 왼쪽에서 40픽셀"이 아니라 **"1024칸 좌표계의 40번째 칸"**
을 뜻하게 된다. 실제 픽셀 위치는 나눗셈으로 나온다.

```
실제 픽셀 = 씬에 적은 값 × (창 크기 ÷ 기준 해상도)
                           └───────── 배율 ─────────┘
```

기준 해상도 1024, 창 1536이면 배율 1.5이므로 `offset_left = 40`은 60픽셀 지점에
그려지고, 폰트 크기 18은 27픽셀로 렌더링된다.

여기서 다시 데이터 분류가 적용된다.

| 분류 | 값 |
| --- | --- |
| 정의 데이터 | 기준 해상도 |
| 가변 상태 | 창 크기, 전체화면 여부 |
| 파생 데이터 | **배율** |

배율은 저장하지 않는다. CEO 나이를 생년월일에서 계산하고 평단가를 매입 원가에서
나눴던 것과 같은 판단이다. 저장하면 창 크기가 바뀔 때마다 갱신해야 하고, 한 곳이라도
빠뜨리면 어긋난다.

여기서 뷰포트를 화면상의 표시 위치로 오해하면 안 된다. 뷰포트는 **위치가 아니라
좌표계의 눈금 개수**다. 창을 화면 어디로 옮기든 게임 내용은 변하지 않는다. 창 위치는
OS의 영역이고 뷰포트는 게임 내부의 영역이다.

### 2.3. 창 크기에 맞춰 화면 비율 유지

기준 해상도와 실제 창의 차이를 메우는 방식은 하나가 아니다. 창이 기준보다 1.5배
커졌을 때의 결과로 비교하면 이렇게 갈린다.

| 스트레치 모드 | 동작 | 글씨 |
| --- | --- | --- |
| 변환 없음 (`disabled`) | 캔버스가 원래 크기 그대로, 남는 자리는 여백 | 그대로 |
| 캔버스 확대 (`canvas_items`) | 기준 해상도를 통째로 1.5배 확대 | **커짐** |
| 영역 확장 (`viewport` 계열) | 좌표계 자체가 넓어져 더 많이 보임 | 그대로 |

두 번째는 돋보기, 세 번째는 창문을 넓히는 것에 해당한다. 화면이 넓어지면 지도를 더
보여주는 것이 이득인 게임은 세 번째가 맞고, UI 배치가 고정된 게임은 두 번째가 맞다.

종횡비가 어긋날 때의 처리도 골라야 한다.

| 종횡비 처리 | 결과 |
| --- | --- |
| 유지 + 여백 (`keep`) | 검은 띠가 생기지만 화면이 찌그러지지 않음 |
| 무시하고 늘림 (`ignore`) | 꽉 차지만 원이 타원이 되고 글씨가 뭉개짐 |
| 한 축만 맞춤 (`keep_width` 등) | 찌그러지지 않고 여백도 없으나 보이는 영역이 화면마다 달라짐 |

일반적으로 찌그러뜨리는 것보다 여백이 낫다고 본다.

#### 화면 확대 방식에 따른 화질 차이

확대할 때 정보를 새로 만들어낼 수 있느냐가 갈림길이다.

- **텍스트와 벡터 도형** — 글자 모양이 외곽선 곡선으로 저장돼 있어, 배율이 정해지면
그 크기로 처음부터 다시 래스터화된다. 확대가 아니라 재생성이므로 선명하다.
- **비트맵 이미지** — 픽셀 수가 이미 정해져 있어 없던 픽셀을 만들어내야 한다.
주변을 섞으면 흐려지고, 가까운 픽셀을 복사하면 계단이 생긴다.
- **픽셀아트** — 배율이 정수가 아니면 1픽셀이 1.5픽셀로 나뉘며 반올림이 일어나
도트 크기가 들쭉날쭉해진다. 그래서 정수 배율만 허용하는 옵션을 쓰는 것이 보통이다.

#### 프로젝트 스트레치 설정

`project.godot`의 `[display]` 절에 세 가지를 지정했다.

```
window/size/viewport_width=1024    ; 기준 해상도
window/size/viewport_height=600
window/stretch/mode="canvas_items" ; 캔버스 확대
window/stretch/aspect="keep"       ; 종횡비 유지 + 여백
```

씬 파일은 한 줄도 고치지 않았다. `offset_left = 40`은 계속 1024×600 기준이고 확대는
엔진이 마지막 단계에서 처리한다. `DisplaySettings.PRESETS`의 창 크기를 1280×750,
1440×844처럼 1024:600의 배수로 맞춘 것도 종횡비를 정확히 맞춰 여백을 없애기 위해서다.

### 2.4. 창 크기·전체화면 설정 저장

게임에는 경로가 두 종류 있고, 앞서의 데이터 분류가 파일 위치에도 그대로 대응된다.

|  | `res://` | `user://` |
| --- | --- | --- |
| 누가 정하나 | 개발자 | 플레이어 |
| 언제 | 게임을 만들 때 | 게임이 돌아갈 때 |
| 예시 | 게임 이름, 기준 해상도, 씬, 리소스 | 창 크기, 음량, 키 설정, 세이브 |
| 쓰기 | **불가** | 가능 |

`res://`에 쓸 수 없는 이유는 여러 겹이다.

- **OS 권한** — 설치 폴더는 관리자 권한 영역이라 일반 사용자가 쓸 수 없다.
- **계정 분리** — 한 PC를 여러 사람이 쓰면 설치 폴더의 세이브는 서로 덮어쓴다.
- **패키징** — 빌드하면 `res://` 전체가 `.pck` 아카이브 하나로 압축된다. 경로가
파일시스템이 아니라 아카이브 내부를 가리키는 가상 경로가 되므로 파일을 끼워 넣을
수 없다.
- **업데이트** — 재설치하면 설치 폴더 내용은 교체되고 세이브도 함께 사라진다.
- **샌드박스** — 스토어로 배포하면 접근 가능한 경로가 OS 차원에서 제한된다.

`user://`는 OS마다 정해진 사용자 데이터 표준 위치를 가리키는 별칭이다. macOS는
`~/Library/Application Support/<앱>/`, Windows는 `AppData\Roaming\<앱>\`으로 풀리고,
코드에서는 OS 분기 없이 `user://settings.cfg`라고만 쓴다.

에디터에서 실행할 때는 `res://`가 평범한 폴더라 써도 동작한다. 배포하는 순간 조용히
실패하므로 개발 중에는 드러나지 않는 함정이다.

#### `ConfigFile`로 창 설정 파일 저장

INI 형식을 읽고 쓰는 내장 클래스이며, 파이썬 `configparser`에 해당한다.

```
const CONFIG_PATH := "user://settings.cfg"

func save_settings(volume: float) -> void:
	var config := ConfigFile.new()
	config.set_value("audio", "bgm_volume", volume)
	config.save(CONFIG_PATH)

func load_settings() -> float:
	var config := ConfigFile.new()
	# 파일이 없으면 첫 실행이므로 기본값을 쓴다. 에러가 아니다.
	if config.load(CONFIG_PATH) != OK:
		return 1.0
	return float(config.get_value("audio", "bgm_volume", 1.0))
```

외부 파일에서 읽은 값은 신뢰하지 않는다. 선택지 목록이 나중에 줄어들면 낡은 설정
파일의 인덱스가 배열 범위를 넘을 수 있으므로 `clampi()`로 좁혀 둔다.

#### `DisplaySettings`로 설정 유지

`DisplaySettings`가 autoload인 이유는 `GameState`와 같다. 창 설정은 씬보다 오래
살아야 하고, autoload는 메인 씬보다 먼저 초기화되므로 첫 화면이 그려지기 전에 창
크기가 정해진다.

값을 바꾸는 함수는 모두 `_apply()`(화면 반영) → `_save()`(파일 기록) 순으로 끝난다.
설정 화면(`Settings.gd`)은 상태를 갖지 않고, `settings_changed` 시그널을 받아
`DisplaySettings`에서 현재값을 다시 읽어 그린다.

## 구현 결과

1. 매매, 평단가와 수익률 구현

    ![주식 매매와 평단가 및 수익률을 확인하는 모습](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/godot/2026-08-08/stock-trading.gif)

2. 해상도 조절과 뉴스 이벤트

    ![창 크기를 조절하고 주간 뉴스 이벤트를 확인하는 모습](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/project/godot/2026-08-08/display-settings-news-events.gif)

---

> 이전 글: [게임 만들기 - Godot 주가 이력·Scene 분리·선 그래프 구현하기](/posts/2026-08-03-game_maker/)
