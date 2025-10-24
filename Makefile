.PHONY: help install serve start stop restart status clean logs build watch dev

help:
	@echo "Jekyll 블로그 관리 명령어:"
	@echo "  make install  - 의존성 패키지 설치"
	@echo "  make serve    - Jekyll 서버 시작 (포그라운드)"
	@echo "  make start    - Jekyll 서버 시작 (백그라운드)"
	@echo "  make stop     - Jekyll 서버 종료"
	@echo "  make restart  - Jekyll 서버 재시작"
	@echo "  make status   - Jekyll 서버 상태 확인"
	@echo "  make logs     - 서버 로그 확인"
	@echo "  make clean    - 생성된 사이트 및 로그 삭제"
	@echo ""
	@echo "LESS 컴파일 명령어:"
	@echo "  make build    - LESS를 CSS로 컴파일 (배포 전 실행)"
	@echo "  make watch    - LESS 파일 변경 감시 및 자동 컴파일"
	@echo "  make dev      - Jekyll + LESS 자동 컴파일 동시 실행"

install:
	@echo "📦 의존성 패키지 설치 중..."
	bundle install --path vendor/bundle
	@echo "📦 Node.js 패키지 설치 중..."
	npm install

serve:
	@echo "🚀 Jekyll 서버 시작 중... (http://localhost:4000)"
	bundle exec jekyll serve

start:
	@echo "🚀 Jekyll 서버를 백그라운드로 시작합니다..."
	@pkill -f jekyll 2>/dev/null || true
	@nohup bundle exec jekyll serve > jekyll.log 2>&1 &
	@sleep 2
	@echo "✅ 서버가 시작되었습니다: http://localhost:4000"
	@echo "📝 로그 확인: make logs"

stop:
	@echo "🛑 Jekyll 서버를 종료합니다..."
	@pkill -f jekyll && echo "✅ 서버가 종료되었습니다." || echo "⚠️  실행 중인 서버가 없습니다."

restart:
	@echo "🔄 Jekyll 서버를 재시작합니다..."
	@$(MAKE) stop
	@sleep 1
	@$(MAKE) start

status:
	@echo "📊 Jekyll 서버 상태:"
	@lsof -ti:4000 > /dev/null && echo "✅ 서버 실행 중 (PID: $$(lsof -ti:4000))" || echo "⚠️  서버가 실행 중이 아닙니다."
	@lsof -ti:4000 > /dev/null && echo "🌐 http://localhost:4000" || true

logs:
	@if [ -f jekyll.log ]; then \
		tail -f jekyll.log; \
	else \
		echo "⚠️  jekyll.log 파일이 없습니다."; \
	fi

clean:
	@echo "🧹 생성된 파일들을 삭제합니다..."
	@rm -rf _site .jekyll-cache .jekyll-metadata jekyll.log
	@echo "✅ 삭제 완료!"

build:
	@echo "🔨 LESS를 CSS로 컴파일 중..."
	@if [ ! -d "node_modules" ]; then \
		echo "⚠️  node_modules가 없습니다. npm install을 실행합니다..."; \
		npm install; \
	fi
	@npx grunt less
	@echo "✅ CSS 컴파일 완료!"
	@echo "📝 생성된 파일: css/hux-blog.css, css/hux-blog.min.css"

watch:
	@echo "👀 LESS 파일 변경 감시 중... (Ctrl+C로 종료)"
	@if [ ! -d "node_modules" ]; then \
		echo "⚠️  node_modules가 없습니다. npm install을 실행합니다..."; \
		npm install; \
	fi
	@npx grunt watch

dev:
	@echo "🚀 개발 환경 시작 중..."
	@if [ ! -d "node_modules" ]; then \
		echo "⚠️  node_modules가 없습니다. npm install을 실행합니다..."; \
		npm install; \
	fi
	@echo "✨ Jekyll 서버 + LESS 자동 컴파일 실행"
	@echo "📍 http://localhost:4000"
	@echo "👀 LESS 파일이 자동으로 감시됩니다"
	@echo "⚠️  종료: Ctrl+C"
	@npx grunt watch & bundle exec jekyll serve

