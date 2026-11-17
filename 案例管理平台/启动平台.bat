@echo off
chcp 65001 >nul
title 数据分析案例管理平台
echo 正在启动后端 (FastAPI :8000)...
start "后端-FastAPI" /d backend cmd /k "python -m uvicorn main:app --port 8000"
echo 正在启动前端 (Vite :5173)...
start "前端-Vite" /d frontend cmd /k "npm run dev"
echo 启动完成，浏览器访问 http://localhost:5173
timeout /t 3 >nul
start http://localhost:5173
