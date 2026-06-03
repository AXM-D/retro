import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="RETRO - Active Defense & Counterattack OSINT Platform")
    parser.add_argument("--config", "-c", type=str, help="Path to config YAML")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8500, help="Port (default: 8500)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload")
    args = parser.parse_args()
    if args.config:
        from retro.core.config import load_config
        load_config(args.config)
    uvicorn.run("retro.api.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
