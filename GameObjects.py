# GameObjects.py
import os
import random
import pygame

class TerrainManager:
    """Handles terrain names, texture loading and weighted selection + export colors."""
    def __init__(self, asset_folder="assets"):
        # ordered list of terrain type names
        self.terrain_names = [
            "forest", "desert", "water", "stone", "dirt",
            "sand", "jungle", "plains", "clay", "mountain",
            "snow", "town", "swamp"
        ]

        # load textures (pygame Surfaces). fallback: colored placeholder
        self.terrains = []
        for name in self.terrain_names:
            path = os.path.join(asset_folder, f"{name}.png")
            try:
                texture = pygame.image.load(path).convert_alpha()
            except Exception:
                # fallback placeholder surface (32x32)
                texture = pygame.Surface((32, 32), pygame.SRCALPHA)
                texture.fill([random.randint(50, 255) for _ in range(3)])
            self.terrains.append(texture)

        # small influence to avoid monotone maps (tweak to taste)
        self.influence_factor = 0.5

        # representative colors for export (RGB tuples). Adjust if you want different export colors.
        self.color_map = {
            "forest": (34, 139, 34),
            "desert": (210, 180, 140),
            "water": (70, 130, 180),
            "stone": (169, 169, 169),
            "dirt": (205, 133, 63),
            "sand": (222, 184, 135),
            "jungle": (46, 139, 87),
            "plains": (240, 230, 140),
            "clay": (160, 82, 45),
            "mountain": (112, 128, 144),
            "snow": (240, 248, 255),
            "town": (150, 111, 51),
            "swamp": (47, 79, 47),
        }

    def get_random_terrain(self, neighbor_types):
        """
        Return (terrain_type_name, texture_surface) chosen with neighbor influence.
        neighbor_types: list of strings (terrain names) from adjacent tiles.
        """
        # base weights (equal)
        weights = [1.0 for _ in self.terrains]

        # add influence from neighbors (neighbor_types are strings)
        for nt in neighbor_types:
            if nt in self.terrain_names:
                idx = self.terrain_names.index(nt)
                weights[idx] += self.influence_factor

        # weighted pick
        total = sum(weights)
        pick = random.uniform(0, total)
        cumulative = 0.0
        for i, w in enumerate(weights):
            cumulative += w
            if pick <= cumulative:
                return self.terrain_names[i], self.terrains[i]

        # fallback
        i = random.randrange(len(self.terrains))
        return self.terrain_names[i], self.terrains[i]

    def get_texture(self, type_name):
        """Return the loaded texture Surface for a terrain name (or None)."""
        if type_name in self.terrain_names:
            i = self.terrain_names.index(type_name)
            return self.terrains[i]
        return None

    def get_tile_color(self, type_name):
        """Return RGB color for export for a terrain name (fallback black)."""
        return self.color_map.get(type_name, (0, 0, 0))


class InfiniteMap:
    """Stores revealed tiles with both 'type' and 'texture' for each coordinate."""
    def __init__(self, terrain_manager):
        self.tiles = {}  # (x,y) -> {"type": str, "texture": Surface}
        self.terrain_manager = terrain_manager

    def get_neighbors(self, x, y, include_diagonals=False):
        """Return a list of neighbor terrain type names (strings)."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if include_diagonals:
            directions += [(-1, -1), (1, -1), (-1, 1), (1, 1)]

        neighbors = []
        for dx, dy in directions:
            tile = self.tiles.get((x + dx, y + dy))
            if tile:
                neighbors.append(tile["type"])
        return neighbors

    def reveal_tile(self, x, y):
        """Reveal tile at (x,y) — choose a terrain type influenced by neighbor types."""
        if (x, y) not in self.tiles:
            neighbors = self.get_neighbors(x, y)
            if neighbors:
                # get_random_terrain returns (type_name, texture_surface)
                terrain_type, texture = self.terrain_manager.get_random_terrain(neighbors)
            else:
                # first-tile random choice
                i = random.randrange(len(self.terrain_manager.terrain_names))
                terrain_type = self.terrain_manager.terrain_names[i]
                texture = self.terrain_manager.terrains[i]

            # store a dict with consistent keys
            self.tiles[(x, y)] = {"type": terrain_type, "texture": texture}

    def get_tile_texture(self, x, y):
        tile = self.tiles.get((x, y))
        return tile["texture"] if tile else None

    def get_tile_type(self, x, y):
        tile = self.tiles.get((x, y))
        return tile["type"] if tile else None

    def all_tiles(self):
        """Yield (x, y, texture, type_name) for every revealed tile."""
        for (x, y), tile in self.tiles.items():
            yield x, y, tile["texture"], tile["type"]


class Player:
    """Simple player position holder."""
    def __init__(self, start_x=0, start_y=0):
        self.x = start_x
        self.y = start_y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy