"""Local Python server for the Vehicle Availability prototype.

Run with: python3 server.py
Then open http://localhost:8000 in a browser.
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "dummy_data.json"


def load_data() -> dict:
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


class VehicleAvailabilityHandler(SimpleHTTPRequestHandler):
    """Serves the prototype files plus a small, in-memory JSON API."""

    data = load_data()

    def send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        if parsed.path == "/api/reservations":
            self.send_json(self.data["reservations"])
            return

        if parsed.path == "/api/vehicles":
            query = parse_qs(parsed.query)
            reservation_id = query.get("reservation_id", [""])[0]
            reservation = next(
                (item for item in self.data["reservations"] if item["id"] == reservation_id),
                None,
            )
            vehicles = self.data["vehicles"]
            if reservation:
                # The dataset intentionally includes alternatives to demonstrate
                # category substitutions and equipment gaps.
                vehicles = [
                    {**vehicle, "from": reservation["category"]}
                    for vehicle in vehicles
                ]
            self.send_json(vehicles)
            return

        if parsed.path == "/api/health":
            self.send_json({"status": "ok"})
            return

        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if urlparse(self.path).path != "/api/assignments":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            reservation_id = payload["reservation_id"]
            vehicle_id = payload["vehicle_id"]
        except (json.JSONDecodeError, KeyError, ValueError):
            self.send_json({"error": "reservation_id and vehicle_id are required"}, HTTPStatus.BAD_REQUEST)
            return

        reservation = next((item for item in self.data["reservations"] if item["id"] == reservation_id), None)
        vehicle = next((item for item in self.data["vehicles"] if item["id"] == vehicle_id), None)
        if not reservation or not vehicle:
            self.send_json({"error": "Reservation or vehicle was not found"}, HTTPStatus.NOT_FOUND)
            return

        reservation["status"] = "assigned"
        assignment = {"reservation_id": reservation_id, "vehicle_id": vehicle_id, "status": "confirmed"}
        self.send_json(assignment, HTTPStatus.CREATED)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("", 8000), VehicleAvailabilityHandler)
    print("Vehicle Availability is running at http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
