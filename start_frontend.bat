@echo off
echo Starting Mini Chatbot Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
echo Starting React app...
call npm start
pause
