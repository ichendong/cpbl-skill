#!/bin/bash
# Autonomous Coder - CPBL Skill 版
# 用法: ./run.sh [max_iterations]

set -e

MAX_ITERATIONS=${1:-10}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(dirname "$SCRIPT_DIR")"

TASKS_FILE="$SCRIPT_DIR/tasks.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.md"
PROMPT_FILE="$SCRIPT_DIR/prompt.md"

echo "🦾 Autonomous Coder 啟動"
echo "專案路徑: $PROJECT_PATH"
echo "任務清單: $TASKS_FILE"
echo "最大迭代: $MAX_ITERATIONS"
echo ""

if [ ! -f "$TASKS_FILE" ]; then
    echo "❌ 找不到 tasks.json"
    exit 1
fi

for i in $(seq 1 $MAX_ITERATIONS); do
    echo "═══════════════════════════════════════"
    echo "迭代 $i / $MAX_ITERATIONS"
    echo "═══════════════════════════════════════"
    
    PENDING_COUNT=$(jq '[.tasks[] | select(.status == "pending")] | length' "$TASKS_FILE" 2>/dev/null || echo "0")
    BLOCKED_COUNT=$(jq '[.tasks[] | select(.status == "blocked")] | length' "$TASKS_FILE" 2>/dev/null || echo "0")
    TOTAL_COUNT=$(jq '.tasks | length' "$TASKS_FILE" 2>/dev/null || echo "0")
    
    if [ "$PENDING_COUNT" -eq 0 ]; then
        echo ""
        echo "✅ 所有任務完成！"
        exit 0
    fi
    
    if [ "$BLOCKED_COUNT" -ge "$TOTAL_COUNT" ]; then
        echo ""
        echo "⚠️ 所有任務都被卡住了！"
        exit 2
    fi
    
    # 取得下一個待處理任務的資訊
    NEXT_TASK=$(jq -r '[.tasks[] | select(.status == "pending")] | sort_by(.priority) | .[0]' "$TASKS_FILE")
    TASK_ID=$(echo "$NEXT_TASK" | jq -r '.id')
    TASK_TITLE=$(echo "$NEXT_TASK" | jq -r '.title')
    
    echo "📝 執行任務: $TASK_ID - $TASK_TITLE"
    echo "   待處理: $PENDING_COUNT, 卡住: $BLOCKED_COUNT"
    echo ""
    
    # 讀取 prompt 並替換變數
    PROMPT=$(cat "$PROMPT_FILE" | \
        sed "s|{{TASKS_FILE}}|$TASKS_FILE|g" | \
        sed "s|{{PROGRESS_FILE}}|$PROGRESS_FILE|g" | \
        sed "s|{{PROJECT_PATH}}|$PROJECT_PATH|g")
    
    # 用 openclaw 執行
    openclaw spawn --message "$PROMPT" --cwd "$PROJECT_PATH" --model glm-5-turbo 2>&1 || true
    
    # 讀取更新後的任務狀態
    sleep 2
done

echo ""
echo "達到最大迭代次數 $MAX_ITERATIONS"
exit 1
