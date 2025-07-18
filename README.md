# Linear Servo Module

A Viam module that emulates a servo component using a linear actuator controlled by a motor. This module provides servo-like behavior (position control in degrees) while using a linear actuator for physical movement.

## Model mcvella:servo:linear-servo

The linear servo model converts angular position commands (in degrees) into linear actuator movements. It calculates the required movement time based on the actuator's speed and travel distance, then controls the motor at full power for the calculated duration.

### Features

- **Servo-like Interface**: Accepts position commands in degrees (0-180° by default)
- **Linear Actuator Control**: Converts angular positions to linear movements
- **Automatic Calibration**: Performs min/max calibration on initialization
- **Configurable Range**: Customizable minimum and maximum position limits
- **Duration-based Control**: Motor runs at full power for calculated time based on speed
- **Position Tracking**: Maintains current position state

### Configuration

The following attribute template can be used to configure this model:

```json
{
  "motor": "<motor_name>",
  "length_inches": <float>,
  "mm_per_second": <float>,
  "max_position_degrees": <int>,
  "min_position_degrees": <int>,
  "total_degrees": <int>,
  "start_position": <int>
}
```

#### Attributes

The following attributes are available for this model:

| Name                    | Type   | Inclusion | Default | Description                                    |
|-------------------------|--------|-----------|---------|------------------------------------------------|
| `motor`                 | string | Required  | -       | Name of the motor component to control         |
| `length_inches`         | float  | Required  | -       | Total travel length of the linear actuator     |
| `mm_per_second`         | float  | Required  | -       | Movement speed used to calculate duration      |
| `max_position_degrees`  | int    | Optional  | 180     | Maximum angular position (degrees)             |
| `min_position_degrees`  | int    | Optional  | 0       | Minimum angular position (degrees)             |
| `total_degrees`         | int    | Optional  | 180     | Total angular range (degrees)                  |
| `start_position`        | int    | Optional  | 90      | Initial position after calibration (degrees)   |

#### Example Configuration

```json
{
  "motor": "my_linear_motor",
  "length_inches": 10.0,
  "mm_per_second": 25.4,
  "max_position_degrees": 180,
  "min_position_degrees": 0,
  "total_degrees": 180,
  "start_position": 90
}
```

### How It Works

1. **Position Conversion**: Angular positions (degrees) are converted to linear distances based on the total travel range
2. **Time Calculation**: Movement time is calculated using `distance / speed`
3. **Motor Control**: The motor runs at full power (±1.0) for the calculated duration
4. **Calibration**: On initialization, the actuator moves to min, then max, then target position

### Example Movement Calculation

For a 10-inch actuator with 25.4 mm/second speed:
- Moving from 90° to 0° (90° movement)
- Linear distance: `(90° / 180°) × 10 inches = 5 inches`
- Time needed: `(5 inches × 25.4 mm/inch) / 25.4 mm/second = 5 seconds`
- Motor runs at -1.0 power (full reverse) for 5 seconds

### API Methods

The linear servo implements the standard servo interface:

- `move(angle)`: Move to specified angle in degrees
- `get_position()`: Return current position in degrees
- `stop()`: Stop any current movement
- `is_moving()`: Check if currently moving

### Calibration

On initialization, the module performs a calibration sequence:
1. Move to minimum position
2. Move to maximum position  
3. Move to target start position

This ensures accurate position tracking and validates the full range of motion.
