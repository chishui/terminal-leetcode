from .log import init_logger
from .terminal import Terminal
from .auth import Auth


def main():
    """Main entry point"""
    init_logger()
    try:
        auth = Auth()
        term = Terminal(auth)
        term.run()
    except Exception:
        pass
