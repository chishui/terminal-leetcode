from .terminal import Terminal


def main():
    """Main entry point"""
    try:
        term = Terminal()
        term.run()
    except Exception:
        pass
