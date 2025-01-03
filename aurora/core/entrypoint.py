from ui.cli import main
import asyncio

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
