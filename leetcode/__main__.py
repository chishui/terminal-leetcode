from .terminal import Terminal
from .log import init_logger

def main():
    """Main entry point"""
    init_logger()
    try:
        term = Terminal()
        term.run()
    except Exception:
        pass
