"""Puente entre el EventBus y los WebSocket de los clientes (patrón Observer).

Las rutas de hardware publican eventos sin saber quién está conectado; este hub se suscribe a
esos eventos y le entrega a cada jugador SOLO los mensajes de su panel.

Detalle técnico: el EventBus es síncrono y las rutas corren en hilos del servidor, mientras que
cada WebSocket vive en el event loop de asyncio. Por eso el hub no envía directamente: deja el
mensaje en la cola de cada conexión con call_soon_threadsafe y la conexión lo envía desde su loop.
"""
import asyncio
import threading
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

from app.shared.events import EventBus, HardwareButtonEvent, PanelLinked, PanelUnlinked
from app.shared.logger import get_logger

logger = get_logger()

_Subscriber = tuple[asyncio.AbstractEventLoop, asyncio.Queue]


class HardwareHub:
    def __init__(self, bus: EventBus) -> None:
        self._subscribers: dict[str, list[_Subscriber]] = defaultdict(list)
        self._lock = threading.Lock()
        bus.subscribe(HardwareButtonEvent, self._on_button)
        bus.subscribe(PanelLinked, self._on_linked)
        bus.subscribe(PanelUnlinked, self._on_unlinked)

    # ---- Eventos del bus -> mensajes del protocolo (PROTOCOL.md, "WebSocket") ----
    def _on_button(self, e: HardwareButtonEvent) -> None:
        self._deliver(
            e.player_id,
            {"type": "button", "deviceId": e.device_id, "button": e.button, "event": e.event, "timestamp": e.timestamp},
        )

    def _on_linked(self, e: PanelLinked) -> None:
        self._deliver(e.player_id, {"type": "device.linked", "deviceId": e.device_id})

    def _on_unlinked(self, e: PanelUnlinked) -> None:
        self._deliver(e.player_id, {"type": "device.unlinked", "deviceId": e.device_id})

    def _deliver(self, player_id: str, message: dict) -> None:
        with self._lock:
            targets = list(self._subscribers.get(player_id, ()))
        for loop, queue in targets:
            try:
                loop.call_soon_threadsafe(queue.put_nowait, message)
            except RuntimeError:  # el loop de esa conexión ya se cerró
                pass

    def connection_count(self, player_id: str) -> int:
        with self._lock:
            return len(self._subscribers.get(player_id, ()))

    # ---- Conexiones ---------------------------------------------------------
    async def serve(self, websocket: WebSocket, player_id: str) -> None:
        """Mantiene la conexión abierta y le envía los mensajes del jugador hasta que se cierre."""
        subscriber: _Subscriber = (asyncio.get_running_loop(), asyncio.Queue())
        with self._lock:
            self._subscribers[player_id].append(subscriber)
        logger.info("Cliente conectado al WebSocket de hardware", extra={"extra_data": {"player": player_id}})

        disconnected = asyncio.create_task(self._wait_for_disconnect(websocket))
        try:
            while True:
                next_message = asyncio.create_task(subscriber[1].get())
                done, _ = await asyncio.wait({next_message, disconnected}, return_when=asyncio.FIRST_COMPLETED)
                if disconnected in done:
                    next_message.cancel()
                    return
                await websocket.send_json(next_message.result())
        except (WebSocketDisconnect, RuntimeError):
            return
        finally:
            disconnected.cancel()
            with self._lock:
                remaining = self._subscribers.get(player_id, [])
                if subscriber in remaining:
                    remaining.remove(subscriber)
                if not remaining:
                    self._subscribers.pop(player_id, None)
            logger.info("Cliente desconectado del WebSocket de hardware", extra={"extra_data": {"player": player_id}})

    @staticmethod
    async def _wait_for_disconnect(websocket: WebSocket) -> None:
        # El cliente no necesita enviar nada; cualquier mensaje suyo se ignora.
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                return
