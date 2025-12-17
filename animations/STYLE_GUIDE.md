# Day 1 Animation - Style Guide & Architecture

## Overview
The Day 1 animation has been refactored into a modular, well-documented structure with extensive style documentation and reusable helper functions.

## File Structure
- `day1.py` - Main refactored animation (current version)
- `day1_old.py` - Previous monolithic version (before refactoring)
- `day1_backup.py` - Additional backup copy

## Architecture

### Main Entry Point
```python
def construct(self):
    """Orchestrates all three scenes."""
    self.scene_problem()
    self.clear()
    self.scene_algorithm()
    self.clear()
    self.scene_circuit()
```

### Scene Functions

#### Scene 1: Problem Demonstration
- `scene_problem()` - Main problem scene
  - Demonstrates dial mechanics with visual examples
  - Shows instruction processing
  - Tracks Part 1 (lands on 0) and Part 2 (crosses 0) counters

#### Scene 2: Algorithm Explanation
- `scene_algorithm()` - Main algorithm scene orchestrator
  - `algorithm_part1()` - Part 1: Landing on zero
  - `algorithm_part2()` - Part 2: Crossing zero (with separate L/R formulas)
  - `algorithm_fixed_point()` - Fixed-point division optimization

#### Scene 3: Circuit Implementation
- `scene_circuit()` - Main circuit scene orchestrator
  - `circuit_stage_input()` - Stage 1: Input buffer
  - `circuit_stage_position()` - Stage 2: Position register
  - `circuit_stage_parallel_compute()` - Stage 3: Parallel LEFT/RIGHT computation
  - `circuit_stage_mux()` - Stage 4: Direction multiplexer
  - `circuit_stage_feedback()` - Stage 5: Feedback loop
  - `circuit_stage_counters()` - Stage 6: Part 1 and Part 2 counters
  - `circuit_dataflow_demo()` - Complete dataflow animation

### Helper Functions (Parameterized Visuals)

#### `create_dial(radius, center, include_labels)`
Creates a circular dial with consistent styling.
- Handles tick marks (every 5 units)
- Longer ticks every 25 units
- Labels every 10 units
- 0 at right, counterclockwise numbering

#### `create_arrow_pointer(dial_or_circle, position, center, stroke_width)`
Creates arrow pointer for dial at specified position.

#### `animate_dial_rotation(arrow, dial_center, position_tracker, direction, magnitude, show_crossings, p2_counter, dial_radius)`
Animates dial rotation with proper flash timing.
- **CRITICAL**: Flashes occur BEFORE rotation segments
- Flash: 0.15s, then Rotation: 0.35s per segment
- Handles both LEFT and RIGHT directions
- Automatically calculates zero crossings

#### `create_code_block(lines, scale)`
Creates styled code blocks using VGroup + Text.
- **CRITICAL**: Uses Text with Monospace font instead of Code class
- Returns tuple: (code_lines VGroup, code_box Rectangle)
- Consistent gray styling

## Style Preferences (Documented in Code)

### Flash Timing
```python
FLASH_DURATION = 0.15  # Flash before rotation
ROTATION_DURATION = 0.35  # Rotation per crossing segment
```
**Why**: Ensures flash is synchronized with arrow crossing zero, not during rotation.

### Code Blocks
```python
# STYLE PREFERENCE: Use VGroup with Text instead of Code class
code_lines, code_box = self.create_code_block([
    "if direction == RIGHT:",
    "    crossings = (pos + mag) // 100",
    ...
])
```
**Why**: Manim's Code class has compatibility issues with certain parameter names.

### Formulas
```python
# STYLE PREFERENCE: Different formulas for LEFT vs RIGHT
formula_p2_right = MathTex(r"\text{Right: } \lfloor (\text{pos} + \text{mag}) / 100 \rfloor")
formula_p2_left = MathTex(r"\text{Left: } \lfloor (\text{pos} - 1) / 100 \rfloor - \lfloor (\text{pos} - \text{mag} - 1) / 100 \rfloor")
```
**Why**: LEFT direction uses different zero-crossing calculation than RIGHT.

### Layout
```python
# STYLE PREFERENCE: Absolute positioning to prevent overflow
why_box = Rectangle(...).shift(DOWN*2.5)  # Not relative positioning
```
**Why**: Relative positioning can push elements off-screen.

### Circuit Dataflow
```python
# STYLE PREFERENCE: Show parallel computation before mux selection
# Both paths receive position (ORANGE) and magnitude (YELLOW)
arrow_pos_r = Arrow(..., color=self.COLOR_POSITION)
arrow_pos_l = Arrow(..., color=self.COLOR_POSITION)
arrow_mag_r = CurvedArrow(..., color=self.COLOR_MAGNITUDE)
arrow_mag_l = CurvedArrow(..., color=self.COLOR_MAGNITUDE)
# Then mux selects between pre-computed results
```
**Why**: Accurately represents parallel hardware architecture where both paths compute simultaneously.

## Constants

### Visual Constants
```python
DIAL_RADIUS = 2.5          # Main problem dial
DEMO_DIAL_RADIUS = 1.5     # Algorithm explanation dial
SIM_DIAL_RADIUS = 0.8      # Circuit simulation dial
```

### Timing Constants
```python
FLASH_DURATION = 0.15      # Flash before rotation
ROTATION_DURATION = 0.35   # Rotation per crossing
STANDARD_WAIT = 0.5        # Standard pause
LONG_WAIT = 1.5            # Extended pause
EXTENDED_WAIT = 2.0        # Long pause
```

### Colors
```python
COLOR_DIAL = BLUE
COLOR_ARROW = RED
COLOR_PART1 = GREEN         # Landing on zero
COLOR_PART2 = YELLOW        # Crossing zero
COLOR_DIRECTION = RED       # Direction signal
COLOR_POSITION = ORANGE     # Position data
COLOR_MAGNITUDE = YELLOW    # Magnitude data
COLOR_MUX = PURPLE          # Multiplexer
COLOR_CODE = GRAY           # Code blocks
COLOR_COMPUTE_BOX = BLUE    # Computation boxes
```

### Text Scales
```python
SCALE_TITLE = 0.8       # Scene titles
SCALE_SUBTITLE = 0.6    # Sub-scene titles
SCALE_TEXT = 0.5        # Standard text
SCALE_SMALL = 0.4       # Small text
SCALE_TINY = 0.3        # Very small text
SCALE_CODE = 0.35       # Code text
```

## Benefits of Refactoring

1. **Modularity**: Each scene is a separate function, easy to modify independently
2. **Reusability**: Helper functions ensure consistent visuals across scenes
3. **Documentation**: Extensive docstrings and comments explain every style choice
4. **Maintainability**: Clear structure makes it easy to find and update specific elements
5. **Consistency**: Parameterized functions ensure uniform dial creation, rotation, etc.
6. **Testability**: Individual scene functions can be tested in isolation

## Usage Examples

### Creating a dial
```python
dial = self.create_dial(radius=2.5, center=ORIGIN, include_labels=True)
```

### Animating rotation
```python
new_pos = self.animate_dial_rotation(
    arrow, dial_center, pos_tracker, 
    direction="R", magnitude=45,
    show_crossings=True, p2_counter=counter
)
```

### Creating code blocks
```python
code_lines, code_box = self.create_code_block([
    "new_pos = (pos + mag) % 100",
    "if next_pos == 0:",
    "    part1_count += 1"
], scale=0.4)
```

## Rendering

Render the animation using:
```bash
manim -ql day1.py Day1  # Low quality (480p15) for fast preview
manim -qh day1.py Day1  # High quality (1080p60) for final render
```
