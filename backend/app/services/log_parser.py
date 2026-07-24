import re
from pathlib import Path


class LogParser:
    """
    Parses raw application logs into structured data.
    """

    LOG_PATTERNS = [
        re.compile(
            r"^(?:\[(?P<timestamp>\d{2}:\d{2}:\d{2})\]|(?P<timestamp_plain>\d{2}:\d{2}:\d{2}))\s+"
            r"(?P<level>ERROR|WARNING|INFO)\s+"
            r"(?P<message>.+)$"
        ),
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:Z)?)\s+"
            r"(?P<level>ERROR|WARNING|INFO)\s+"
            r"(?P<message>.+)$"
        ),
        re.compile(
            r"^(?P<level>ERROR|WARNING|INFO)[:\s-]+(?P<message>.+)$"
        ),
    ]

    def parse(self, file_path: str):

        parsed_logs = []

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found.")

        with file_path.open("r", encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                parsed = self._parse_line(line)

                if parsed is not None:
                    parsed_logs.append(parsed)

        return parsed_logs

    def _parse_line(self, line: str):
        for pattern in self.LOG_PATTERNS:
            match = pattern.match(line)
            if not match:
                continue

            data = match.groupdict()
            timestamp = data.get("timestamp") or data.get("timestamp_plain")
            message = data["message"].strip()

            service = self.detect_service(message)

            return {
                "timestamp": timestamp,
                "level": data["level"],
                "service": service,
                "message": message,
            }

        return None

    def detect_service(self, message):

        message = message.lower()

        if "database" in message:
            return "Database"

        if "payment" in message:
            return "Payment"

        if "gateway" in message:
            return "API Gateway"

        if "redis" in message:
            return "Redis"

        if "cache" in message:
            return "Cache"

        return "Unknown"