import socket
import threading
import json
from typing import Dict, Tuple


class RelayServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self.rooms: Dict[str, Dict[str, socket.socket]] = {}
        self.lock = threading.Lock()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(100)
        print(f"Relay server listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = server_sock.accept()
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
        finally:
            server_sock.close()

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]):
        room_id = None
        role = None
        try:
            while True:
                length_data = self._recv_all(conn, 4)
                if not length_data:
                    break
                length = int.from_bytes(length_data, "big")
                payload = self._recv_all(conn, length)
                if not payload:
                    break

                raw = length_data + payload

                try:
                    message = json.loads(payload.decode("utf-8"))
                except Exception:
                    message = None

                if isinstance(message, dict) and message.get("type") == "relay_register":
                    room_id = str(message.get("room_id") or "default")
                    role = str(message.get("role") or "guest")
                    self._register_client(room_id, role, conn)
                    print(f"Client {addr} registered as {role} in room {room_id}")
                    continue

                target = self._get_target(room_id, role)
                if target:
                    try:
                        target.sendall(raw)
                    except OSError:
                        pass
        finally:
            if room_id and role:
                with self.lock:
                    if room_id in self.rooms and self.rooms[room_id].get(role) is conn:
                        self.rooms[room_id].pop(role, None)
                        if not self.rooms[room_id]:
                            self.rooms.pop(room_id, None)
            try:
                conn.close()
            except OSError:
                pass

    def _register_client(self, room_id: str, role: str, conn: socket.socket):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                room = {}
                self.rooms[room_id] = room
            room[role] = conn

    def _get_target(self, room_id: str, role: str) -> socket.socket | None:
        if not room_id:
            return None
        other_role = "guest" if role == "host" else "host"
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return None
            return room.get(other_role)

    def _recv_all(self, conn: socket.socket, n: int) -> bytes | None:
        data = b""
        while len(data) < n:
            try:
                part = conn.recv(n - len(data))
                if not part:
                    return None
                data += part
            except OSError:
                return None
        return data


if __name__ == "__main__":
    server = RelayServer()
    server.start()

