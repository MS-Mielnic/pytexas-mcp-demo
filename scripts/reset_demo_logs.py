from pathlib import Path

AUDIT_LOG = Path("logs/audit/audit.jsonl")
PROTOCOL_LOG = Path("logs/protocol/protocol.log")


def reset_file(path: Path):
    if path.exists():
        path.write_text("")  # truncate file
        print(f"[OK] Cleared: {path}")
    else:
        # create empty file if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        print(f"[OK] Created empty file: {path}")


def main():
    print("Resetting demo logs...\n")

    reset_file(AUDIT_LOG)
    reset_file(PROTOCOL_LOG)

    print("\nDone. Logs are clean for next run.")


if __name__ == "__main__":
    main()
