#!/bin/bash

# KFAligner Web Application Restart Script
# This script stops and starts the Gunicorn server for the KFAligner web application

set -e

# Configuration
WEBAPP_DIR="/var/www/html/kfaligner/webapp"
PID_FILE="$WEBAPP_DIR/server.pid"
LOG_DIR="$WEBAPP_DIR"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
BIND_ADDRESS="127.0.0.1:5011"
WORKERS=2
TIMEOUT=300

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== KFAligner Web Application Restart Script ===${NC}"

# Function to stop the server
stop_server() {
    # First, find all gunicorn processes for this app
    MASTER_PID=$(pgrep -f "gunicorn: master \[webapp.app:app\]" | head -1)
    
    if [ ! -z "$MASTER_PID" ]; then
        echo -e "${YELLOW}Stopping Gunicorn master (PID: $MASTER_PID)...${NC}"
        kill -TERM "$MASTER_PID"
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! ps -p "$MASTER_PID" > /dev/null 2>&1; then
                echo -e "${GREEN}Server stopped successfully${NC}"
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
        done
        # Force kill if still running
        if ps -p "$MASTER_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Forcing shutdown...${NC}"
            kill -9 "$MASTER_PID"
            rm -f "$PID_FILE"
        fi
    elif [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping Gunicorn (PID from file: $PID)...${NC}"
            kill -TERM "$PID"
            sleep 2
            if ps -p "$PID" > /dev/null 2>&1; then
                kill -9 "$PID"
            fi
        fi
        echo -e "${YELLOW}Cleaning up PID file...${NC}"
        rm -f "$PID_FILE"
    else
        echo -e "${GREEN}No server running${NC}"
    fi
}

# Function to start the server
start_server() {
    cd "$WEBAPP_DIR"
    
    # Activate virtual environment if exists
    if [ -d "/home/tyoon/anaconda3/envs/aligner" ]; then
        echo -e "${YELLOW}Activating conda environment 'aligner'...${NC}"
        source /home/tyoon/anaconda3/etc/profile.d/conda.sh
        conda activate aligner
    fi
    
    echo -e "${YELLOW}Starting Gunicorn on $BIND_ADDRESS with $WORKERS workers...${NC}"
    
    gunicorn \
        --bind "$BIND_ADDRESS" \
        --workers "$WORKERS" \
        --timeout "$TIMEOUT" \
        --access-logfile "$ACCESS_LOG" \
        --error-logfile "$ERROR_LOG" \
        --pid "$PID_FILE" \
        --daemon \
        webapp.app:app
    
    sleep 2
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Server started successfully (PID: $PID)${NC}"
            echo -e "${GREEN}Application available at: http://localhost:5010${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}Failed to start server${NC}"
    return 1
}

# Function to reload the server (graceful restart)
reload_server() {
    MASTER_PID=$(pgrep -f "gunicorn: master \[webapp.app:app\]" | head -1)
    
    if [ ! -z "$MASTER_PID" ]; then
        echo -e "${YELLOW}Reloading Gunicorn (Master PID: $MASTER_PID)...${NC}"
        kill -HUP "$MASTER_PID"
        sleep 2
        echo -e "${GREEN}Server reloaded successfully${NC}"
        return 0
    elif [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Reloading Gunicorn (PID: $PID)...${NC}"
            kill -HUP "$PID"
            sleep 2
            echo -e "${GREEN}Server reloaded successfully${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}Server not running. Starting fresh...${NC}"
    start_server
}

# Function to show status
show_status() {
    MASTER_PID=$(pgrep -f "gunicorn: master \[webapp.app:app\]" | head -1)
    
    if [ ! -z "$MASTER_PID" ]; then
        echo -e "${GREEN}Server is running (Master PID: $MASTER_PID)${NC}"
        ps aux | grep "gunicorn.*webapp.app:app" | grep -v grep
        return 0
    elif [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Server is running (PID from file: $PID)${NC}"
            ps aux | grep "$PID" | grep -v grep
            return 0
        else
            echo -e "${RED}PID file exists but process not running${NC}"
            return 1
        fi
    else
        echo -e "${RED}Server is not running${NC}"
        return 1
    fi
}

# Main script logic
case "${1:-restart}" in
    start)
        echo -e "${YELLOW}Starting server...${NC}"
        stop_server
        start_server
        ;;
    stop)
        echo -e "${YELLOW}Stopping server...${NC}"
        stop_server
        ;;
    restart)
        echo -e "${YELLOW}Restarting server...${NC}"
        stop_server
        start_server
        ;;
    reload)
        echo -e "${YELLOW}Reloading server configuration...${NC}"
        reload_server
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status}"
        echo ""
        echo "  start   - Stop any running server and start fresh"
        echo "  stop    - Stop the server"
        echo "  restart - Stop and start the server (full restart)"
        echo "  reload  - Gracefully reload the server (HUP signal)"
        echo "  status  - Show server status"
        echo ""
        echo "Default action: restart"
        exit 1
        ;;
esac

exit 0
