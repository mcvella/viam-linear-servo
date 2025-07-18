import asyncio
from viam.module.module import Module
try:
    from models.linear_servo import LinearServo
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.linear_servo import LinearServo


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
