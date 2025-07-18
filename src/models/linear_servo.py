from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple, cast)

from typing_extensions import Self
from viam.components.servo import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes, struct_to_dict
from viam.components.motor import Motor

import asyncio

class LinearServo(Servo, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("mcvella", "servo"), "linear-servo"
    )
    motor: Motor
    position: int = 0
    start_position: int = 90
    max_position_degrees: int = 180
    min_position_degrees: int = 0 
    total_degrees: int = 180
    mm_per_second: float
    length_inches: float
    
    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Servo component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any required dependencies or optional dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies and the
                second element is a list of optional dependencies
        """
        required = []
        optional = []
        attributes = struct_to_dict(config.attributes)
        motor = attributes.get("motor")
        if motor is None:
            raise Exception("motor is required")
        required.append(motor)
        
        length_inches = attributes.get("length_inches")
        if length_inches is None:
            raise Exception("length_inches is required")
        mm_per_second = attributes.get("mm_per_second")
        if mm_per_second is None:
            raise Exception("mm_per_second is required")

        return required, optional

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both required and optional)
        """
    
        attributes = struct_to_dict(config.attributes)
        motor_name = attributes.get("motor")
        motor = dependencies[Motor.get_resource_name(str(motor_name))]
        self.motor = cast(Motor, motor)
        self.length_inches = cast(float, attributes.get("length_inches", 0))
        self.mm_per_second = cast(float, attributes.get("mm_per_second", 0))
        self.max_position_degrees = cast(int, attributes.get("max_position_degrees", self.max_position_degrees))
        self.min_position_degrees = cast(int, attributes.get("min_position_degrees", self.min_position_degrees))
        self.total_degrees = cast(int, attributes.get("total_degrees", self.total_degrees))
        self.position = cast(int, attributes.get("start_position", self.start_position))
        asyncio.ensure_future(self.initialize())
        
        return super().reconfigure(config, dependencies)

    async def initialize(self):
        # Calibration sequence: go to min, then max, then target position
        self.logger.info("Starting calibration sequence...")
        
        # Store the original target position before calibration moves
        target_position = self.position
        
        # First, go to minimum position to establish baseline
        self.logger.info(f"Moving to minimum position: {self.min_position_degrees}°")
        await self.move(self.min_position_degrees)
        
        # Then go to maximum position to establish full range
        self.logger.info(f"Moving to maximum position: {self.max_position_degrees}°")
        await self.move(self.max_position_degrees)
        
        # Finally, go to the actual target position
        self.logger.info(f"Moving to target position: {target_position}°")
        await self.move(target_position)
        
        self.logger.info("Calibration sequence completed")
    
    async def move(
        self,
        angle: int,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        # Calculate the target position within bounds
        target_position = max(self.min_position_degrees, min(angle, self.max_position_degrees))
        
        # Calculate the distance to move in degrees
        degrees_to_move = target_position - self.position
        
        if degrees_to_move == 0:
            return  # Already at target position
        
        # Calculate the physical distance to move in inches
        # Convert degrees to linear distance based on total travel
        inches_per_degree = self.length_inches / self.total_degrees
        inches_to_move = abs(degrees_to_move) * inches_per_degree
        
        # Convert to mm and calculate time needed
        mm_to_move = inches_to_move * 25.4  # Convert inches to mm
        time_needed = mm_to_move / self.mm_per_second
        
        # Determine direction (positive or negative power)
        power = 1.0 if degrees_to_move > 0 else -1.0
        
        # Set motor power and run for calculated time
        await self.motor.set_power(power)
        await asyncio.sleep(time_needed)
        await self.motor.stop()
        
        # Update current position
        self.position = int(target_position)

    async def get_position(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> int:
        return self.position

    async def stop(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        await self.motor.stop()

    async def is_moving(self) -> bool:
        return await self.motor.is_moving()

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        self.logger.error("`do_command` is not implemented")
        raise NotImplementedError()

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()

