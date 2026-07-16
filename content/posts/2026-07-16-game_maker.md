---
title: "게임 만들기 - Godot 기초 배우기"
date: "2026-07-16"
categories:
  - "study"
tags:
  - "game_maker"
  - "project"
  - "Godot"
  - "node"
  - "script"
  - "scene"
series:
  - "Godot"
ShowToc: true
TocOpen: false
---

# 2026-07-16 — Godot 기초 학습 정리

## 오늘 한 것
- Godot 4.7 설치 (Homebrew)
- 첫 프로젝트 세팅, 씬(`.tscn`)과 스크립트(`.gd`) 연결 확인
- 클릭하면 자산이 오르는 간단한 UI 예제 제작
- 자산이 랜덤(50/50)으로 오르내리는 슬롯머신으로 발전
- 씬 전환(은행 페이지) + 전역 상태(Autoload) 도입
- 상태 메시지("돈을 벌었다!" / "돈을 잃었다!") 표시 추가
- `tutorials/`, `docs/` 폴더로 프로젝트 구조 정리

## 1. 스크립트와 씬

- **씬(Scene)**: 화면에 나타나는 것. 버튼, 라벨 등을 배치해두는 선언적 파일(`.tscn`).
- **스크립트(Script)**: 동작, 변수, 로직 등 실제 코드(`.gd`).

## 2. 노드 vs 변수

- **변수**: 값 하나를 담는 상자.
- **노드**:
  - 객체(라벨, 버튼, 관리자 등). 따라서 자신만의 속성과 함수를 가짐.
  - 씬 정의 파일(`.tscn`) 내에 정의되어 있음.
  - **Autoload**: 노드를 전역으로 등록. `project.godot` 파일에서 등록 가능.

## 3. Autoload (싱글톤)

- 씬이 바뀌어도 사라지지 않는 전역 저장소.
- 실제 정체는 **전역 노드**. 전역 변수는 전역 노드의 속성으로 관리되는 것.

## 4. 멀티 씬

- 씬이 여러 개면 씬끼리 변수를 공유해야 할 수 있음.
- **전역 노드를 하나 설정하고, 그 노드의 속성들을 전역 변수로 쓰는 방식**을 이용
  (= `GameState.gd`를 Autoload로 등록해서 `GameState.money`를 여러 씬이 공유).

## 5. 씬 전환

```gdscript
get_tree().change_scene_to_file("res://tutorials/scenes/Bank.tscn")
```

- `get_tree()`: 씬 관리자(`SceneTree` 객체) 반환.
- 씬 관련 함수는 씬 관리자만 호출할 수 있음 (`change_scene_to_file()`은
  `SceneTree`의 메서드이므로 `get_tree()`로 그 객체를 먼저 가져와야 호출 가능).

## 6. `$이름`

- `get_node("이름")`의 축약형으로, 이름이 '이름'인 노드를 찾아오라는 **검색 명령**임
  (변수 선언이 아님).
- 나중에 노드 참조가 많아지면 아래처럼 해두면 자동완성/타입 체크가 편함:
  ```gdscript
  @onready var status_label: Label = $StatusLabel
  ```

## 프로젝트 구조
```
tutorials/
├── scenes/
│   ├── Main.tscn   # 자산 표시, 돈넣기(슬롯머신), 은행가기 버튼
│   └── Bank.tscn   # 자산 표시, 대출받기, 돌아가기 버튼
└── scripts/
    ├── Main.gd
    ├── Bank.gd
    └── GameState.gd   # Autoload로 등록된 전역 자산 상태
```

## 실습

1. Godot 에디터 사용법. 아래 파일 시스템에서 Scene을 추가 후 Command + b로 디버거 실행

![godot 에디터 사용법](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/1.png)

2. 버튼을 누르면 자산을 획득하는 기능 구현

![버튼 클릭 기능 스크린샷](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/2.png)

![버튼 클릭 기능 동작](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/3.gif)

3. 씬을 추가하여 은행 씬을 추가했고, 거기에선 버튼을 누르면 돈을 받도록 설정. 기존 씬에선 버튼을 누를때 50%의 확률로 돈을 얻거나 잃도록 수정
    
![은행 씬 스크린샷](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/4.png)

![은행 씬 동작](https://cdn.jsdelivr.net/gh/importunate-dev/blog-images/study/gamemaker/5.gif)