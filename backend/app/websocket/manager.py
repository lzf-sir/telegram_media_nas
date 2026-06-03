"""
WebSocket Connection Manager
"""
from typing import Dict, Set
from fastapi import WebSocket
from fastapi.routing import APIRouter
import json
from loguru import logger

websocket_router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager for real-time updates"""

    def __init__(self):
        # Task-specific connections
        self.task_connections: Dict[int, Set[WebSocket]] = {}
        # Global notification connections
        self.notification_connections: Set[WebSocket] = set()

    async def connect_to_task(self, websocket: WebSocket, task_id: int):
        """Connect to a specific task's progress updates"""
        await websocket.accept()
        if task_id not in self.task_connections:
            self.task_connections[task_id] = set()
        self.task_connections[task_id].add(websocket)
        logger.info(f"WebSocket connected to task {task_id}")

    async def connect_to_notifications(self, websocket: WebSocket):
        """Connect to global notifications"""
        await websocket.accept()
        self.notification_connections.add(websocket)
        logger.info("WebSocket connected to notifications")

    def disconnect_from_task(self, websocket: WebSocket, task_id: int):
        """Disconnect from a specific task"""
        if task_id in self.task_connections:
            self.task_connections[task_id].discard(websocket)
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]
        logger.info(f"WebSocket disconnected from task {task_id}")

    def disconnect_from_notifications(self, websocket: WebSocket):
        """Disconnect from notifications"""
        self.notification_connections.discard(websocket)
        logger.info("WebSocket disconnected from notifications")

    async def send_task_update(self, task_id: int, message: dict):
        """Send update to all connections watching a task"""
        if task_id in self.task_connections:
            disconnected = set()
            for connection in self.task_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to connection: {e}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect_from_task(conn, task_id)

    async def broadcast_notification(self, message: dict):
        """Broadcast notification to all notification connections"""
        disconnected = set()
        for connection in self.notification_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send notification: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect_from_notifications(conn)

    async def send_task_progress(
        self,
        task_id: int,
        status: str,
        current: int,
        total: int,
        success: int = 0,
        failed: int = 0,
        downloaded_bytes: int = 0,
        total_bytes: int = 0,
        current_file: str = None,
        current_file_progress: float = 0.0,
        download_speed: float = 0.0,
        eta_seconds: int = 0,
    ):
        """发送任务进度更新（含速度和 ETA）"""
        message = {
            "type": "progress",
            "task_id": task_id,
            "status": status,
            "current": current,
            "total": total,
            "success": success,
            "failed": failed,
            "downloaded_bytes": downloaded_bytes,
            "total_bytes": total_bytes,
            "current_file": current_file,
            "current_file_progress": current_file_progress,
            "download_speed": round(download_speed, 2),
            "eta_seconds": eta_seconds,
            "progress": round(current / total * 100, 2) if total and total > 0 else 0,
        }
        await self.send_task_update(task_id, message)

    async def send_task_complete(self, task_id: int, success: bool, message: str = ""):
        """Send task completion notification"""
        msg = {
            "type": "complete",
            "task_id": task_id,
            "success": success,
            "message": message,
        }
        await self.send_task_update(task_id, msg)
        await self.broadcast_notification(msg)


# Global manager instance
manager = ConnectionManager()


@websocket_router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: int):
    """WebSocket endpoint for task progress updates"""
    await manager.connect_to_task(websocket, task_id)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # 响应心跳
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except Exception as e:
        logger.warning(f"Task WebSocket error: {e}")
    finally:
        manager.disconnect_from_task(websocket, task_id)


@websocket_router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    """WebSocket endpoint for global notifications"""
    await manager.connect_to_notifications(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except Exception as e:
        logger.warning(f"Notifications WebSocket error: {e}")
    finally:
        manager.disconnect_from_notifications(websocket)
