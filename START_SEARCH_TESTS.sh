#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  CLM Backend - Search System Test Suite Launcher${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if server is running
echo -e "${YELLOW}ℹ Checking if Django server is running on port 11000...${NC}"
if timeout 2 bash -c "echo >/dev/tcp/localhost/11000" 2>/dev/null; then
    echo -e "${GREEN}✓ Server is already running${NC}"
else
    echo -e "${YELLOW}ℹ Server not running. Starting Django development server...${NC}"
    echo -e "${YELLOW}ℹ (This will run in the background)${NC}"
    
    # Start Django server in background
    cd "$SCRIPT_DIR"
    python manage.py runserver 11000 > /dev/null 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}ℹ Waiting for server to start...${NC}"
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt 30 ]; do
        if timeout 2 bash -c "echo >/dev/tcp/localhost/11000" 2>/dev/null; then
            echo -e "${GREEN}✓ Server started successfully (PID: $SERVER_PID)${NC}"
            echo ""
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 1
    done
    
    if [ $RETRY_COUNT -ge 30 ]; then
        echo -e "${YELLOW}⚠ Server startup timeout${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Running Search System Tests${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Run the test script
cd "$SCRIPT_DIR/tests/Week_3"
bash Search.sh

# Capture the exit code
TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests completed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Tests completed with exit code: $TEST_EXIT_CODE${NC}"
fi
echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📝 Documentation:${NC}"
echo "  • Complete flow explanation: SEARCH_FLOW_COMPLETE_EXPLANATION.md"
echo "  • Quick guide: SEARCH_SYSTEM_QUICK_GUIDE.md"
echo "  • Visual flows: SEARCH_SYSTEM_VISUAL_FLOWS.md"
echo "  • Full endpoints: SEARCH_ENDPOINTS_COMPLETE_FLOW.md"
echo ""
