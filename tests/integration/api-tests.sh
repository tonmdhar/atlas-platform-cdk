#!/bin/bash
set -e

SERVICE_URL=${SERVICE_URL:-"http://localhost:8080"}
ENV_NAME=${ENV_NAME:-"gamma"}
PASS=0
FAIL=0

echo "=== Integration Tests for $ENV_NAME ==="

# Helper function
assert_status() {
  local test_name=$1
  local expected=$2
  local actual=$3
  if [ "$actual" -eq "$expected" ]; then
    echo "PASS: $test_name (HTTP $actual)"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $test_name - expected $expected, got $actual"
    FAIL=$((FAIL + 1))
  fi
}

# --- CRUD Tests ---

# Test 1: Create item
echo ""
echo ">> POST /api/items (create)"
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$SERVICE_URL/api/items" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "Integration test item"}')
CREATE_STATUS=$(echo "$CREATE_RESPONSE" | tail -1)
CREATE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')
assert_status "Create item" 201 "$CREATE_STATUS"

ITEM_ID=$(echo "$CREATE_BODY" | jq -r '.id')
echo "   Created item ID: $ITEM_ID"

# Test 2: Get item by ID
echo ""
echo ">> GET /api/items/$ITEM_ID"
GET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/items/$ITEM_ID")
assert_status "Get item" 200 "$GET_STATUS"

# Test 3: List all items
echo ""
echo ">> GET /api/items (list)"
LIST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/items")
assert_status "List items" 200 "$LIST_STATUS"

# Test 4: Update item
echo ""
echo ">> PUT /api/items/$ITEM_ID (update)"
UPDATE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$SERVICE_URL/api/items/$ITEM_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "description": "Updated description"}')
assert_status "Update item" 200 "$UPDATE_STATUS"

# Test 5: Delete item
echo ""
echo ">> DELETE /api/items/$ITEM_ID"
DELETE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$SERVICE_URL/api/items/$ITEM_ID")
assert_status "Delete item" 204 "$DELETE_STATUS"

# Test 6: Get deleted item (should 404)
echo ""
echo ">> GET /api/items/$ITEM_ID (expect 404)"
GET_DELETED_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/items/$ITEM_ID")
assert_status "Get deleted item returns 404" 404 "$GET_DELETED_STATUS"

# --- Error Handling Tests ---

# Test 7: Get non-existent item
echo ""
echo ">> GET /api/items/nonexistent-id (expect 404)"
NOT_FOUND_STATUS=$(curl -s -o /dev/null -w "%{http_code}"
"$SERVICE_URL/api/items/nonexistent-id-12345")
assert_status "Non-existent item returns 404" 404 "$NOT_FOUND_STATUS"

# --- Load Test ---
echo ""
echo ">> Basic load test (20 concurrent requests)..."
LOAD_PASS=0
for i in $(seq 1 20); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/actuator/health" &)
done
wait

# Simple sequential load test with timing
START_TIME=$(date +%s%N)
for i in $(seq 1 50); do
  curl -s -o /dev/null "$SERVICE_URL/api/items"
done
END_TIME=$(date +%s%N)
DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))
AVG_MS=$((DURATION_MS / 50))
echo "   50 requests completed in ${DURATION_MS}ms (avg: ${AVG_MS}ms/request)"

if [ "$AVG_MS" -lt 500 ]; then
  echo "PASS: Average response time ${AVG_MS}ms < 500ms threshold"
  PASS=$((PASS + 1))
else
  echo "FAIL: Average response time ${AVG_MS}ms >= 500ms threshold"
  FAIL=$((FAIL + 1))
fi

# --- Summary ---
echo ""
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
