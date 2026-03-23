#!/bin/bash
# ================================================================
# 이미지 분리 스크립트
#
# 실행 방법:
#   1. GitHub에서 'blog-images' 저장소를 먼저 생성하세요
#      https://github.com/new → 이름: blog-images → Create
#
#   2. 이 스크립트를 실행하세요:
#      bash scripts/setup-blog-images.sh
#
# 이 스크립트는:
#   - 현재 저장소의 img/ 폴더를 ../blog-images/로 복사
#   - blog-images 저장소를 초기화하고 push
# ================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
IMG_SRC="$REPO_ROOT/../junsoopooh.github.io.bak/img"  # 원본 Jekyll 저장소의 img 폴더
BLOG_IMAGES_DIR="$REPO_ROOT/../blog-images"
GITHUB_USER="importunate-dev"

echo "=== 이미지 분리 스크립트 ==="
echo ""

# 1. blog-images 디렉토리 생성
if [ -d "$BLOG_IMAGES_DIR" ]; then
    echo "⚠️  blog-images 디렉토리가 이미 존재합니다. 덮어씁니다."
    rm -rf "$BLOG_IMAGES_DIR"
fi

mkdir -p "$BLOG_IMAGES_DIR"

# 2. 이미지 복사 (img/ 하위 구조 유지, img/ 자체는 제거)
echo "📁 이미지 복사 중..."
if [ -d "$IMG_SRC" ]; then
    cp -r "$IMG_SRC"/* "$BLOG_IMAGES_DIR/"
    echo "✅ $(find "$BLOG_IMAGES_DIR" -type f | wc -l)개 파일 복사 완료"
else
    echo "❌ 원본 이미지 폴더를 찾을 수 없습니다: $IMG_SRC"
    echo "   수동으로 img/ 폴더의 내용을 $BLOG_IMAGES_DIR/로 복사해주세요."
    exit 1
fi

# 3. Git 초기화 및 Push
echo ""
echo "🔧 Git 초기화 중..."
cd "$BLOG_IMAGES_DIR"
git init
git add .
git commit -m "Initial commit: migrate blog images from main repo"

echo ""
echo "📤 GitHub에 push 중..."
git remote add origin "https://github.com/$GITHUB_USER/blog-images.git"
git branch -M main
git push -u origin main

echo ""
echo "=== 완료! ==="
echo ""
echo "이미지 URL 형식:"
echo "  https://cdn.jsdelivr.net/gh/$GITHUB_USER/blog-images/[경로]"
echo ""
echo "예시:"
echo "  https://cdn.jsdelivr.net/gh/$GITHUB_USER/blog-images/study/algo1.webp"
