#!/bin/bash
set -e

SERVICE_URL=${SERVICE_URL:-"http://localhost:8080"}
ENV_NAME=${ENV_NAME:-"beta"}

echo "=== Smoke Tests for $ENV_NAME ==="

# Test 1: Health check
echo ">> Testing /actuator/health..."
HEALTH=$(curl -sf "$SERVICE_URL/actuator/health")
STATUS=$(echo "$HEALTH" | jq -r '.status')
if [ "$STATUS" != "UP" ]; then
  echo "FAIL: Health status is $STATUS"
  exit 1
fi
echo "PASS: Health status is UP"

# Test 2: Info endpoint
echo ">> Testing /api/info..."
INFO=$(curl -sf "$SERVICE_URL/api/info")
ENV_RESPONSE=$(echo "$INFO" | jq -r '.environment')
if [ "$ENV_RESPONSE" != "$ENV_NAME" ]; then
  echo "FAIL: Expected environment=$ENV_NAME, got $ENV_RESPONSE"
  exit 1
fi
echo "PASS: Environment is $ENV_NAME"

# Test 3: Check pod count (requires kubectl access)
echo ">> Checking pod count..."
READY_PODS=$(kubectl get pods -n atlas -l app=atlas-platform --field-selector=status.phase=Running
--no-headers 2>/dev/null | wc -l | tr -d ' ')
MIN_REPLICAS=2
if [ "$READY_PODS" -lt "$MIN_REPLICAS" ]; then
  echo "FAIL: Only $READY_PODS pods running, expected >= $MIN_REPLICAS"
  exit 1
fi
echo "PASS: $READY_PODS pods running"

# Test 4: No CrashLoopBackOff
echo ">> Checking for CrashLoopBackOff..."
CRASH_PODS=$(kubectl get pods -n atlas -l app=atlas-platform --no-headers 2>/dev/null | grep -c
"CrashLoopBackOff" || true)
if [ "$CRASH_PODS" -gt 0 ]; then
  echo "FAIL: $CRASH_PODS pods in CrashLoopBackOff"
  exit 1
fi
echo "PASS: No CrashLoopBackOff pods"

echo ""
echo "=== All smoke tests passed! ==="