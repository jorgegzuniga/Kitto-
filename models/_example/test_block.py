"""Pipeline smoke test: a filleted block with a keyring hole. Delete once real models exist."""
from build123d import Box, Cylinder, Pos, Rot, fillet, Axis

block = Box(40, 24, 8)
block = fillet(block.edges().filter_by(Axis.Z), radius=6)
hole = Pos(14, 0, 0) * Cylinder(2.5, 10)
part = block - hole
