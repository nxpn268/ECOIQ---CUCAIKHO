import os, random, math, pygame  # Import các thư viện cơ bản
from os import listdir  # Import hàm lấy danh sách file trong thư mục
from os.path import isfile, join  # Import hàm kiểm tra file và nối đường dẫn
import time 
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


pygame.init()  # Khởi tạo pygame



# Set up khung màn hình và background

# Độ rộng màn hình:
WIDTH, HEIGHT = 1200, 700
FPS = 60
PLAYER_VEL = 5
white = (255, 255, 255)
# Khởi tạo cửa số game
window = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('''UEH Discovery''')

# Setup phông chữ:
Font = pygame.font.SysFont('''Pixel Sans''', 25)

# Đặt tiêu đề cho cửa sổ game
pygame.display.set_caption('''Platformer''') 

# Tạo màu chuyển động
gradient_color = pygame.Color(0, 0, 0)
color_step = 1  # Tốc độ chuyển màu

gradient_color.hsva = ((gradient_color.hsva[0] + color_step) % 360, 100, 100, 100)





# Khởi tạo đồng hồ đếm thời gian 
clock = pygame.time.Clock()


# Thiết lập danh sách các bài nhạc
music_lists = ['''songs1.mp3''', '''songs 2.mp3''', '''songs 3.mp3''', '''songs 4.mp3''']

# Thiết lập mixer cho audio
pygame.mixer.init()

# Hàm cho phát nhạc random trong list, make sure là trong một lần chơi thì phát nhạc không trùng lặp với vòng trước
def play_random_musicbg(previous_song=None):
    available_songs = [song for song in music_lists if song != previous_song]
    current_song = random.choice(available_songs)
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play(-1)  # Loop the music
    return current_song

# Khi sử dụng trong các main game thì ở đoạn đầu cần phải khai báo 
# previous_song  = None
# sau đó trong đoạn chính thì có dòng  previous_song = play_random_music(previous_song)  # Play new random music
# Set up hiện là đang play song nào bằng cách:  song_text = font.render(f'''Now playing: {previous_song}''', True, (255, 255, 255)
#   screen.blit(song_text, (320 - song_text.get_width() // 2, 250))



# Hàm lật hình ảnh (sprites) theo chiều ngang
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]  # Lật từng sprite trong danh sách

# Hàm tải các sprite từ sprite sheet
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join('''assets''', dir1, dir2)  # Đường dẫn tới thư mục chứa sprite
    images = [f for f in listdir(path) if isfile(join(path, f))]  # Lấy danh sách các file trong thư mục
    all_sprites = {}  # Dictionary chứa các sprite

    for image in images:  # Lặp qua từng file ảnh
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  # Tải ảnh với hỗ trợ alpha
        sprites = []  # Danh sách các sprite tách ra từ sprite sheet
        for i in range(sprite_sheet.get_width() // width):  # Tính số lượng sprite trong ảnh
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  # Tạo surface mới
            rect = pygame.Rect(i * width, 0, width, height)  # Xác định vùng của sprite trên sprite sheet
            surface.blit(sprite_sheet, (0, 0), rect)  # Sao chép sprite từ sprite sheet
            sprites.append(pygame.transform.scale2x(surface))  # Phóng to sprite lên 2 lần
        if direction:  # Nếu cần tạo sprite cho cả 2 hướng
            all_sprites[image.replace('''.png''', '''''') + '''_right'''] = sprites  # Sprite hướng phải
            all_sprites[image.replace('''.png''', '''''') + '''_left'''] = flip(sprites)  # Sprite hướng trái
        else:
            all_sprites[image.replace('''.png''', '''''')] = sprites  # Sprite mặc định
    return all_sprites  # Trả về dictionary chứa tất cả sprite

# Hàm lấy sprite khối vuông (block) -> chướng ngại vật 
def get_block(size):
    path = join('''assets''', '''Terrain''', '''Terrain.png''')  # Đường dẫn tới ảnh nền
    image = pygame.image.load(path).convert_alpha()  # Tải ảnh nền
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Tạo surface có kích thước khối vuông
    rect = pygame.Rect(0, 0, size, size)  # Xác định vùng khối vuông trong ảnh nền
    surface.blit(image, (0, 0), rect)  # Sao chép vùng khối vuông vào surface
    return pygame.transform.scale2x(surface)  # Phóng to surface lên 2 lần

class ScoreBoard:
    def __init__(self, screen, score, played_time, remaining_time):
        self.screen = screen
        self.score = score
        self.played_time = played_time
        self.remaining_time = remaining_time
        
        # Kích thước và vị trí bảng
        self.width = 400
        self.height = 300
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Font chữ
        self.title_font = pygame.font.SysFont('''Pixel Sans''', 36)
        self.text_font = pygame.font.SysFont('''Pixel Sans''', 36)
        
    def draw(self):
        # Vẽ background của bảng
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Vẽ tiêu đề
        title = self.title_font.render("Kết quả", True, (0, 0, 0))
        title_rect = title.get_rect(centerx=self.x + self.width//2, 
                                    y=self.y + 20)
        self.screen.blit(title, title_rect)
        
        # Vẽ thông tin
        texts = [
            f"Điểm số: {self.score}",
            f"Thời gian đã chơi: {self.played_time}s",
            f"Thời gian còn lại: {self.remaining_time}s"
        ]
        
        y_offset = 100
        for text in texts:
            text_surface = self.text_font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(centerx=self.x + self.width//2, 
                                            y=self.y + y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 50




# Lớp lựa chọn
class ButtonBoard:
    def __init__(self, screen, score):
        self.screen = screen
        self.score = score
        
        # Kích thước và vị trí bảng
        self.width = 400
        self.height = 200
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Font chữ
        self.font = pygame.font.Font(None, 36)
        
        # Tạo các nút
        self.buttons = []
        if score >= 4:
            self.buttons = [
                {"text": "Main Menu", "rect": pygame.Rect(self.x + 50, self.y + 50, 300, 40)},
                {"text": "Restart", "rect": pygame.Rect(self.x + 50, self.y + 100, 300, 40)},
                {"text": "Next Round", "rect": pygame.Rect(self.x + 50, self.y + 150, 300, 40)}
            ]
        else:
            self.buttons = [
                {"text": "Main Menu", "rect": pygame.Rect(self.x + 50, self.y + 50, 300, 40)},
                {"text": "Restart", "rect": pygame.Rect(self.x + 50, self.y + 100, 300, 40)}
            ]
            
    def draw(self):
        # Vẽ background của bảng
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Vẽ các nút
        for button in self.buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), button["rect"])
            pygame.draw.rect(self.screen, (0, 0, 0), button["rect"], 2)
            
            text = self.font.render(button["text"], True, (0, 0, 0))
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
            
    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["text"]
        return None

# Hàm vẽ chữ lên màn hình với khả năng điều chỉnh kích thước
def draw_text(window, text, x, y, size=36, center=False, color=white):
    font = pygame.font.SysFont(None, size)  # Tạo font với kích thước tùy chỉnh
    rendered_text = font.render(text, True, color)
    if center:
        x = x - rendered_text.get_width() // 2
        y = y - rendered_text.get_height() // 2
    window.blit(rendered_text, (x, y))

# Class đại diện cho nhân vật người chơi

def start_menu(window, background_image_path, button_position1):
    # Tải ảnh menu và scale fit với khung hình 
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # Set up button Start
    button_width, button_height = 200, 50
    button_color = (0, 200, 0)
    button_hover_color = (0, 255, 0)
    text_color = (255, 255, 255)
    font = pygame.font.SysFont('''Pixel Sans''', 36)

    # Define button position and rectangle
    button_x, button_y = button_position1
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Set up nhạc ở start_menu
    pygame.mixer.music.load('''mainmenu.mp3''')
    pygame.mixer.music.play(-1)  # Vòng lặp vô tận

    running = True
    while running:
        window.blit(background_image, (0, 0))
        

        draw_text(window, '''EcoIQ:The Trash Challenge''', WIDTH//2, 80,center=True,  color =(255, 87, 51), size = 80) # Sửa lại vị trí sau khi import ảnh nền của Hằng vào 
        # draw_text(window, '''EcoIQ:The Tr''', WIDTH//2-200, 80,center=True, color =(255, 195, 0), size = 80)
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
        button_current_color = button_hover_color if is_hovering else button_color

        # Vẽ nút Start lên screen
        pygame.draw.rect(window, button_current_color, button_rect)
        text_surface = font.render('''Start''', True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        window.blit(text_surface, text_rect)

        

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                pygame.mixer.music.stop()
                return '''start_game'''  # Close the menu and start the game

        pygame.display.update()
def menu_map(window, background_image_path, button_position2):
    # Load and scale the background image
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # Define button properties
    button_width, button_height = 300, 310
    button_hover_color = (0, 255, 0)
    # Load button image and scale
    button_image = pygame.image.load("assets\Background\map3.png")
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    # Define button position and rectangle
    button_x, button_y = button_position2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    running = True
    while running:
        window.blit(background_image, (0, 0))
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)

        # Draw hover effect
        if is_hovering:
            pygame.draw.rect(window, button_hover_color, button_rect, 5)

        # Draw the button
        window.blit(button_image, (button_x, button_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                return "return_to_main"  # Return to `main`

        pygame.display.update()

def menu_map2(window, background_image_path, button_position2):
    # Load and scale the background image
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # Define button properties
    button_width, button_height = 270, 330
    button_hover_color = (0, 255, 0)
    # Load button image and scale
    button_image = pygame.image.load("assets\Background\map2.png")
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    # Define button position and rectangle
    button_x, button_y = button_position2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    running = True
    while running:
        window.blit(background_image, (0, 0))
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)

        # Draw hover effect
        if is_hovering:
            pygame.draw.rect(window, button_hover_color, button_rect, 5)

        # Draw the button
        window.blit(button_image, (button_x, button_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                return "return_to_main"  # Return to `main`

        pygame.display.update()

def menu_map3(window, background_image_path, button_position2):
    # Load and scale the background image
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # Define button properties
    button_width, button_height = 280, 250
    button_hover_color = (0, 255, 0)
    # Load button image and scale
    button_image = pygame.image.load("assets\Background\map4.png")
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    # Define button position and rectangle
    button_x, button_y = button_position2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    running = True
    while running:
        window.blit(background_image, (0, 0))
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)

        # Draw hover effect
        if is_hovering:
            pygame.draw.rect(window, button_hover_color, button_rect, 5)

        # Draw the button
        window.blit(button_image, (button_x, button_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                return "return_to_main"  # Return to `main`

        pygame.display.update()

def menu_map4(window, background_image_path, button_position2):
    # Load and scale the background image
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    # Define button properties
    button_width, button_height = 305, 260
    button_hover_color = (0, 255, 0)
    # Load button image and scale
    button_image = pygame.image.load("assets\Background\map5.png")
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    # Define button position and rectangle
    button_x, button_y = button_position2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    running = True
    while running:
        window.blit(background_image, (0, 0))
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)

        # Draw hover effect
        if is_hovering:
            pygame.draw.rect(window, button_hover_color, button_rect, 5)

        # Draw the button
        window.blit(button_image, (button_x, button_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                return "return_to_main"  # Return to `main`

        pygame.display.update()
# Lớp cơ sở đại diện cho đối tượng trong game
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()  # Gọi constructor của lớp cha
        self.rect = pygame.Rect(x, y, width, height)  # Tạo hình chữ nhật đại diện cho đối tượng
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Tạo surface cho đối tượng
        self.width = width  # Chiều rộng đối tượng
        self.height = height  # Chiều cao đối tượng
        self.name = name  # Tên đối tượng (nếu có)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))  # Vẽ đối tượng lên màn hình


# Lớp đại diện cho khối vuông (block)
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  # Gọi constructor lớp cha
        block = get_block(size)  # Lấy sprite của khối
        self.image.blit(block, (0, 0))  # Sao chép sprite vào surface
        self.mask = pygame.mask.from_surface(self.image)  # Tạo mặt nạ va chạm từ sprite


# Lớp đại diện cho bẫy lửa (Fire)
class Fire(Object):
    ANIMATION_DELAY = 3  # Độ trễ giữa các khung hình animation

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, '''fire''')  # Gọi constructor lớp cha
        self.fire = load_sprite_sheets('''Traps''', '''Fire''', width, height)  # Tải sprite của bẫy lửa
        self.image = self.fire['''off'''][0]  # Đặt hình ảnh ban đầu của bẫy lửa là trạng thái '''tắt'''
        self.mask = pygame.mask.from_surface(self.image)  # Tạo mặt nạ va chạm từ hình ảnh
        self.animation_count = 0  # Bộ đếm animation
        self.animation_name = '''off'''  # Trạng thái ban đầu là '''tắt'''

    def on(self):
        self.animation_name = '''on'''  # Chuyển trạng thái bẫy lửa thành '''bật'''

    def off(self):
        self.animation_name = '''off'''  # Chuyển trạng thái bẫy lửa thành '''tắt'''

    def loop(self):
        sprites = self.fire[self.animation_name]  # Lấy danh sách sprite dựa trên trạng thái hiện tại
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Tính khung hình hiện tại
        self.image = sprites[sprite_index]  # Cập nhật hình ảnh hiện tại của bẫy lửa
        self.animation_count += 1  # Tăng bộ đếm animation
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))  # Cập nhật vị trí của hình chữ nhật
        self.mask = pygame.mask.from_surface(self.image)  # Cập nhật mặt nạ va chạm
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):  # Reset bộ đếm nếu vượt quá số khung hình
            self.animation_count = 0

# Hàm lấy nền của game từ file ảnh
def get_background(name):
    image = pygame.image.load(join('''assets''', '''Background''', name))  # Tải ảnh nền
    _, _, width, height = image.get_rect()  # Lấy kích thước của ảnh
    tiles = []  # Danh sách các vị trí cần vẽ nền
    for i in range(WIDTH // width + 1):  # Lặp qua trục X
        for j in range(HEIGHT // height + 1):  # Lặp qua trục Y
            pos = (i * width, j * height)  # Tính vị trí vẽ
            tiles.append(pos)  # Thêm vị trí vào danh sách
    return tiles, image  # Trả về danh sách vị trí và hình ảnh

# Hàm vẽ tất cả các đối tượng lên màn hình
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:  # Vẽ các ô nền
        window.blit(bg_image, tile)
    for obj in objects:  # Vẽ các đối tượng
        obj.draw(window, offset_x)
    player.draw(window, offset_x)  # Vẽ nhân vật
    pygame.display.update()  # Cập nhật màn hình

# Hàm tạo cấu trúc 3 khối vuông (block)
def create_three_block_structure(x, y, block_size, orientation='''horizontal'''):
    blocks = []  # Danh sách khối vuông
    if orientation == '''horizontal''':  # Kiểu nằm ngang
        for i in range(3):
            blocks.append(Block(x + i * block_size, y, block_size))
    elif orientation == '''vertical''':  # Kiểu dọc
        for i in range(3):
            blocks.append(Block(x, y + i * block_size, block_size))
    elif orientation == '''L-shape''':  # Kiểu chữ '''L'''
        blocks.append(Block(x, y, block_size))
        blocks.append(Block(x+ block_size, y - block_size, block_size))
        blocks.append(Block(x + block_size, y, block_size))
    elif orientation == '''question 1''':  # Kiểu nằm ngang
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 2''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 3''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 4''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 5''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''2horizontal''':  # Kiểu nằm ngang
        for i in range(2):
            blocks.append(Block(x + i * block_size, y, block_size))
    elif orientation == '''4horizontal''':  # Kiểu nằm ngang
        for i in range(4):
            blocks.append(Block(x + i * block_size, y, block_size))
    elif orientation == '''4vertical''':  # Kiểu dọc
        for i in range(4):
            blocks.append(Block(x, y + i * block_size, block_size))
    elif orientation == '''2vertical''':  # Kiểu dọc
        for i in range(2):
            blocks.append(Block(x, y + i * block_size, block_size))
    elif orientation == '''block''':  # Kiểu dọc
        for i in range(1):
            blocks.append(Block(x, y + i * block_size, block_size))
    else:
        raise ValueError('''Invalid orientation. Choose 'horizontal', 'vertical', or 'L-shape'.''')
    return blocks  # Trả về danh sách khối

# Hàm tạo cấu trúc 1 khối vuông câu hỏi

# Hàm kiểm tra va chạm theo phương dọc -> để đưa nhân vật đứng lên 
def handle_vertical_collision(player, object, dy):
    collided_object = []  # Danh sách các đối tượng va chạm
    for obj in object:  # Lặp qua các đối tượng
        if pygame.sprite.collide_mask(player, obj):  # Nếu va chạm
            if dy > 0:  # Nếu đang rơi xuống
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:  # Nếu đang nhảy lên
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_object.append(obj)  # Thêm đối tượng vào danh sách va chạm
    return collided_object  # Trả về danh sách

# Hàm kiểm tra va chạm theo phương ngang -> để đưa nhân vật đứng lên
def collide(player, object, dx):
    player.move(dx, 0)  # Di chuyển nhân vật
    player.update()  # Cập nhật trạng thái nhân vật
    collided_object = None
    for obj in object:  # Lặp qua các đối tượng
        if pygame.sprite.collide_mask(player, obj):  # Nếu va chạm
            collided_object = obj
            break
    player.move(-dx, 0)  # Trả lại vị trí ban đầu
    player.update()
    return collided_object

# Hàm xử lý di chuyển
def handle_move(player, object):
    keys = pygame.key.get_pressed()  # Lấy trạng thái bàn phím
    player.x_vel = 0  # Reset vận tốc ngang
    collide_left = collide(player, object, -PLAYER_VEL * 4)  # Kiểm tra va chạm bên trái
    collide_right = collide(player, object, PLAYER_VEL * 4)  # Kiểm tra va chạm bên phải
    if keys[pygame.K_LEFT] and not collide_left:  # Di chuyển trái nếu không va chạm
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:  # Di chuyển phải nếu không va chạm
        player.move_right(PLAYER_VEL)
    vertical_collide = handle_vertical_collision(player, object, player.y_vel)  # Xử lý va chạm dọc
    for obj in [collide_left, collide_right, *vertical_collide]:  # Kiểm tra va chạm với lửa
        if obj and obj.name == '''fire''':
            player.make_hit()

# Menu thắng 
def trigger_menu(window, background_image_path, button_position):
    '''''''''
    Displays a menu with a picture and button when triggered.
    Args:
        window (pygame.Surface): The game window.
        background_image_path (str): Path to the menu background image.
        button_position (tuple): Position of the button.

    Returns:
        str: Returns 'menu_map' if the button is clicked.
    '''''''''
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    button_width, button_height = 200, 50
    button_color = (0, 200, 0)
    button_hover_color = (0, 255, 0)
    text_color = (255, 255, 255)
    font = pygame.font.Font(None, 36)
    # Thiếu nội dung win game
    
    # Set up sound trước
    pygame.mixer.music.load('''soundtrigger.mp3''')
    pygame.mixer.music.load('''soundtrigger.mp3''')
    # Set up nhạc
    pygame.mixer.music.load('''triggermenu.mp3''')
    pygame.mixer.music.play(-1)  # Vòng lặp vô tận


    button_x, button_y = button_position
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    running = True
    while running:
        window.blit(background_image, (0, 0))

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if mouse is hovering over the button
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
        button_current_color = button_hover_color if is_hovering else button_color

        # Draw the button
        pygame.draw.rect(window, button_current_color, button_rect)
        text_surface = font.render('''Go to Map''', True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        window.blit(text_surface, text_rect)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                pygame.mixer.music.stop()
                return '''menu_map'''  # Trigger transition to `menu_map`

        pygame.display.update()
        

# Hàm thông báo đã win game hay chưa: nếu win thì có 2 lựa chọn là chơi tiếp vòng tiếp theo hoặc quay về menu map


# Hàm đếm thời gian và hiển thị đồng hồ trong từng màn
def countdown_timer(start_time, round_time):
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_left = round_time - elapsed_time
    return max(time_left, 0)  # Đảm bảo không trả về giá trị âm

# Hàm khởi tạo lớp hình ảnh dấu chấm hỏi đè lên blocks câu hỏi
    # Function to add question mark overlay to blocks
def add_question_mark_overlay(block):
    # Tải hình ảnh câu hỏi
    question_mark_image = pygame.image.load('''question.png''')
        
    # Điều chỉnh kích thước của hình ảnh câu hỏi cho vừa khít với block
    question_mark_image = pygame.transform.scale(question_mark_image, (96, 96))
        
    # Tạo một surface cho các block
    for b in block:
        # Thêm overlay câu hỏi vào block
        b.question_mark_surface = question_mark_image
            
    return block


# Khởi tạo danh sách các câu hỏi vòng 1
question_bank1 = [
    {'''question''': '''Đâu là cấu trúc địa chỉ Email của UEH?''',
     '''options''': ['''A. tenho.mssv@ueh.edu.vn''', '''B. tenho.mssv@st.ueh.edu.vn''', '''C.mssv@ueh.edu.vn''', '''D.mssv@st.ueh.edu.vn'''], 
     '''correct''': '''B'''},

    {'''question''': '''Sinh viên có thể tham khảo chương trình đào tạo của ngành mình đang học tại website nào?''',
     '''options''': ['''A. student.ueh.edu.vn''', '''B. dsa.ueh.edu.vn''', '''C. tckt.ueh.edu.vn''', '''D.cntt.ueh.edu.vn'''], 
     '''correct''': '''A'''},

    {'''question''': '''Sinh viên muốn tìm kiếm các cơ hội việc làm,
     thực tập thì có thể liên hệ phòng ban nào''', '''options''': ['''A. Phòng Nhân sự''', '''B. Phòng Marketing - Truyền thông''', '''C. Phòng Đào tạo''', '''D. Phòng Chăm sóc và hỗ trợ người học''' ], '''correct''': '''D'''}, 
    {'''question''': '''Để xét học bổng khuyến khích học tập, 
     sinh viên cần có mức xếp loại rèn luyện nào?''',
     '''options''': [
         '''A. Từ Tốt trở lên (>=80 điểm)''',
         '''B. Từ Xuất sắc trở lên (>=90 điểm)''',
         '''C. Từ Trung bình trở lên (>=50 điểm)''',
         '''D. Từ Khá trở lên (>=65 điểm)'''
     ],
     '''correct''': '''D'''},
    {'''question''': '''Các trường thành viên của UEH có tên gì?''',
     '''options''': [
         '''A. Trường Kinh doanh UEH; Trường Kinh tế, Luật và Quản lý nhà nước UEH
         ; và Trường Công nghệ và thiết kế UE''',
         '''B. Trường Kinh doanh UEH; Trường Luật và Quản lý nhà nước UEH;
         và Trường Công nghệ thông minh và thiết kế UEH''',
         '''C. Trường Kinh doanh UEH; Trường Luật''',
         '''D. Trường đời; Trường Kinh doanh UEH; Trường Công nghệ thông minh và tương tác'''
     ],
     '''correct''': '''A'''},
    {'''question''': '''Năm trụ cột chiến lược của UEH bao gồm?''',
     '''options''': [
         '''A. Đào tạo, nghiên cứu, cộng đồng, phát triển nguồn nhân lực và vận hành''',
         '''B. Đào tạo, nghiên cứu, kết nối, phát triển nguồn nhân lực và cộng đồng''',
         '''C. Đào tạo, nghiên cứu, cộng đồng, quản trị, và vận hành''',
         '''D. Đào tạo, kết nối, nghiên cứu, cộng đồng, và vận hành'''
     ],
     '''correct''': '''C'''},

    {'''question''': '''Sứ mạng Tiên phong đổi mới, sáng tạo của UEH là:''',
     '''options''': [
         '''A. Trường đào tạo ra các nhà lãnh đạo và những doanh nhân hàng đầu của Việt Nam''',
         '''B. Đổi mới sáng tạo - Trách nhiệm quốc gia - Phát triển bền vững''',
         '''C. Độc lập, sáng tạo, hiệu quả trong nghiên cứu khoa học''',
         '''D. UEH nhận ra xu hướng thời đại công nghệ thay đổi nhanh chóng và xây dựng lợi thế 
         cạnh tranh thông qua việc không ngừng đổi mới và sáng tạo tri thức trong đào tạo và nghiên cứu khoa học'''
     ],
     '''correct''': '''D'''},

    
    {'''question''': '''UEH được thành lập vào thời gian nào?''',
     '''options''': [
         '''A. 10/1976''',
         '''B. 9/1976''',
         '''C. 11/1976''',
         '''D. 8/1976'''],

     '''correct''': '''A'''},
    
     {
        '''question''': '''Khẩu hiệu của UEH?''',
        '''options''': [
            '''A. Thỏa sức sáng tạo - Chủ động tương lai
            - Toàn diện giá trị''',
            '''B. Kiến thức - Sáng tạo - Thành công''',
            '''C. Đổi mới - Sáng tạo - Phát triển''',
            '''D. Tri thức - Trách nhiệm - Phát triển'''
        ],
        '''correct''': '''A'''
    },

    {
        '''question''': '''Tầm nhìn của UEH?''',
        '''options''': [
            '''A. Trở thành một hệ thống đại học nghiên cứu trong tốp đầu Châu Á,
            nơi hội tụ của khoa học, công nghệ, đổi mới sáng tạo, văn hóa và tri thức Việt Nam''',
            '''B. Đến năm 2030, UEH sẽ trở thành Đại học đa ngành có 
            danh tiếng học thuật trong khu vực Châu Á và phát triển bền vững''',
            '''C. Đến năm 2045 trở thành đại học nghiên cứu và đổi mới sáng tạo,
            đa ngành, đa lĩnh vực, trong nhóm các đại học hàng đầu châu Á và thế giới''',
            '''D. Trở thành đại học theo định hướng nghiên cứu,
            đa ngành, đa lĩnh vực, thuộc nhóm 5 đại học hàng đầu của Việt Nam'''
        ],
        '''correct''': '''B'''
    },

    {
        '''question''': '''Trước ngày 30/4/1975, cơ sở 59C Nguyễn Đình Chiểu,
        Phường Võ Thị Sáu, Quận 3 có tên là?''',
        '''options''': [
            '''A. Trường Đại học Quản lý nhà nước Sài Gòn''',
            '''B. Trường Đại học Kinh tế Sài Gòn''',
            '''C. Trường Đại học Luật khoa Sài Gòn''',
            '''D. Học viện Hành chính quốc gia'''
        ],
        '''correct''': '''C'''
    }
]
def get_hoi(size):
    path = join('''assets''', '''Terrain''', '''hoi2.png''')  # Path to the new sprite image
    image = pygame.image.load(path).convert_alpha()  # Load the sprite with alpha transparency
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Create a new surface for the block
    rect = pygame.Rect(0, 0, size, size)  # Define the area of the sprite
    surface.blit(image, (0, 0), rect)  # Copy the sprite to the surface
    return pygame.transform.scale2x(surface)  # Scale up the sprite for better visibility

# Thêm class MysteryBlock kế thừa từ Block
class MysteryBlock(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        hoi = get_hoi(size)  # Lấy sprite của khối
        self.image.blit(hoi, (0, 0))  # Sao chép sprite vào surface
        self.mask = pygame.mask.from_surface(self.image)  # Tạo mặt nạ va chạm từ sprite
        #self.image = pygame.image.load('''question.png''').convert_alpha()
        #self.image = pygame.transform.scale(self.image, (size, size))
        #self.rect = self.image.get_rect(topleft=(x, y))
        self.answered = False

    def draw(self, win, offset_x):
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# Hàm tạo cấu trúc 1 khối vuông câu hỏi
def create_one_question_block_structure(x, y, block_size, orientation = '''horizontal'''):
    blocks = []
    if orientation == '''question 1''':  # Kiểu nằm ngang
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 2''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y, block_size))
    elif orientation == '''question 3''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y* block_size, block_size))
    elif orientation == '''question 4''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y* block_size, block_size))
    elif orientation == '''question 5''':  # Kiểu dọc
        blocks.append(MysteryBlock(x, y* block_size, block_size))
    else:
        raise ValueError('''Invalid orientation. Choose 'horizontal', 'vertical'.''')
    return blocks  # Trả về danh sách khối


# Hàm xử lý va chạm với block câu hỏi 
def handle_question_block_collision(player, question_blocks, window, used_questions):
    for block in question_blocks:
        if not block.answered:  # Chỉ xử lý nếu block chưa được trả lời
            # Kiểm tra va chạm
            if pygame.sprite.collide_rect(player, block):  # Đơn giản hóa kiểm tra va chạm
                print('''Collision detected!''')  # Debug message
                
                # Chọn câu hỏi ngẫu nhiên từ các câu chưa sử dụng
                available_questions = [q for q in question_bank1 if q not in used_questions]
                if available_questions:
                    question = random.choice(available_questions)
                    
                    # Tạm dừng game và hiển thị overlay câu hỏi
                    is_correct = show_question_dialog(window, question)
                    
                    # Đánh dấu block đã được trả lời và thêm câu hỏi vào danh sách đã sử dụng
                    block.answered = True
                    used_questions.append(question)
                    
                    return is_correct
    return None

# Hàm hiện bảng câu hỏi lên
def show_question_dialog(window, question_data):
    # Tạo overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    
    # Vẽ overlay lên màn hình chính
    window.blit(overlay, (0, 0))
    
    # Kích thước và vị trí dialog
    dialog_width = 1200
    dialog_height = 700
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    
    # Tạo surface cho dialog
    dialog = pygame.Surface((dialog_width, dialog_height))
    dialog.fill((255, 255, 255))
    
    # Font và màu sắc
    try:
        question_font = pygame.font.Font('''Cabin-Italic.ttf''', 36)  # Font cho câu hỏi
        option_font = pygame.font.Font('''Cabin-Variable.ttf''', 32)  # Font cho các lựa chọn
    except:
        print('''Font Cabin not found, using system font''')
        question_font = pygame.font.SysFont('''Arial''', 36)
        option_font = pygame.font.SysFont('''Arial''', 32)
    
    text_color = (0, 0, 0)
    button_color = (0, 200, 0)
    button_hover_color = (0, 255, 0)
    
    # Render câu hỏi với font mới
    # Chia câu hỏi thành nhiều dòng nếu quá dài
    words = question_data['''question'''].split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Kiểm tra độ dài dòng hiện tại
        test_line = ' '.join(current_line)
        if question_font.size(test_line)[0] > dialog_width - 40:  # Trừ lề
            current_line.pop()  # Bỏ từ cuối
            lines.append(' '.join(current_line))  # Thêm dòng hiện tại
            current_line = [word]  # Bắt đầu dòng mới với từ không vừa
    
    if current_line:  # Thêm dòng cuối cùng
        lines.append(' '.join(current_line))
    
    # Render từng dòng câu hỏi
    question_surfaces = []
    total_question_height = 0
    for line in lines:
        text_surface = question_font.render(line, True, text_color)
        question_surfaces.append(text_surface)
        total_question_height += text_surface.get_height() + 10  # 5px spacing
    
    # Tạo các button cho câu trả lời
    button_height = 100
    button_spacing = 50
    buttons = []
    
    # Tính toán vị trí bắt đầu của các button dựa trên chiều cao của câu hỏi
    start_y = total_question_height + 40
    
    for i, option in enumerate(question_data['''options''']):
        button_rect = pygame.Rect(20, start_y + i * (button_height + button_spacing), 
                                dialog_width - 40, button_height)
        buttons.append((button_rect, option))
    
    # Game loop cho dialog
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        relative_mouse_pos = (mouse_pos[0] - dialog_x, mouse_pos[1] - dialog_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button, option in buttons:
                    if button.collidepoint(relative_mouse_pos):
                        answer = option[0]
                        return answer == question_data['''correct''']
        
        # Vẽ dialog và nội dung
        dialog.fill((255, 255, 255))
        
        # Vẽ từng dòng câu hỏi
        current_y = 20
        for text_surface in question_surfaces:
            dialog.blit(text_surface, (20, current_y))
            current_y += text_surface.get_height() + 5
        
        # Vẽ các button
        for button, option in buttons:
            is_hovering = button.collidepoint(relative_mouse_pos)
            color = button_hover_color if is_hovering else button_color
            pygame.draw.rect(dialog, color, button)
            
            # Vẽ text trên button với font Cabin
            option_text = option_font.render(option, True, text_color)
            option_rect = option_text.get_rect(center=button.center)
            dialog.blit(option_text, option_rect)
        
        # Vẽ dialog lên màn hình chính
        window.blit(dialog, (dialog_x, dialog_y))
        pygame.display.update()

# Hàm chính điều khiển game
# Hàm chính điều khiển game
def main2(window):
    class Player(pygame.sprite.Sprite):
        COLOR = (255, 0, 0)  # Màu của nhân vật (không được sử dụng với sprite)
        GRAVITY = 0.8  # Tốc độ rơi
        SPRITES = load_sprite_sheets('''MainCharacters''', '''PinkMan2''', 32, 32, True)  # Tải sprite của nhân vật
        ANIMATION_DELAY = 3  # Độ trễ giữa các khung hình trong animation

        def __init__(self, x, y, width, height):
            super().__init__()  # Gọi constructor của lớp ch
            self.rect = pygame.Rect(x, y, width, height)  # Tạo hình chữ nhật đại diện cho nhân vật
            self.x_vel = 0  # Vận tốc ngang
            self.y_vel = 0  # Vận tốc dọc
            self.mask = None  # Mặt nạ va chạm của nhân vật
            self.direction = '''left'''  # Hướng di chuyển mặc định
            self.animation_count = 0  # Bộ đếm khung hình animation
            self.fall_count = 0  # Bộ đếm trạng thái rơi
            self.jump_count = 0  # Số lần nhảy liên tiếp
            self.hit = False  # Trạng thái bị va chạm
            self.hit_count = 0  # Bộ đếm khi va chạm

        def jump(self):
            self.y_vel = -self.GRAVITY * 8  # Thiết lập vận tốc nhảy
            self.animation_count = 0  # Reset bộ đếm animation
            self.jump_count += 1  # Tăng số lần nhảy
            if self.jump_count == 1:  # Nếu là nhảy lần đầu
                self.fall_count = 0  # Reset trạng thái rơi

        def move(self, dx, dy):
            self.rect.x += dx  # Di chuyển nhân vật theo trục X
            self.rect.y += dy  # Di chuyển nhân vật theo trục Y

        def make_hit(self):
            self.hit = True  # Đặt trạng thái bị va chạm

        def move_left(self, vel):
            self.x_vel = -vel  # Đặt vận tốc sang trái
            if self.direction != '''left''':  # Nếu không phải hướng trái
                self.direction = '''left'''  # Đặt hướng trái
                self.animation_count = 0  # Reset animation

        def move_right(self, vel):
            self.x_vel = vel  # Đặt vận tốc sang phải
            if self.direction != '''right''':  # Nếu không phải hướng phải
                self.direction = '''right'''  # Đặt hướng phải
                self.animation_count = 0  # Reset animation

        def loop(self, fps):
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  # Tăng vận tốc dọc theo trọng lực
            self.move(self.x_vel, self.y_vel)  # Cập nhật vị trí nhân vật
            if self.hit:  # Nếu bị va chạm
                self.hit_count += 1  # Tăng bộ đếm va chạm
            if self.hit_count > fps * 2:  # Sau 2 giây
                self.hit = False  # Hủy trạng thái va chạm
                self.hit_count = 0  # Reset bộ đếm va chạm
            self.fall_count += 1  # Tăng trạng thái rơi
            self.update_sprite()  # Cập nhật sprite hiện tại

        def landed(self):
            self.fall_count = 0  # Reset trạng thái rơi
            self.y_vel = 0  # Dừng vận tốc dọc
            self.jump_count = 0  # Reset số lần nhảy

        def hit_head(self):
            self.count = 0  # Reset trạng thái rơi
            self.y_vel *= -1  # Đảo hướng vận tốc dọc

        def update_sprite(self):
            sprite_sheet = '''idle'''  # Đặt sprite mặc định là đứng yên
            if self.hit:  # Nếu bị va chạm
                sprite_sheet = '''hit'''
            elif self.y_vel < 0:  # Nếu đang nhảy
                if self.jump_count == 1:  # Nếu nhảy 1 lần
                    sprite_sheet = '''jump'''
                elif self.jump_count == 2:  # Nếu nhảy 2 lần
                    sprite_sheet = '''double_jump'''
            elif self.y_vel > self.GRAVITY * 2:  # Nếu đang rơi
                sprite_sheet = '''fall'''
            elif self.x_vel != 0:  # Nếu đang di chuyển
                sprite_sheet = '''run'''
            sprite_sheet_name = sprite_sheet + '''_''' + self.direction  # Thêm hướng di chuyển
            sprites = self.SPRITES[sprite_sheet_name]  # Lấy sprite tương ứng
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Tính khung hình hiện tại
            self.sprite = sprites[sprite_index]  # Đặt sprite hiện tại
            self.animation_count += 1  # Tăng bộ đếm animation

        def update(self):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Cập nhật vị trí chữ nhật đại diện
            self.mask = pygame.mask.from_surface(self.sprite)  # Tạo mặt nạ va chạm từ sprite

        def draw(self, win, offset_x):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Vẽ nhân vật lên màn hình
    
    # Hiển thị menu bắt đầu game
    
    # Play nhạc của vòng
    previous_song = None
    previous_song = play_random_musicbg(previous_song) 

    
    score = 0
    used_questions = []
    game_over = False
    background, bg_image = get_background('''bgtest.jpg''')
    block_size = 96
    player = Player(100, 150, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    
    
    offset_x = 0
    scroll_area_width = 200
    run = True
    game_over = False
    clock = pygame.time.Clock()


    for x in range(0,3):
        if x==3:
            pygame.quit()
            quit()
    # Tạo các khối trong game
    o=17
    three_blocks_horizontal = create_three_block_structure(6040, 400+o, block_size, "horizontal")
    three_blocks_vertical = create_three_block_structure(12300, 200+o, block_size, "vertical")
    three_blocks_L_shape = create_three_block_structure(29050, 400+o, block_size, "L-shape")
    three_blocks_horizontal1 = create_three_block_structure(3100, 100+o, block_size, "horizontal")
    three_blocks_vertical1 = create_three_block_structure(21500, 400+o, block_size, "vertical")
    three_blocks_L_shape1 = create_three_block_structure(15500, 400+o, block_size, "L-shape")
    two_blocks_vertical= create_three_block_structure(800, 400+o, block_size, "2vertical")
    two_blocks_vertical1= create_three_block_structure(800+block_size, 400+o, block_size, "2vertical")
    two_blocks_horizontal= create_three_block_structure(1200, 230+o, block_size, "2horizontal")
    two_blocks_horizontal1= create_three_block_structure(2100, 230+o, block_size, "2horizontal")
    four_blocks_horizontal= create_three_block_structure(18000, 400+o, block_size, "4horizontal")
    four_blocks_vertical = create_three_block_structure(26000, 1300+o, block_size, "4vertical")
    block = create_three_block_structure(500, 497+o, block_size, "block")
    block1 = create_three_block_structure(1800, 390+o, block_size, "block")
    block2 = create_three_block_structure(2500, 400+o, block_size, "block")
    block3 = create_three_block_structure(2800, 250+o, block_size, "block")
    floor = [Block(i * block_size, HEIGHT - block_size+5, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    mystery_block1 = create_three_block_structure(1300, 150+o, block_size, '''question 1''')
    mystery_block2 = create_three_block_structure(200, 500+o, block_size, '''question 2''')
    mystery_block3 = create_three_block_structure(900, 330+o, block_size, '''question 3''')
    mystery_block4 = create_three_block_structure(3300, 20+o, block_size,'''question 4''')
    mystery_block5 = create_three_block_structure(2230, 150+o, block_size,'''question 5''') 
    
# Tạo danh sách objects
    objects = [*floor,
        *[Block(0, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *[Block(5000, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *three_blocks_horizontal,
        *three_blocks_vertical,
        *three_blocks_L_shape,
        *three_blocks_horizontal1,
        *three_blocks_vertical1,
        *three_blocks_L_shape1,
        *two_blocks_horizontal,
        *two_blocks_horizontal1,
        *two_blocks_vertical,
        *four_blocks_horizontal,
        *four_blocks_vertical,
        *block,
        *two_blocks_vertical1,
        *block1,
        *block2,
        *block3,
        *mystery_block5,
        *mystery_block3,
        *mystery_block4,
        *mystery_block2,
        *mystery_block1
    ]

    # Tạo danh sách riêng cho mystery blocks
    mystery_blocks = [*mystery_block1, *mystery_block2, *mystery_block3, *mystery_block4, *mystery_block5]
    
    # Thêm mystery blocks vào danh sách objects
    objects.extend(mystery_blocks)

    offset_x = 0  # Offset trục X
    scroll_area_width = 200  # Khu vực cuộn
    run = True
    game_over = False
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    text_color = (0, 255, 0)

    clock = pygame.time.Clock()
     
    # Random 5 câu hỏi từ ngân hàng câu hỏi
    selected_questions = random.sample(question_bank1, 5)
    used_questions = []
    
    # Font cho hiển thị điểm và thời gian
    font = pygame.font.Font('''Cabin-Variable.ttf''', 36)
    while run:
      # Filter out answered mystery blocks
        objects = [obj for obj in objects if not (isinstance(obj, MysteryBlock) and obj.answered)]
        # Tính toán thời gian còn lại
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Chuyển từ mili giây sang giây
        time_left = max(0, round_time - elapsed_time)  # Đảm bảo thời gian không âm
        
         # Hiển thị điểm và thời gian
        score_text = font.render(f'''Score: {score}/5''', True, (0, 255, 0))
        time_text = font.render(f'''Time: {time_left}s''', True, (0, 255, 0))
        score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
        time_rect = time_text.get_rect(topright=(WIDTH - 20, 60))
        
         
        
        # Vẽ điểm và thời gian
        window.blit(score_text, score_rect)
        window.blit(time_text, time_rect)
        
        pygame.display.update()

         # Nếu hết giờ, thoát game
       
            

        # Cập nhật vị trí camera
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


       # Xử lý va chạm với block câu hỏi
        question_result = handle_question_block_collision(player, mystery_blocks, window, used_questions)
        if question_result is not None:
            if question_result:
                score += 1
                print(f'''Score increased to {score}''')  # Debug message

       

        if time_left == 0:  # Check if the time is up
            print('''Hết giờ!''')
            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()
            
            # # Vẽ các bảng thông báo
            # window.fill((200, 200, 200))  # Background
            # score_board.draw()
            # button_board.draw()
            # pygame.display.flip()
        
            # # Hiện bảng lựa chọn dựa vào điểm số
            # if score>=4:
            #     choice_dialog = ResultInfo(window, has_next_round=True)
            #     window.wait_window(choice_dialog.choice_window)
            
            #     # Xử lý lựa chọn
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
                    
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)  # Khởi động lại màn chơi
            #     elif choice_dialog.choice == "next":
            #         window.destroy()
            #         main3(window)
            # elif score<4:
            #     # Hiển thị thông báo game over
            #     game_over = GameOverDialog(window, score)
            #     window.wait_window(game_over.dialog_window)
            #     game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''

            #     # Hiển thị dialog với 2 nút cho trường hợp thất bại
            #     choice_dialog = ChoiceDialogFail(window)
            #     window.wait_window(choice_dialog.choice_window)
                
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)
                
                # Check if player reaches the x-axis condition
        if player.rect.x > 3500:  # Example condition
            action = trigger_menu(window, '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_win.png''', (WIDTH // 2 - 100, HEIGHT // 2 + 200))
            # if action == '''menu_map''':
            #     map_action = menu_map(window, '''assets/Background/z6105275572936_31db720c63d3dafccde4dd83d4772e28.jpg''', (WIDTH // 2 - 125, HEIGHT // 2 - 100))
            #     if map_action == '''return_to_main''':
            return  # Exit `main` and restart the game loop
        clock.tick(FPS)  # Giới hạn FPS
        for event in pygame.event.get():  # Xử lý sự kiện
            if event.type == pygame.QUIT:
                run = False
                break
            if not game_over and event.type == pygame.KEYDOWN:  # Nếu nhấn SPACE
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if game_over:  # Xử lý màn hình Game Over
            game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''
            game_over_image = pygame.image.load(game_over_image_path).convert_alpha()
            game_over_image = pygame.transform.scale(game_over_image, (400, 300))
            window.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render('''GAME OVER''', True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
            image_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            button_width, button_height = 200, 50
            button_color = (0, 200, 0)
            button_hover_color = (0, 255, 0)
            button_text_color = (255, 255, 255)
            button_font = pygame.font.Font(None, 36)
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 200, button_width, button_height)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(pygame.mouse.get_pos()):
                            return
                window.fill((0, 0, 0))
                window.blit(game_over_image, image_rect)
                window.blit(text, text_rect)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
                current_button_color = button_hover_color if is_hovering else button_color
                pygame.draw.rect(window, current_button_color, button_rect)
                button_text = button_font.render('''Restart''', True, button_text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                window.blit(button_text, button_text_rect)
                pygame.display.update()
            # Hiển thị thông báo game over
            print('''Trò chơi kết thúc''')
        

            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()   

        player.loop(FPS)  # Cập nhật trạng thái nhân vật
        fire.loop()  # Cập nhật trạng thái bẫy lửa
        handle_move(player, objects)  # Xử lý di chuyển

        if player.rect.top > HEIGHT or player.rect.bottom < -100:  # Kiểm tra rơi khỏi màn hình
            game_over = True
            continue
        draw(window, background, bg_image, player, objects, offset_x)  # Vẽ tất cả đối tượng
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    pygame.quit()
    quit()
def main(window):
    class Player(pygame.sprite.Sprite):
        COLOR = (255, 0, 0)  # Màu của nhân vật (không được sử dụng với sprite)
        GRAVITY = 0.8  # Tốc độ rơi
        SPRITES = load_sprite_sheets('''MainCharacters''', '''MaskDude1''', 32, 32, True)  # Tải sprite của nhân vật
        ANIMATION_DELAY = 3  # Độ trễ giữa các khung hình trong animation

        def __init__(self, x, y, width, height):
            super().__init__()  # Gọi constructor của lớp ch
            self.rect = pygame.Rect(x, y, width, height)  # Tạo hình chữ nhật đại diện cho nhân vật
            self.x_vel = 0  # Vận tốc ngang
            self.y_vel = 0  # Vận tốc dọc
            self.mask = None  # Mặt nạ va chạm của nhân vật
            self.direction = '''left'''  # Hướng di chuyển mặc định
            self.animation_count = 0  # Bộ đếm khung hình animation
            self.fall_count = 0  # Bộ đếm trạng thái rơi
            self.jump_count = 0  # Số lần nhảy liên tiếp
            self.hit = False  # Trạng thái bị va chạm
            self.hit_count = 0  # Bộ đếm khi va chạm

        def jump(self):
            self.y_vel = -self.GRAVITY * 8  # Thiết lập vận tốc nhảy
            self.animation_count = 0  # Reset bộ đếm animation
            self.jump_count += 1  # Tăng số lần nhảy
            if self.jump_count == 1:  # Nếu là nhảy lần đầu
                self.fall_count = 0  # Reset trạng thái rơi

        def move(self, dx, dy):
            self.rect.x += dx  # Di chuyển nhân vật theo trục X
            self.rect.y += dy  # Di chuyển nhân vật theo trục Y

        def make_hit(self):
            self.hit = True  # Đặt trạng thái bị va chạm

        def move_left(self, vel):
            self.x_vel = -vel  # Đặt vận tốc sang trái
            if self.direction != '''left''':  # Nếu không phải hướng trái
                self.direction = '''left'''  # Đặt hướng trái
                self.animation_count = 0  # Reset animation

        def move_right(self, vel):
            self.x_vel = vel  # Đặt vận tốc sang phải
            if self.direction != '''right''':  # Nếu không phải hướng phải
                self.direction = '''right'''  # Đặt hướng phải
                self.animation_count = 0  # Reset animation

        def loop(self, fps):
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  # Tăng vận tốc dọc theo trọng lực
            self.move(self.x_vel, self.y_vel)  # Cập nhật vị trí nhân vật
            if self.hit:  # Nếu bị va chạm
                self.hit_count += 1  # Tăng bộ đếm va chạm
            if self.hit_count > fps * 2:  # Sau 2 giây
                self.hit = False  # Hủy trạng thái va chạm
                self.hit_count = 0  # Reset bộ đếm va chạm
            self.fall_count += 1  # Tăng trạng thái rơi
            self.update_sprite()  # Cập nhật sprite hiện tại

        def landed(self):
            self.fall_count = 0  # Reset trạng thái rơi
            self.y_vel = 0  # Dừng vận tốc dọc
            self.jump_count = 0  # Reset số lần nhảy

        def hit_head(self):
            self.count = 0  # Reset trạng thái rơi
            self.y_vel *= -1  # Đảo hướng vận tốc dọc

        def update_sprite(self):
            sprite_sheet = '''idle'''  # Đặt sprite mặc định là đứng yên
            if self.hit:  # Nếu bị va chạm
                sprite_sheet = '''hit'''
            elif self.y_vel < 0:  # Nếu đang nhảy
                if self.jump_count == 1:  # Nếu nhảy 1 lần
                    sprite_sheet = '''jump'''
                elif self.jump_count == 2:  # Nếu nhảy 2 lần
                    sprite_sheet = '''double_jump'''
            elif self.y_vel > self.GRAVITY * 3:  # Nếu đang rơi
                sprite_sheet = '''fall'''
            elif self.x_vel != 0:  # Nếu đang di chuyển
                sprite_sheet = '''run'''
            sprite_sheet_name = sprite_sheet + '''_''' + self.direction  # Thêm hướng di chuyển
            sprites = self.SPRITES[sprite_sheet_name]  # Lấy sprite tương ứng
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Tính khung hình hiện tại
            self.sprite = sprites[sprite_index]  # Đặt sprite hiện tại
            self.animation_count += 1  # Tăng bộ đếm animation

        def update(self):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Cập nhật vị trí chữ nhật đại diện
            self.mask = pygame.mask.from_surface(self.sprite)  # Tạo mặt nạ va chạm từ sprite

        def draw(self, win, offset_x):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Vẽ nhân vật lên màn hình
    # Hiển thị menu bắt đầu game
    
    # Play nhạc của vòng
    previous_song = None
    previous_song = play_random_musicbg(previous_song) 

    
    score = 0
    used_questions = []
    game_over = False
    background, bg_image = get_background('''bgtest.jpg''')
    block_size = 96
    player = Player(100, 150, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    
    
    offset_x = 0
    scroll_area_width = 200
    run = True
    game_over = False
    clock = pygame.time.Clock()


    for x in range(0,3):
        if x==3:
            pygame.quit()
            quit()
    # Tạo các khối trong game
    o=17
    three_blocks_horizontal = create_three_block_structure(600, 400+o, block_size, '''horizontal''')
    three_blocks_vertical = create_three_block_structure(12300, 200+o, block_size, '''vertical''')
    three_blocks_L_shape = create_three_block_structure(29500, 400+o, block_size, '''L-shape''')
    three_blocks_horizontal1 = create_three_block_structure(20000, 500+o, block_size, '''horizontal''')
    three_blocks_vertical1 = create_three_block_structure(21000, 400+o, block_size, '''vertical''')
    three_blocks_L_shape1 = create_three_block_structure(1500, 400+o, block_size, '''L-shape''')
    two_blocks_vertical= create_three_block_structure(1200, 400+o, block_size, '''2vertical''')
    two_blocks_vertical1= create_three_block_structure(2100, 390+o, block_size, '''2vertical''')
    two_blocks_horizontal= create_three_block_structure(2500, 400+o, block_size, '''2horizontal''')
    four_blocks_horizontal= create_three_block_structure(18000, 400+o, block_size, '''4horizontal''')
    four_blocks_vertical = create_three_block_structure(26000, 1300+o, block_size, '''4vertical''')
    block = create_three_block_structure(400, 497+o, block_size, '''block''')
    block1 = create_three_block_structure(18000, 390+o, block_size, "block")
    block2 = create_three_block_structure(25000, 400+o, block_size, "block")
    block3 = create_three_block_structure(28000, 250+o, block_size, "block")
    mystery_block1 = create_three_block_structure(1300, 300+o, block_size, '''question 1''')
    mystery_block2 = create_three_block_structure(200, 500+o, block_size, '''question 2''')
    mystery_block3 = create_three_block_structure(900, 330+o, block_size, '''question 3''')
    mystery_block4 = create_three_block_structure(2130, 320+o, block_size,'''question 4''')
    mystery_block5 = create_three_block_structure(2530, 300+o, block_size,'''question 5''') 
    two_blocks_horizontal1= create_three_block_structure(21000, 230+o, block_size, "2horizontal")    
    floor = [Block(i * block_size, HEIGHT - block_size+5, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
   
# Tạo danh sách objects
    objects = [*floor,
        *[Block(0, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *[Block(3000, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *three_blocks_horizontal,
        *three_blocks_vertical,
        *three_blocks_L_shape,
        *three_blocks_horizontal1,
        *three_blocks_vertical1,
        *three_blocks_L_shape1,
        *two_blocks_horizontal,
        *two_blocks_horizontal1,
        *two_blocks_vertical,
        *four_blocks_horizontal,
        *four_blocks_vertical,
        *block,
        *two_blocks_vertical1,
        *block1,
        *block2,
        *block3,
        *mystery_block5,
        *mystery_block3,
        *mystery_block4,
        *mystery_block2,
        *mystery_block1
    ]

    # Tạo danh sách riêng cho mystery blocks
    mystery_blocks = [*mystery_block1, *mystery_block2, *mystery_block3, *mystery_block4, *mystery_block5]
    
    # Thêm mystery blocks vào danh sách objects
    objects.extend(mystery_blocks)

    offset_x = 0  # Offset trục X
    scroll_area_width = 200  # Khu vực cuộn
    run = True
    game_over = False
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    text_color = (0, 255, 0)

    clock = pygame.time.Clock()
     
    # Random 5 câu hỏi từ ngân hàng câu hỏi
    selected_questions = random.sample(question_bank1, 5)
    used_questions = []
    
    # Font cho hiển thị điểm và thời gian
    font = pygame.font.Font('''Cabin-Variable.ttf''', 36)
    while run:
      # Filter out answered mystery blocks
        objects = [obj for obj in objects if not (isinstance(obj, MysteryBlock) and obj.answered)]
        # Tính toán thời gian còn lại
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Chuyển từ mili giây sang giây
        time_left = max(0, round_time - elapsed_time)  # Đảm bảo thời gian không âm
        
         # Hiển thị điểm và thời gian
        score_text = font.render(f'''Score: {score}/5''', True, (0, 255, 0))
        time_text = font.render(f'''Time: {time_left}s''', True, (0, 255, 0))
        score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
        time_rect = time_text.get_rect(topright=(WIDTH - 20, 60))
        
         
        
        # Vẽ điểm và thời gian
        window.blit(score_text, score_rect)
        window.blit(time_text, time_rect)
        
        pygame.display.update()

         # Nếu hết giờ, thoát game
       
            

        # Cập nhật vị trí camera
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


       # Xử lý va chạm với block câu hỏi
        question_result = handle_question_block_collision(player, mystery_blocks, window, used_questions)
        if question_result is not None:
            if question_result:
                score += 1
                print(f'''Score increased to {score}''')  # Debug message

       

        if time_left == 0:  # Check if the time is up
            print('''Hết giờ!''')
            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()
            
            # # Vẽ các bảng thông báo
            # window.fill((200, 200, 200))  # Background
            # score_board.draw()
            # button_board.draw()
            # pygame.display.flip()
        
            # # Hiện bảng lựa chọn dựa vào điểm số
            # if score>=4:
            #     choice_dialog = ResultInfo(window, has_next_round=True)
            #     window.wait_window(choice_dialog.choice_window)
            
            #     # Xử lý lựa chọn
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
                    
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)  # Khởi động lại màn chơi
            #     elif choice_dialog.choice == "next":
            #         window.destroy()
            #         main3(window)
            # elif score<4:
            #     # Hiển thị thông báo game over
            #     game_over = GameOverDialog(window, score)
            #     window.wait_window(game_over.dialog_window)
            #     game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''

            #     # Hiển thị dialog với 2 nút cho trường hợp thất bại
            #     choice_dialog = ChoiceDialogFail(window)
            #     window.wait_window(choice_dialog.choice_window)
                
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)
                
                # Check if player reaches the x-axis condition
        if player.rect.x > 3500:  # Example condition
            action = trigger_menu(window, '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_win.png''', (WIDTH // 2 - 100, HEIGHT // 2 + 200))
            # if action == '''menu_map''':
            #     map_action = menu_map(window, '''assets/Background/z6105275572936_31db720c63d3dafccde4dd83d4772e28.jpg''', (WIDTH // 2 - 125, HEIGHT // 2 - 100))
            #     if map_action == '''return_to_main''':
            return  # Exit `main` and restart the game loop
        clock.tick(FPS)  # Giới hạn FPS
        for event in pygame.event.get():  # Xử lý sự kiện
            if event.type == pygame.QUIT:
                run = False
                break
            if not game_over and event.type == pygame.KEYDOWN:  # Nếu nhấn SPACE
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if game_over:  # Xử lý màn hình Game Over
            game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''
            game_over_image = pygame.image.load(game_over_image_path).convert_alpha()
            game_over_image = pygame.transform.scale(game_over_image, (400, 300))
            window.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render('''GAME OVER''', True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
            image_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            button_width, button_height = 200, 50
            button_color = (0, 200, 0)
            button_hover_color = (0, 255, 0)
            button_text_color = (255, 255, 255)
            button_font = pygame.font.Font(None, 36)
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 200, button_width, button_height)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(pygame.mouse.get_pos()):
                            return
                window.fill((0, 0, 0))
                window.blit(game_over_image, image_rect)
                window.blit(text, text_rect)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
                current_button_color = button_hover_color if is_hovering else button_color
                pygame.draw.rect(window, current_button_color, button_rect)
                button_text = button_font.render('''Restart''', True, button_text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                window.blit(button_text, button_text_rect)
                pygame.display.update()
            # Hiển thị thông báo game over
            print('''Trò chơi kết thúc''')
        

            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()   

        player.loop(FPS)  # Cập nhật trạng thái nhân vật
        fire.loop()  # Cập nhật trạng thái bẫy lửa
        handle_move(player, objects)  # Xử lý di chuyển

        if player.rect.top > HEIGHT or player.rect.bottom < -100:  # Kiểm tra rơi khỏi màn hình
            game_over = True
            continue
        draw(window, background, bg_image, player, objects, offset_x)  # Vẽ tất cả đối tượng
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    pygame.quit()
    quit()
def main3(window):
    class Player(pygame.sprite.Sprite):
        COLOR = (255, 0, 0)  # Màu của nhân vật (không được sử dụng với sprite)
        GRAVITY = 0.8  # Tốc độ rơi
        SPRITES = load_sprite_sheets('''MainCharacters''', '''NinjaFrog3''', 32, 32, True)  # Tải sprite của nhân vật
        ANIMATION_DELAY = 3  # Độ trễ giữa các khung hình trong animation

        def __init__(self, x, y, width, height):
            super().__init__()  # Gọi constructor của lớp ch
            self.rect = pygame.Rect(x, y, width, height)  # Tạo hình chữ nhật đại diện cho nhân vật
            self.x_vel = 0  # Vận tốc ngang
            self.y_vel = 0  # Vận tốc dọc
            self.mask = None  # Mặt nạ va chạm của nhân vật
            self.direction = '''left'''  # Hướng di chuyển mặc định
            self.animation_count = 0  # Bộ đếm khung hình animation
            self.fall_count = 0  # Bộ đếm trạng thái rơi
            self.jump_count = 0  # Số lần nhảy liên tiếp
            self.hit = False  # Trạng thái bị va chạm
            self.hit_count = 0  # Bộ đếm khi va chạm

        def jump(self):
            self.y_vel = -self.GRAVITY * 8  # Thiết lập vận tốc nhảy
            self.animation_count = 0  # Reset bộ đếm animation
            self.jump_count += 1  # Tăng số lần nhảy
            if self.jump_count == 1:  # Nếu là nhảy lần đầu
                self.fall_count = 0  # Reset trạng thái rơi

        def move(self, dx, dy):
            self.rect.x += dx  # Di chuyển nhân vật theo trục X
            self.rect.y += dy  # Di chuyển nhân vật theo trục Y

        def make_hit(self):
            self.hit = True  # Đặt trạng thái bị va chạm

        def move_left(self, vel):
            self.x_vel = -vel  # Đặt vận tốc sang trái
            if self.direction != '''left''':  # Nếu không phải hướng trái
                self.direction = '''left'''  # Đặt hướng trái
                self.animation_count = 0  # Reset animation

        def move_right(self, vel):
            self.x_vel = vel  # Đặt vận tốc sang phải
            if self.direction != '''right''':  # Nếu không phải hướng phải
                self.direction = '''right'''  # Đặt hướng phải
                self.animation_count = 0  # Reset animation

        def loop(self, fps):
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  # Tăng vận tốc dọc theo trọng lực
            self.move(self.x_vel, self.y_vel)  # Cập nhật vị trí nhân vật
            if self.hit:  # Nếu bị va chạm
                self.hit_count += 1  # Tăng bộ đếm va chạm
            if self.hit_count > fps * 2:  # Sau 2 giây
                self.hit = False  # Hủy trạng thái va chạm
                self.hit_count = 0  # Reset bộ đếm va chạm
            self.fall_count += 1  # Tăng trạng thái rơi
            self.update_sprite()  # Cập nhật sprite hiện tại

        def landed(self):
            self.fall_count = 0  # Reset trạng thái rơi
            self.y_vel = 0  # Dừng vận tốc dọc
            self.jump_count = 0  # Reset số lần nhảy

        def hit_head(self):
            self.count = 0  # Reset trạng thái rơi
            self.y_vel *= -1  # Đảo hướng vận tốc dọc

        def update_sprite(self):
            sprite_sheet = '''idle'''  # Đặt sprite mặc định là đứng yên
            if self.hit:  # Nếu bị va chạm
                sprite_sheet = '''hit'''
            elif self.y_vel < 0:  # Nếu đang nhảy
                if self.jump_count == 1:  # Nếu nhảy 1 lần
                    sprite_sheet = '''jump'''
                elif self.jump_count == 2:  # Nếu nhảy 2 lần
                    sprite_sheet = '''double_jump'''
            elif self.y_vel > self.GRAVITY * 2:  # Nếu đang rơi
                sprite_sheet = '''fall'''
            elif self.x_vel != 0:  # Nếu đang di chuyển
                sprite_sheet = '''run'''
            sprite_sheet_name = sprite_sheet + '''_''' + self.direction  # Thêm hướng di chuyển
            sprites = self.SPRITES[sprite_sheet_name]  # Lấy sprite tương ứng
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Tính khung hình hiện tại
            self.sprite = sprites[sprite_index]  # Đặt sprite hiện tại
            self.animation_count += 1  # Tăng bộ đếm animation

        def update(self):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Cập nhật vị trí chữ nhật đại diện
            self.mask = pygame.mask.from_surface(self.sprite)  # Tạo mặt nạ va chạm từ sprite

        def draw(self, win, offset_x):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Vẽ nhân vật lên màn hình
    # Hiển thị menu bắt đầu game
    
    # Play nhạc của vòng
    previous_song = None
    previous_song = play_random_musicbg(previous_song) 

    
    score = 0
    used_questions = []
    game_over = False
    background, bg_image = get_background('''bgtest.jpg''')
    block_size = 96
    player = Player(100, 150, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    
    
    offset_x = 0
    scroll_area_width = 200
    run = True
    game_over = False
    clock = pygame.time.Clock()


    for x in range(0,3):
        if x==3:
            pygame.quit()
            quit()
    # Tạo các khối trong game
    o=17
    three_blocks_horizontal = create_three_block_structure(1800, 680+o, block_size, '''horizontal''')
    three_blocks_vertical = create_three_block_structure(12300, 200+o, block_size, '''vertical''')
    three_blocks_L_shape = create_three_block_structure(1080, 330+o, block_size, '''L-shape''')#1030,270
    three_blocks_L_shape1 = create_three_block_structure(2250, 500+o, block_size, '''L-shape''')
    three_blocks_horizontal1 = create_three_block_structure(20000, 500+o, block_size, '''horizontal''')
    three_blocks_vertical1 = create_three_block_structure(1300, 780+o, block_size, '''vertical''')
    two_blocks_vertical= create_three_block_structure(12000, 400+o, block_size, '''2vertical''')
    two_blocks_vertical1= create_three_block_structure(21000, 390+o, block_size, '''2vertical''')
    two_blocks_horizontal= create_three_block_structure(2700, 300+o, block_size, '''2horizontal''')
    four_blocks_horizontal= create_three_block_structure(18000, 400+o, block_size, '''4horizontal''')
    four_blocks_vertical = create_three_block_structure(26000, 1300+o, block_size, '''4vertical''')
    block = create_three_block_structure(700, 497+o, block_size, '''block''')
    block1 = create_three_block_structure(18000, 390+o, block_size, "block")
    block2 = create_three_block_structure(20500, 400+o, block_size, "block")
    block3 = create_three_block_structure(28000, 250+o, block_size, "block")
    floor = [Block(i * block_size, HEIGHT - block_size+5, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    mystery_block1 = create_three_block_structure(400, 500+o, block_size, '''question 1''')
    mystery_block2 = create_three_block_structure(1800, 600+o, block_size, '''question 2''')
    mystery_block3 = create_three_block_structure(1180, 150+o, block_size, '''question 3''')
    mystery_block4 = create_three_block_structure(2380, 300+o, block_size,'''question 4''')
    mystery_block5 = create_three_block_structure(2800, 150+o, block_size,'''question 5''') 
    two_blocks_horizontal1= create_three_block_structure(21000, 230+o, block_size, "2horizontal")    
       
# Tạo danh sách objects
    objects = [
        *[Block(0, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *[Block(5000, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *three_blocks_horizontal,
        *three_blocks_vertical,
        *three_blocks_L_shape,
        *three_blocks_horizontal1,
        *three_blocks_vertical1,
        *three_blocks_L_shape1,
        *two_blocks_horizontal,
        *two_blocks_horizontal1,
        *two_blocks_vertical,
        *four_blocks_horizontal,
        *four_blocks_vertical,
        *block,
        *two_blocks_vertical1,
        *block1,
        *block2,
        *block3,
        *mystery_block5,
        *mystery_block3,
        *mystery_block4,
        *mystery_block2,
        *mystery_block1
    ]

    # Tạo danh sách riêng cho mystery blocks
    mystery_blocks = [*mystery_block1, *mystery_block2, *mystery_block3, *mystery_block4, *mystery_block5]
    
    # Thêm mystery blocks vào danh sách objects
    objects.extend(mystery_blocks)

    offset_x = 0  # Offset trục X
    scroll_area_width = 200  # Khu vực cuộn
    run = True
    game_over = False
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    text_color = (0, 255, 0)

    clock = pygame.time.Clock()
     
    # Random 5 câu hỏi từ ngân hàng câu hỏi
    selected_questions = random.sample(question_bank1, 5)
    used_questions = []
    
    # Font cho hiển thị điểm và thời gian
    font = pygame.font.Font('''Cabin-Variable.ttf''', 36)
    while run:
      # Filter out answered mystery blocks
        objects = [obj for obj in objects if not (isinstance(obj, MysteryBlock) and obj.answered)]
        # Tính toán thời gian còn lại
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Chuyển từ mili giây sang giây
        time_left = max(0, round_time - elapsed_time)  # Đảm bảo thời gian không âm
        
         # Hiển thị điểm và thời gian
        score_text = font.render(f'''Score: {score}/5''', True, (0, 255, 0))
        time_text = font.render(f'''Time: {time_left}s''', True, (0, 255, 0))
        score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
        time_rect = time_text.get_rect(topright=(WIDTH - 20, 60))
        
         
        
        # Vẽ điểm và thời gian
        window.blit(score_text, score_rect)
        window.blit(time_text, time_rect)
        
        pygame.display.update()

         # Nếu hết giờ, thoát game
       
            

        # Cập nhật vị trí camera
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


       # Xử lý va chạm với block câu hỏi
        question_result = handle_question_block_collision(player, mystery_blocks, window, used_questions)
        if question_result is not None:
            if question_result:
                score += 1
                print(f'''Score increased to {score}''')  # Debug message

       

        if time_left == 0:  # Check if the time is up
            print('''Hết giờ!''')
            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()
            
            # # Vẽ các bảng thông báo
            # window.fill((200, 200, 200))  # Background
            # score_board.draw()
            # button_board.draw()
            # pygame.display.flip()
        
            # # Hiện bảng lựa chọn dựa vào điểm số
            # if score>=4:
            #     choice_dialog = ResultInfo(window, has_next_round=True)
            #     window.wait_window(choice_dialog.choice_window)
            
            #     # Xử lý lựa chọn
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
                    
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)  # Khởi động lại màn chơi
            #     elif choice_dialog.choice == "next":
            #         window.destroy()
            #         main3(window)
            # elif score<4:
            #     # Hiển thị thông báo game over
            #     game_over = GameOverDialog(window, score)
            #     window.wait_window(game_over.dialog_window)
            #     game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''

            #     # Hiển thị dialog với 2 nút cho trường hợp thất bại
            #     choice_dialog = ChoiceDialogFail(window)
            #     window.wait_window(choice_dialog.choice_window)
                
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)
                
                # Check if player reaches the x-axis condition
        if player.rect.x > 3500:  # Example condition
            action = trigger_menu(window, '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_win.png''', (WIDTH // 2 - 100, HEIGHT // 2 + 200))
            # if action == '''menu_map''':
            #     map_action = menu_map(window, '''assets/Background/z6105275572936_31db720c63d3dafccde4dd83d4772e28.jpg''', (WIDTH // 2 - 125, HEIGHT // 2 - 100))
            #     if map_action == '''return_to_main''':
            return  # Exit `main` and restart the game loop
        clock.tick(FPS)  # Giới hạn FPS
        for event in pygame.event.get():  # Xử lý sự kiện
            if event.type == pygame.QUIT:
                run = False
                break
            if not game_over and event.type == pygame.KEYDOWN:  # Nếu nhấn SPACE
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if game_over:  # Xử lý màn hình Game Over
            game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''
            game_over_image = pygame.image.load(game_over_image_path).convert_alpha()
            game_over_image = pygame.transform.scale(game_over_image, (400, 300))
            window.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render('''GAME OVER''', True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
            image_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            button_width, button_height = 200, 50
            button_color = (0, 200, 0)
            button_hover_color = (0, 255, 0)
            button_text_color = (255, 255, 255)
            button_font = pygame.font.Font(None, 36)
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 200, button_width, button_height)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(pygame.mouse.get_pos()):
                            return
                window.fill((0, 0, 0))
                window.blit(game_over_image, image_rect)
                window.blit(text, text_rect)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
                current_button_color = button_hover_color if is_hovering else button_color
                pygame.draw.rect(window, current_button_color, button_rect)
                button_text = button_font.render('''Restart''', True, button_text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                window.blit(button_text, button_text_rect)
                pygame.display.update()
            # Hiển thị thông báo game over
            print('''Trò chơi kết thúc''')
        

            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()   

        player.loop(FPS)  # Cập nhật trạng thái nhân vật
        fire.loop()  # Cập nhật trạng thái bẫy lửa
        handle_move(player, objects)  # Xử lý di chuyển

        if player.rect.top > HEIGHT or player.rect.bottom < -100:  # Kiểm tra rơi khỏi màn hình
            game_over = True
            continue
        draw(window, background, bg_image, player, objects, offset_x)  # Vẽ tất cả đối tượng
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    pygame.quit()
    quit()
def main4(window):
    class Player(pygame.sprite.Sprite):
        COLOR = (255, 0, 0)  # Màu của nhân vật (không được sử dụng với sprite)
        GRAVITY = 0.8  # Tốc độ rơi
        SPRITES = load_sprite_sheets('''MainCharacters''', '''VirtualGuy4''', 32, 32, True)  # Tải sprite của nhân vật
        ANIMATION_DELAY = 3  # Độ trễ giữa các khung hình trong animation

        def __init__(self, x, y, width, height):
            super().__init__()  # Gọi constructor của lớp ch
            self.rect = pygame.Rect(x, y, width, height)  # Tạo hình chữ nhật đại diện cho nhân vật
            self.x_vel =0  # Vận tốc ngang
            self.y_vel =0  # Vận tốc dọc
            self.mask = None  # Mặt nạ va chạm của nhân vật
            self.direction = '''left'''  # Hướng di chuyển mặc định
            self.animation_count = 0  # Bộ đếm khung hình animation
            self.fall_count = 0  # Bộ đếm trạng thái rơi
            self.jump_count = 0  # Số lần nhảy liên tiếp
            self.hit = False  # Trạng thái bị va chạm
            self.hit_count = 0  # Bộ đếm khi va chạm

        def jump(self):
            self.y_vel = -self.GRAVITY * 8  # Thiết lập vận tốc nhảy
            self.animation_count = 0  # Reset bộ đếm animation
            self.jump_count += 1  # Tăng số lần nhảy
            if self.jump_count == 1:  # Nếu là nhảy lần đầu
                self.fall_count = 0  # Reset trạng thái rơi

        def move(self, dx, dy):
            self.rect.x += dx*3  # Di chuyển nhân vật theo trục X
            self.rect.y += dy  # Di chuyển nhân vật theo trục Y

        def make_hit(self):
            self.hit = True  # Đặt trạng thái bị va chạm

        def move_left(self, vel):
            self.x_vel = -vel  # Đặt vận tốc sang trái
            if self.direction != '''left''':  # Nếu không phải hướng trái
                self.direction = '''left'''  # Đặt hướng trái
                self.animation_count = 0  # Reset animation

        def move_right(self, vel):
            self.x_vel = vel  # Đặt vận tốc sang phải
            if self.direction != '''right''':  # Nếu không phải hướng phải
                self.direction = '''right'''  # Đặt hướng phải
                self.animation_count = 0  # Reset animation

        def loop(self, fps):
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)  # Tăng vận tốc dọc theo trọng lực
            self.move(self.x_vel, self.y_vel)  # Cập nhật vị trí nhân vật
            if self.hit:  # Nếu bị va chạm
                self.hit_count += 1  # Tăng bộ đếm va chạm
            if self.hit_count > fps * 2:  # Sau 2 giây
                self.hit = False  # Hủy trạng thái va chạm
                self.hit_count = 0  # Reset bộ đếm va chạm
            self.fall_count += 1  # Tăng trạng thái rơi
            self.update_sprite()  # Cập nhật sprite hiện tại

        def landed(self):
            self.fall_count = 0  # Reset trạng thái rơi
            self.y_vel = 0  # Dừng vận tốc dọc
            self.jump_count = 0  # Reset số lần nhảy

        def hit_head(self):
            self.count = 0  # Reset trạng thái rơi
            self.y_vel *= -1  # Đảo hướng vận tốc dọc

        def update_sprite(self):
            sprite_sheet = '''idle'''  # Đặt sprite mặc định là đứng yên
            if self.hit:  # Nếu bị va chạm
                sprite_sheet = '''hit'''
            elif self.y_vel < 0:  # Nếu đang nhảy
                if self.jump_count == 1:  # Nếu nhảy 1 lần
                    sprite_sheet = '''jump'''
                elif self.jump_count == 2:  # Nếu nhảy 2 lần
                    sprite_sheet = '''double_jump'''
            elif self.y_vel > self.GRAVITY * 2:  # Nếu đang rơi
                sprite_sheet = '''fall'''
            elif self.x_vel != 0:  # Nếu đang di chuyển
                sprite_sheet = '''run'''
            sprite_sheet_name = sprite_sheet + '''_''' + self.direction  # Thêm hướng di chuyển
            sprites = self.SPRITES[sprite_sheet_name]  # Lấy sprite tương ứng
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Tính khung hình hiện tại
            self.sprite = sprites[sprite_index]  # Đặt sprite hiện tại
            self.animation_count += 1  # Tăng bộ đếm animation

        def update(self):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Cập nhật vị trí chữ nhật đại diện
            self.mask = pygame.mask.from_surface(self.sprite)  # Tạo mặt nạ va chạm từ sprite

        def draw(self, win, offset_x):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Vẽ nhân vật lên màn hình
    # Hiển thị menu bắt đầu game
    
    # Play nhạc của vòng
    previous_song = None
    previous_song = play_random_musicbg(previous_song) 

    
    score = 0
    used_questions = []
    game_over = False
    background, bg_image = get_background('''bgtest.jpg''')
    block_size = 96
    player = Player(100, 150, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    
    
    offset_x = 0
    scroll_area_width = 200
    run = True
    game_over = False
    clock = pygame.time.Clock()


    for x in range(0,3):
        if x==3:
            pygame.quit()
            quit()
    # Tạo các khối trong game
    o=17
    three_blocks_horizontal = create_three_block_structure(4300, 450+o, block_size, '''horizontal''')
    three_blocks_vertical = create_three_block_structure(12300, 200+o, block_size, '''vertical''')
    three_blocks_L_shape = create_three_block_structure(29500, 400+o, block_size, '''L-shape''')
    three_blocks_horizontal1 = create_three_block_structure(20000, 500+o, block_size, '''horizontal''')
    three_blocks_vertical1 = create_three_block_structure(9070, 100+o, block_size, '''vertical''')
    three_blocks_L_shape1 = create_three_block_structure(15000, 400+o, block_size, '''L-shape''')
    two_blocks_vertical= create_three_block_structure(900, 200+o, block_size, '''2vertical''')
    two_blocks_vertical1= create_three_block_structure(21000, 390+o, block_size, '''2vertical''')
    two_blocks_horizontal= create_three_block_structure(25000, 400+o, block_size, '''2horizontal''')
    four_blocks_horizontal= create_three_block_structure(18000, 400+o, block_size, '''4horizontal''')
    four_blocks_vertical = create_three_block_structure(26000, 1300+o, block_size, '''4vertical''')
    block = create_three_block_structure(600, 497+o, block_size, '''block''')
    block1 = create_three_block_structure(1900, 497+o, block_size, '''block''')
    block2 = create_three_block_structure(3300, 497+o, block_size, '''block''')
    block3 = create_three_block_structure(5800, 450+o, block_size/2, "block")
    floor = [Block(i * block_size, HEIGHT - block_size+5, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    mystery_block1 = create_three_block_structure(700, 450+o, block_size, '''question 1''')
    mystery_block2 = create_three_block_structure(2000, 450+o, block_size, '''question 2''')
    mystery_block3 = create_three_block_structure(3400, 450+o, block_size, '''question 3''')
    mystery_block4 = create_three_block_structure(4400, 300+o, block_size,'''question 4''')
    mystery_block5 = create_three_block_structure(5860, 350+o, block_size,'''question 5''') 
    two_blocks_horizontal1= create_three_block_structure(21000, 230+o, block_size, "2horizontal")
    floor = [Block(i * block_size, 50, block_size) for i in range(0, (WIDTH * 3) // block_size)]
 
# Tạo danh sách objects
    objects = [*floor,
        *[Block(0, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *[Block(6300, h * block_size -64, block_size) for h in range(0, HEIGHT)],
        *three_blocks_horizontal,
        *three_blocks_vertical,
        *three_blocks_L_shape,
        *three_blocks_horizontal1,
        *three_blocks_vertical1,
        *three_blocks_L_shape1,
        *two_blocks_horizontal,
        *two_blocks_horizontal1,
        *two_blocks_vertical,
        *four_blocks_horizontal,
        *four_blocks_vertical,
        *block,
        *two_blocks_vertical1,
        *block1,
        *block2,
        *block3,
        *mystery_block5,
        *mystery_block3,
        *mystery_block4,
        *mystery_block2,
        *mystery_block1
    ]

    # Tạo danh sách riêng cho mystery blocks
    mystery_blocks = [*mystery_block1, *mystery_block2, *mystery_block3, *mystery_block4, *mystery_block5]
    
    # Thêm mystery blocks vào danh sách objects
    objects.extend(mystery_blocks)

    offset_x = 0  # Offset trục X
    scroll_area_width = 200  # Khu vực cuộn
    run = True
    game_over = False
    round_time = 90  # Thời gian mỗi vòng (giây)
    start_time = pygame.time.get_ticks()  # Lấy thời gian bắt đầu
    font = pygame.font.Font(None, 50)
    text_color = (0, 255, 0)

    clock = pygame.time.Clock()
     
    # Random 5 câu hỏi từ ngân hàng câu hỏi
    selected_questions = random.sample(question_bank1, 5)
    used_questions = []
    
    # Font cho hiển thị điểm và thời gian
    font = pygame.font.Font('''Cabin-Variable.ttf''', 36)
    while run:
      # Filter out answered mystery blocks
        objects = [obj for obj in objects if not (isinstance(obj, MysteryBlock) and obj.answered)]
        # Tính toán thời gian còn lại
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Chuyển từ mili giây sang giây
        time_left = max(0, round_time - elapsed_time)  # Đảm bảo thời gian không âm
        
         # Hiển thị điểm và thời gian
        score_text = font.render(f'''Score: {score}/5''', True, (0, 255, 0))
        time_text = font.render(f'''Time: {time_left}s''', True, (0, 255, 0))
        score_rect = score_text.get_rect(topright=(WIDTH - 20, 20))
        time_rect = time_text.get_rect(topright=(WIDTH - 20, 60))
        
         
        
        # Vẽ điểm và thời gian
        window.blit(score_text, score_rect)
        window.blit(time_text, time_rect)
        
        pygame.display.update()

         # Nếu hết giờ, thoát game
       
            

        # Cập nhật vị trí camera
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += 3*player.x_vel


       # Xử lý va chạm với block câu hỏi
        question_result = handle_question_block_collision(player, mystery_blocks, window, used_questions)
        if question_result is not None:
            if question_result:
                score += 1
                print(f'''Score increased to {score}''')  # Debug message

       

        if time_left == 0:  # Check if the time is up
            print('''Hết giờ!''')
            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()
            
            # # Vẽ các bảng thông báo
            # window.fill((200, 200, 200))  # Background
            # score_board.draw()
            # button_board.draw()
            # pygame.display.flip()
        
            # # Hiện bảng lựa chọn dựa vào điểm số
            # if score>=4:
            #     choice_dialog = ResultInfo(window, has_next_round=True)
            #     window.wait_window(choice_dialog.choice_window)
            
            #     # Xử lý lựa chọn
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
                    
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)  # Khởi động lại màn chơi
            #     elif choice_dialog.choice == "next":
            #         window.destroy()
            #         main3(window)
            # elif score<4:
            #     # Hiển thị thông báo game over
            #     game_over = GameOverDialog(window, score)
            #     window.wait_window(game_over.dialog_window)
            #     game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''

            #     # Hiển thị dialog với 2 nút cho trường hợp thất bại
            #     choice_dialog = ChoiceDialogFail(window)
            #     window.wait_window(choice_dialog.choice_window)
                
            #     if choice_dialog.choice == "menu":
            #         window.destroy()
            #         menu_map2(window)
            #     elif choice_dialog.choice == "restart":
            #         window.destroy()
            #         main2(window)
                
                # Check if player reaches the x-axis condition
        if player.rect.x > 6200:  # Example condition
            action = trigger_menu(window, '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_win.png''', (WIDTH // 2 - 100, HEIGHT // 2 + 200))
            # if action == '''menu_map''':
            #     map_action = menu_map(window, '''assets/Background/z6105275572936_31db720c63d3dafccde4dd83d4772e28.jpg''', (WIDTH // 2 - 125, HEIGHT // 2 - 100))
            #     if map_action == '''return_to_main''':
            return  # Exit `main` and restart the game loop
        clock.tick(FPS)  # Giới hạn FPS
        for event in pygame.event.get():  # Xử lý sự kiện
            if event.type == pygame.QUIT:
                run = False
                break
            if not game_over and event.type == pygame.KEYDOWN:  # Nếu nhấn SPACE
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if game_over:  # Xử lý màn hình Game Over
            game_over_image_path = '''assets\MainCharacters\Zeen_png\Zeen_2\Zeen_2_lose.png'''
            game_over_image = pygame.image.load(game_over_image_path).convert_alpha()
            game_over_image = pygame.transform.scale(game_over_image, (400, 300))
            window.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render('''GAME OVER''', True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
            image_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            button_width, button_height = 200, 50
            button_color = (0, 200, 0)
            button_hover_color = (0, 255, 0)
            button_text_color = (255, 255, 255)
            button_font = pygame.font.Font(None, 36)
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 200, button_width, button_height)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(pygame.mouse.get_pos()):
                            return
                window.fill((0, 0, 0))
                window.blit(game_over_image, image_rect)
                window.blit(text, text_rect)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
                current_button_color = button_hover_color if is_hovering else button_color
                pygame.draw.rect(window, current_button_color, button_rect)
                button_text = button_font.render('''Restart''', True, button_text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                window.blit(button_text, button_text_rect)
                pygame.display.update()
            # Hiển thị thông báo game over
            print('''Trò chơi kết thúc''')
        

            run = False
            game_over = True
            # Hiện bảng điểm
            score_board = ScoreBoard(window, score, current_time, 0)
            button_board = ButtonBoard(window, score)
            
            showing_results = True
            while showing_results:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = button_board.handle_click(event.pos)
                        if action:
                            if action == "Main Menu":
                                menu_map2(window)
                                # Chuyển về main menu
                                return "main_menu"
                            elif action == "Restart":
                                main2(window)
                            elif action == "Next Round":
                                # Chuyển sang màn tiếp theo
                                main3(window)
            pygame.display.update()   

        player.loop(FPS)  # Cập nhật trạng thái nhân vật
        fire.loop()  # Cập nhật trạng thái bẫy lửa
        handle_move(player, objects)  # Xử lý di chuyển

        if player.rect.top > HEIGHT or player.rect.bottom < -100:  # Kiểm tra rơi khỏi màn hình
            game_over = True
            continue
        draw(window, background, bg_image, player, objects, offset_x)  # Vẽ tất cả đối tượng
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    pygame.quit()
    quit()
if __name__ == "__main__":
    menu_background_path = "assets/Background/startmenu.jpg"
    start_button_position = (WIDTH // 2 - 100, HEIGHT // 2 + 250)
    map_menu = "assets/Background/map.jpg"
    change_picture_button_position = (WIDTH - 385, HEIGHT // 2 - 30)
    change_picture_button_position2 = (WIDTH - 590, HEIGHT // 2 - 320)
    change_picture_button_position3 = (315, 380)
    change_picture_button_position4 = (55,70)
    start_menu(window, menu_background_path, start_button_position)
    menu_map(window, map_menu, change_picture_button_position,)
    main(window)
    menu_map2(window, map_menu, change_picture_button_position2,)
    main2(window) 
    menu_map3(window, map_menu, change_picture_button_position3,)
    main3(window)
    menu_map4(window, map_menu, change_picture_button_position4,)
    main4(window)
    while True:
        main4(window)
