import json

def read_event_stream(path: str):
    """
    Reads append-only JSONL audit log.
    """
    with open(path, "r") as f:
        for line in f:
            yield json.loads(line)
