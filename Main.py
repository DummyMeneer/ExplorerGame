import pygame
from PIL import Image
from GameObjects import TerrainManager, InfiniteMap, Player
import os
from datetime import datetime


#----------



#----------

# --- Settings ---
TOP_BAR_HEIGHT = 50
MAP_OFFSET_Y = TOP_BAR_HEIGHT
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_SIZE = 800  # Added because it was used but not defined
BASE_TILE_SIZE  = 20
PLAYER_COLOR = (255, 255, 255)
DARK_GREY = (40, 40, 40)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
FONT_SIZE = 24
BACKGROUND_COLOR = (0, 0, 0)
FPS = 30

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Void Explorer - Infinite")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", FONT_SIZE)

# --- Load Tile Textures ---
# Ensure your image files are in a folder called "assets"
TILE_IMAGES = {
    "forest": pygame.image.load(os.path.join("Deltaexplorer/assets", "forest.png")),
    "desert": pygame.image.load(os.path.join("Deltaexplorer/assets", "desert.png")),
    "water": pygame.image.load(os.path.join("Deltaexplorer/assets", "water.png")),
    "stone": pygame.image.load(os.path.join("Deltaexplorer/assets", "stone.png")),
    "dirt": pygame.image.load(os.path.join("Deltaexplorer/assets", "dirt.png")),
    "sand": pygame.image.load(os.path.join("Deltaexplorer/assets", "sand.png")),
    "jungle": pygame.image.load(os.path.join("Deltaexplorer/assets", "jungle.png")),
    "plains": pygame.image.load(os.path.join("Deltaexplorer/assets", "plains.png")),
    "clay": pygame.image.load(os.path.join("Deltaexplorer/assets", "clay.png")),
    "mountain": pygame.image.load(os.path.join("Deltaexplorer/assets", "mountain.png")),
    "snow": pygame.image.load(os.path.join("Deltaexplorer/assets", "snow.png")),
    "swamp": pygame.image.load(os.path.join("Deltaexplorer/assets", "swamp.png")),
    "town": pygame.image.load(os.path.join("Deltaexplorer/assets", "town.png"))
}

# --- Game Objects ---
terrain_manager = TerrainManager()
game_map = InfiniteMap(terrain_manager)
player = Player(0,0)

# Reveal starting tile
game_map.reveal_tile(player.x, player.y)

# --- Camera & Zoom ---
zoom = 1.0  # 1.0 = normal size

# Stats
steps_taken = 0

def world_to_screen(wx, wy, player, zoom):
    """Convert world coordinates to screen position."""
    tile_size = int(BASE_TILE_SIZE * zoom)
    # Center player
    screen_x = SCREEN_SIZE // 2 + (wx - player.x) * tile_size
    screen_y = SCREEN_SIZE // 2 + (wy - player.y) * tile_size
    return screen_x, screen_y, tile_size

def save_explored_map():
    """Export revealed map to image using each tile's center pixel as representative color."""
    coords = list(game_map.tiles.keys())
    if not coords:
        print("No tiles revealed yet.")
        return

    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    img = Image.new("RGB", (width, height))
    pixels = img.load()

    for (x, y), tile_data in game_map.tiles.items():
        px = x - min_x
        py = y - min_y

        # tile_data is a dict {"type": ..., "texture": Surface}
        texture = tile_data["texture"]
        # Extract center pixel color from the texture surface (drop alpha)
        w, h = texture.get_size()
        r, g, b, *rest = texture.get_at((w // 2, h // 2))
        center_color = (r, g, b)
        pixels[px, py] = center_color

    # Scale up for visibility and save
    img = img.resize((width * 10, height * 10), Image.NEAREST)
    filename = f"explored_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(filename)
    print(f"Map saved as {filename}")


# --- Top Bar UI ---
def draw_top_bar():
    pygame.draw.rect(screen, DARK_GREY, (0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT))

    # Draw stats
    explored_count = len(game_map.tiles)
    explored_text = font.render(f"Tiles Explored: {explored_count}", True, (255, 255, 255))
    steps_text = font.render(f"Steps: {steps_taken}", True, (255, 255, 255))

    screen.blit(explored_text, (10, 10))
    screen.blit(steps_text, (250, 10))

    # Draw print button
    print_button_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 30)
    pygame.draw.rect(screen, GREEN, print_button_rect, border_radius=6)
    text_surface = font.render("Print", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=print_button_rect.center)
    screen.blit(text_surface, text_rect)

    return print_button_rect

# --- Main Loop ---
running = True
while running:
    print_button_rect = draw_top_bar()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if print_button_rect.collidepoint(event.pos):
                save_explored_map()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                save_explored_map()
            elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1

                player.move(dx, dy)
                steps_taken += 1
                game_map.reveal_tile(player.x, player.y)

            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                zoom = min(zoom + 0.1, 3.0)
            elif event.key == pygame.K_MINUS:
                zoom = max(zoom - 0.1, 0.5)

    # --- Draw ---
    screen.fill(BACKGROUND_COLOR)

    # Draw top bar again after clearing
    print_button_rect = draw_top_bar()

    tile_size = int(BASE_TILE_SIZE * zoom)
    # Calculate how many tiles fit on screen (for culling)
    half_tiles_x = SCREEN_SIZE // (2 * tile_size) + 2
    half_tiles_y = SCREEN_SIZE // (2 * tile_size) + 2

    # Only draw visible tiles
    for x in range(player.x - half_tiles_x, player.x + half_tiles_x + 1):
        for y in range(player.y - half_tiles_y, player.y + half_tiles_y + 1):
            tile_type = game_map.get_tile_type(x, y)
            if tile_type:
                sx, sy, size = world_to_screen(x, y, player, zoom)
                tile_image = pygame.transform.scale(TILE_IMAGES[tile_type], (size, size))
                screen.blit(tile_image, (sx, sy))

    # Draw player
    px, py, size = world_to_screen(player.x, player.y, player, zoom)
    pygame.draw.rect(screen, PLAYER_COLOR, (px, py, size, size), 2)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


