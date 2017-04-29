from .log import init_logger
from .terminal import Terminal

def main():
    """Main entry point"""
    init_logger()
    try:
        term = Terminal()
        term.run()
    except Exception:
        pass
