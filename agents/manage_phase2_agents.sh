#!/bin/bash

# PulseProof Phase 2 Multi-Agent System Management Script
# Real agent communication using ctx.send and ctx.send_and_receive

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Agent configurations (using simple arrays for compatibility)
AGENT_NAMES=("orchestrator" "event_analyzer" "risk_assessor")
AGENT_PORTS=("8001" "8002" "8003")
AGENT_SCRIPTS=("master_orchestrator/phase2_orchestrator.py" "event_analyzer/phase2_event_analyzer.py" "risk_assessor/phase2_risk_assessor.py")
AGENT_LOGS=("Phase2Orchestrator" "Phase2EventAnalyzer" "Phase2RiskAssessor")

get_agent_config() {
    local agent_name=$1
    local index=0
    
    for name in "${AGENT_NAMES[@]}"; do
        if [ "$name" = "$agent_name" ]; then
            echo "${AGENT_PORTS[$index]}:${AGENT_SCRIPTS[$index]}:${AGENT_LOGS[$index]}"
            return 0
        fi
        index=$((index + 1))
    done
    return 1
}

show_usage() {
    echo "🤖 PulseProof Phase 2 Multi-Agent System Manager"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all Phase 2 agents with real communication"
    echo "  stop        Stop all Phase 2 agents"
    echo "  restart     Restart all Phase 2 agents"
    echo "  status      Show agent status"
    echo "  health      Check agent health"
    echo "  stats       Show agent statistics"
    echo "  test        Run Phase 2 comprehensive tests"
    echo "  logs        Show agent logs"
    echo "  clean       Clean up logs and PIDs"
    echo ""
    echo "Individual agent control:"
    echo "  start-<agent>     Start specific agent (orchestrator, event_analyzer, risk_assessor)"
    echo "  stop-<agent>      Stop specific agent"
    echo "  restart-<agent>   Restart specific agent"
    echo "  status-<agent>    Show specific agent status"
    echo ""
    echo "Phase 2 Features:"
    echo "  ✅ Real agent communication using ctx.send and ctx.send_and_receive"
    echo "  ✅ Synchronous and asynchronous communication patterns"
    echo "  ✅ Enhanced error handling and acknowledgments"
    echo "  ✅ Agent health monitoring with real communication"
}

check_agent_status() {
    local agent_name=$1
    local port=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $agent_name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}❌ $agent_name is not running on port $port${NC}"
        return 1
    fi
}

start_agent() {
    local agent_name=$1
    local port=$2
    local script=$3
    local log_name=$4
    
    echo -e "${BLUE}🚀 Starting Phase 2 $agent_name...${NC}"
    
    # Check if already running
    if check_agent_status "$agent_name" "$port" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  $agent_name is already running${NC}"
        return 0
    fi
    
    # Kill any existing process on the port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
    
    # Start agent
    cd "$(dirname "$0")"
    source venv/bin/activate
    
    if [ -f "$script" ]; then
        nohup python "$script" > "logs/${log_name}.log" 2>&1 &
        local pid=$!
        echo "$pid" > "logs/${log_name}.pid"
        
        # Wait and check if started successfully
        sleep 3
        if check_agent_status "$agent_name" "$port" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Phase 2 $agent_name started successfully (PID: $pid)${NC}"
            return 0
        else
            echo -e "${RED}❌ Phase 2 $agent_name failed to start${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Agent script not found: $script${NC}"
        return 1
    fi
}

stop_agent() {
    local agent_name=$1
    local port=$2
    local log_name=$3
    
    echo -e "${YELLOW}🛑 Stopping Phase 2 $agent_name...${NC}"
    
    # Try to stop gracefully first
    if [ -f "logs/${log_name}.pid" ]; then
        local pid=$(cat "logs/${log_name}.pid")
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null || true
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null || true
            fi
        fi
        rm -f "logs/${log_name}.pid"
    fi
    
    # Force kill any process on the port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    
    sleep 2
    if check_agent_status "$agent_name" "$port" >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to stop $agent_name${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Phase 2 $agent_name stopped successfully${NC}"
        return 0
    fi
}

start_all_agents() {
    echo -e "${BLUE}🚀 Starting all Phase 2 agents with real communication...${NC}"
    echo "=================================================="
    
    # Create logs directory
    mkdir -p logs
    
    local success_count=0
    local total_count=0
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            total_count=$((total_count + 1))
            
            if start_agent "$agent_name" "$port" "$script" "$log_name"; then
                success_count=$((success_count + 1))
            fi
            echo ""
        fi
    done
    
    echo "=================================================="
    echo -e "${GREEN}📊 Started $success_count/$total_count Phase 2 agents successfully${NC}"
    
    if [ $success_count -eq $total_count ]; then
        echo -e "${GREEN}🎉 All Phase 2 agents are running with real communication!${NC}"
        echo ""
        echo -e "${YELLOW}🔍 Quick Health Check:${NC}"
        echo "   curl http://localhost:8001/health"
        echo "   curl http://localhost:8002/health"
        echo "   curl http://localhost:8003/health"
        echo ""
        echo -e "${YELLOW}🧪 Run Phase 2 Tests:${NC}"
        echo "   python test_phase2_system.py"
        echo ""
        echo -e "${YELLOW}📡 Real Agent Communication Features:${NC}"
        echo "   ✅ ctx.send for asynchronous communication"
        echo "   ✅ ctx.send_and_receive for synchronous communication"
        echo "   ✅ Enhanced error handling and acknowledgments"
        echo "   ✅ Agent health monitoring with real communication"
    else
        echo -e "${RED}⚠️  Some Phase 2 agents failed to start${NC}"
    fi
}

stop_all_agents() {
    echo -e "${YELLOW}🛑 Stopping all Phase 2 agents...${NC}"
    echo "=================================================="
    
    local success_count=0
    local total_count=0
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            total_count=$((total_count + 1))
            
            if stop_agent "$agent_name" "$port" "$log_name"; then
                success_count=$((success_count + 1))
            fi
            echo ""
        fi
    done
    
    echo "=================================================="
    echo -e "${GREEN}📊 Stopped $success_count/$total_count Phase 2 agents successfully${NC}"
}

show_status() {
    echo -e "${BLUE}📊 Phase 2 Multi-Agent System Status${NC}"
    echo "=================================================="
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            check_agent_status "$agent_name" "$port"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}🔍 Health Check URLs:${NC}"
    echo "   Orchestrator:    http://localhost:8001/health"
    echo "   Event Analyzer:  http://localhost:8002/health"
    echo "   Risk Assessor:   http://localhost:8003/health"
    echo ""
    echo -e "${YELLOW}📡 Real Communication Features:${NC}"
    echo "   ✅ ctx.send for asynchronous communication"
    echo "   ✅ ctx.send_and_receive for synchronous communication"
    echo "   ✅ Enhanced error handling and acknowledgments"
    echo "   ✅ Agent health monitoring with real communication"
}

check_health() {
    echo -e "${BLUE}🏥 Checking Phase 2 agent health...${NC}"
    echo "=================================================="
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            echo -e "${YELLOW}🔍 Checking Phase 2 $agent_name...${NC}"
            
            if check_agent_status "$agent_name" "$port" >/dev/null 2>&1; then
                # Try to get health endpoint
                local health_url="http://localhost:$port/health"
                if curl -s "$health_url" >/dev/null 2>&1; then
                    echo -e "${GREEN}✅ Phase 2 $agent_name is healthy${NC}"
                    curl -s "$health_url" | python -m json.tool 2>/dev/null || echo "   (Health endpoint responded but not JSON)"
                else
                    echo -e "${YELLOW}⚠️  Phase 2 $agent_name is running but health endpoint not responding${NC}"
                fi
            else
                echo -e "${RED}❌ Phase 2 $agent_name is not running${NC}"
            fi
            echo ""
        fi
    done
}

show_stats() {
    echo -e "${BLUE}📊 Phase 2 Agent Statistics${NC}"
    echo "=================================================="
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            echo -e "${YELLOW}📈 Phase 2 $agent_name Statistics:${NC}"
            
            local stats_url="http://localhost:$port/stats"
            if curl -s "$stats_url" >/dev/null 2>&1; then
                curl -s "$stats_url" | python -m json.tool 2>/dev/null || echo "   (Stats endpoint responded but not JSON)"
            else
                echo -e "${RED}❌ Stats endpoint not responding${NC}"
            fi
            echo ""
        fi
    done
}

run_tests() {
    echo -e "${BLUE}🧪 Running Phase 2 system tests...${NC}"
    echo "=================================================="
    
    if [ -f "test_phase2_system.py" ]; then
        source venv/bin/activate
        python test_phase2_system.py
    else
        echo -e "${RED}❌ Phase 2 test script not found: test_phase2_system.py${NC}"
    fi
}

show_logs() {
    echo -e "${BLUE}📝 Phase 2 Agent Logs${NC}"
    echo "=================================================="
    echo "Available log files:"
    echo ""
    
    for agent_name in "${AGENT_NAMES[@]}"; do
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            if [ -f "logs/${log_name}.log" ]; then
                echo -e "${YELLOW}📄 Phase 2 $agent_name logs (logs/${log_name}.log):${NC}"
                echo "   tail -f logs/${log_name}.log"
                echo "   head -20 logs/${log_name}.log"
            else
                echo -e "${RED}❌ No logs found for Phase 2 $agent_name${NC}"
            fi
            echo ""
        fi
    done
}

clean_up() {
    echo -e "${YELLOW}🧹 Cleaning up Phase 2 logs and PIDs...${NC}"
    
    # Remove PID files
    rm -f logs/*.pid
    
    # Optionally clean logs (ask user)
    echo "Do you want to clean log files? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -f logs/*.log
        echo -e "${GREEN}✅ Log files cleaned${NC}"
    else
        echo -e "${YELLOW}⚠️  Log files preserved${NC}"
    fi
    
    echo -e "${GREEN}✅ Phase 2 cleanup completed${NC}"
}

# Main command handling
case "$1" in
    start)
        start_all_agents
        ;;
    stop)
        stop_all_agents
        ;;
    restart)
        stop_all_agents
        sleep 2
        start_all_agents
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    stats)
        show_stats
        ;;
    test)
        run_tests
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_up
        ;;
    start-*)
        agent_name="${1#start-}"
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            start_agent "$agent_name" "$port" "$script" "$log_name"
        else
            echo -e "${RED}❌ Unknown agent: $agent_name${NC}"
        fi
        ;;
    stop-*)
        agent_name="${1#stop-}"
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            stop_agent "$agent_name" "$port" "$log_name"
        else
            echo -e "${RED}❌ Unknown agent: $agent_name${NC}"
        fi
        ;;
    restart-*)
        agent_name="${1#restart-}"
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            stop_agent "$agent_name" "$port" "$log_name"
            sleep 2
            start_agent "$agent_name" "$port" "$script" "$log_name"
        else
            echo -e "${RED}❌ Unknown agent: $agent_name${NC}"
        fi
        ;;
    status-*)
        agent_name="${1#status-}"
        config=$(get_agent_config "$agent_name")
        if [ $? -eq 0 ]; then
            IFS=':' read -r port script log_name <<< "$config"
            check_agent_status "$agent_name" "$port"
        else
            echo -e "${RED}❌ Unknown agent: $agent_name${NC}"
        fi
        ;;
    *)
        show_usage
        ;;
esac
