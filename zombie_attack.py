import mcpi.minecraft as minecraft
import mcpi.block as block
import mcpi.entity as entity
import time
import random

# ==========================
# Подключение к Minecraft
# ==========================
mc = minecraft.Minecraft.create()

# ==========================
# Игровые переменные
# ==========================
over = False        # Флаг окончания игры
level = 1           # Текущий уровень волн
max_level = 5       # Максимальный уровень
max_level_reached = False
score = 10          # Начальные очки
spawn_timer = time.time()  # Таймер для спавна волн
spawn_delay = 20    # Задержка между волнами (секунды)

# Получаем стартовую позицию игрока
spawn_x, spawn_y, spawn_z = mc.player.getTilePos()

# ==========================
# Функции
# ==========================

# Безопасный телепорт: ставим платформу и телепортируем игрока
def safe_teleport(x, y, z):
    mc.setBlocks(x-1, y-1, z-1, x+1, y-1, z+1, block.GRASS.id)
    mc.player.setTilePos(x, y, z)

# Строим арену 10x10 из розового стекла
def build_arena(center_x, center_y, center_z):
    y = center_y + 3
    x1 = center_x - 5
    x2 = center_x + 5
    z1 = center_z - 5
    z2 = center_z + 5
    # Пол арены
    mc.setBlocks(x1, y, z1, x2, y, z2, block.STAINED_GLASS.id, 6)
    # Стены арены
    mc.setBlocks(x1, y+1, z1, x2, y+5, z1, block.STAINED_GLASS.id, 6)
    mc.setBlocks(x1, y+1, z2, x2, y+5, z2, block.STAINED_GLASS.id, 6)
    mc.setBlocks(x1, y+1, z1, x1, y+5, z2, block.STAINED_GLASS.id, 6)
    mc.setBlocks(x2, y+1, z1, x2, y+5, z2, block.STAINED_GLASS.id, 6)
    mc.postToChat("🏟️ Арена построена!")

# Спавн мобов вокруг арены в зависимости от уровня
def spawn_mobs(level):
    center = mc.player.getTilePos()
    x, y, z = center.x, center.y, center.z
    
    for i in range(5):
        # Случайная сторона спавна: 0=север, 1=восток, 2=юг, 3=запад
        side = random.randint(0, 3)
        if side == 0:  # Север
            rx = random.randint(-5, 5)
            rz = random.randint(-12, -7)
        elif side == 1:  # Восток
            rx = random.randint(7, 12)
            rz = random.randint(-5, 5)
        elif side == 2:  # Юг
            rx = random.randint(-5, 5)
            rz = random.randint(7, 12)
        elif side == 3:  # Запад
            rx = random.randint(-12, -7)
            rz = random.randint(-5, 5)
        
        # Проверка, что точка снаружи арены (6+ блоков от центра)
        if abs(rx) >= 6 or abs(rz) >= 6:
            spawn_y = y + 1
            # Спавн моба в зависимости от уровня
            if level == 1:
                mc.spawnEntity(x + rx, spawn_y, z + rz, entity.ZOMBIE)
            elif level == 2:
                mc.spawnEntity(x + rx, spawn_y, z + rz, entity.SPIDER)
            elif level == 3:
                mc.spawnEntity(x + rx, spawn_y, z + rz, entity.PIG_ZOMBIE)
            elif level == 4:
                mc.spawnEntity(x + rx, spawn_y, z + rz, entity.VEX)
            elif level == 5:
                mc.spawnEntity(x + rx, spawn_y, z + rz, entity.WITHER_SKELETON)
                mc.postToChat("💀 БОСС появился!")

# ==========================
# Начальный спавн и строительство арены
# ==========================
safe_teleport(spawn_x, spawn_y, spawn_z)
build_arena(spawn_x, spawn_y, spawn_z)
mc.player.setTilePos(spawn_x, spawn_y + 2, spawn_z)  # Над полом арены

# ==========================
# Приветствие игрока
# ==========================
mc.postToChat("Добро пожаловать в Мир Зомби!")
mc.postToChat("Мы тебе даем 10 очков.")
mc.postToChat("Ты их можешь тратить на волшебный чат.")
mc.postToChat("Заработки 50 очков, напиши в чат 'win' и ты победишь!")
mc.postToChat("Учти: если отправишь неправильное сообщение, то отправим тебя в ад!!!")
time.sleep(10)

# ==========================
# Главный игровой цикл
# ==========================
while True:
    time.sleep(0.1)
    pos = mc.player.getTilePos()
    
    if over:
        break
    
    # --------------------------
    # Спавн новых волн
    # --------------------------
    current_time = time.time()
    if not max_level_reached and current_time - spawn_timer > spawn_delay:
        spawn_mobs(level)
        mc.postToChat(f"🌊 Волна {level} началась!")
        spawn_timer = current_time  # Сброс таймера
        level += 1
        if level > max_level:
            level = max_level
            max_level_reached = True
            mc.postToChat("🔥 ВЫЖИВАЙ! Новых волн не будет!")
    
    # --------------------------
    # Сбор очков с травы/цветов
    # --------------------------
    grass_found = False
    for check_y in [pos.y, pos.y - 1, pos.y - 2]:
        check_block = mc.getBlock(pos.x, check_y, pos.z)
        if check_block in [block.GRASS_TALL.id, block.FLOWER_CYAN.id, block.FLOWER_YELLOW.id]:
            grass_found = True
            for remove_y in [pos.y, pos.y - 1, pos.y - 2]:
                mc.setBlock(pos.x, remove_y, pos.z, block.AIR.id)
            break
    if grass_found:
        score += 1
        mc.postToChat("+1")
        mc.postToChat("Очки: " + str(score))
    
    # --------------------------
    # Ограничение выхода за арену
    # --------------------------
    if abs(pos.x - spawn_x) > 70 or abs(pos.z - spawn_z) > 70:
        safe_teleport(spawn_x, spawn_y, spawn_z)
        mc.postToChat("Возвращайся обратно и сражайся!!!")
    
    # --------------------------
    # Проверка отрицательных очков
    # --------------------------
    if score < 0:
        mc.postToChat("У тебя отрицательное количество очков. Ты лишён волшебного чата!")
        over = True
    
    # --------------------------
    # Обработка чат-команд
    # --------------------------
    chat = mc.events.pollChatPosts()
    for e in chat:
        m = e.message
        if m == "box":
            mc.setBlocks(pos.x - 5, pos.y - 10, pos.z - 5, pos.x + 5, pos.y - 5, pos.z + 5, block.COBBLESTONE.id)
            mc.setBlocks(pos.x - 4, pos.y - 9, pos.z - 4, pos.x + 4, pos.y - 6, pos.z + 4, block.AIR.id)
            mc.player.setTilePos(pos.x, pos.y - 9, pos.z)
            mc.postToChat("-10")
            mc.postToChat("Очки: " + str(score))
            score -= 10
        elif m == "lava":
            mc.setBlocks(pos.x - 5, pos.y - 1, pos.z - 5, pos.x + 5, pos.y - 1, pos.z + 5, block.LAVA.id)
            mc.setBlocks(pos.x - 5, pos.y - 1, pos.z - 5, pos.x + 5, pos.y - 1, pos.z, block.GRASS.id)
            mc.setBlocks(pos.x, pos.y - 1, pos.z - 5, pos.x, pos.y - 1, pos.z + 5, block.GRASS.id)
            mc.postToChat("-10")
            mc.postToChat("Очки: " + str(score))
            score -= 10
        elif m == "tnt":
            mc.setBlock(pos.x + 3, pos.y, pos.z, block.TNT.id)
            mc.setBlock(pos.x - 3, pos.y, pos.z, block.TNT.id)
            mc.setBlock(pos.x, pos.y, pos.z + 3, block.TNT.id)
            mc.setBlock(pos.x + 3, pos.y + 1, pos.z, block.FIRE.id)
            mc.setBlock(pos.x - 3, pos.y + 1, pos.z, block.FIRE.id)
            mc.setBlock(pos.x, pos.y + 1, pos.z + 3, block.FIRE.id)
            mc.setBlock(pos.x, pos.y + 1, pos.z - 3, block.FIRE.id)
            mc.postToChat("-10")
            mc.postToChat("Очки: " + str(score))
            score -= 10
        elif m == "pit":
            mc.setBlocks(pos.x - 5, pos.y, pos.z - 5, pos.x + 5, pos.y - 5, pos.z + 5, block.AIR.id)
            mc.setBlocks(pos.x, pos.y - 1, pos.z, pos.x + 5, pos.y - 1, pos.z, block.GRASS.id)
            mc.postToChat("-10")
            mc.postToChat("Очки: " + str(score))
            score -= 10
        elif m == "water":
            mc.player.setTilePos(pos.x, pos.y + 10, pos.z)
            mc.setBlock(pos.x, pos.y + 9, pos.z, block.STONE.id)
            mc.setBlocks(pos.x - 5, pos.y + 10, pos.z - 5, pos.x + 5, pos.y + 10, pos.z + 5, block.WATER_FLOWING.id)
            mc.postToChat("-10")
            mc.postToChat("Очки: " + str(score))
            score -= 10
        elif m == "spawn":
            score = 30
            mc.postToChat("Мы вернули тебя обратно.")
            mc.player.setTilePos(-296, 63, -644)
            mc.postToChat("-30")
            mc.postToChat("Очки: " + str(score))
        elif m == "win" and score >= 50:
            # Победа игрока
            score -= 50
            mc.postToChat("-50")
            mc.postToChat("🎉 ПОБЕДА! Строим золотую платформу...")
            current_pos = mc.player.getTilePos()
            mc.setBlock(current_pos.x, current_pos.y - 1, current_pos.z, block.GOLD_BLOCK.id)
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    mc.setBlock(current_pos.x + dx, current_pos.y - 1, current_pos.z + dz, block.GOLD_BLOCK.id)
            win_y = 100
            mc.player.setTilePos(0, win_y, 0)
            platform_size = 7
            half_size = platform_size // 2
            mc.setBlocks(-half_size, win_y - 1, -half_size, 
                         half_size, win_y - 1, half_size, 
                         block.GOLD_BLOCK.id)
            mc.setBlocks(-half_size, win_y, -half_size,
                         -half_size, win_y + 5, -half_size,
                         block.DIAMOND_BLOCK.id)
            mc.setBlocks(half_size, win_y, -half_size,
                         half_size, win_y + 5, -half_size,
                         block.DIAMOND_BLOCK.id)
            mc.setBlocks(-half_size, win_y, half_size,
                         -half_size, win_y + 5, half_size,
                         block.DIAMOND_BLOCK.id)
            mc.setBlocks(half_size, win_y, half_size,
                         half_size, win_y + 5, half_size,
                         block.DIAMOND_BLOCK.id)
            mc.player.setTilePos(0, win_y, 0)
            mc.postToChat("🏆 ТЫ ПОБЕДИЛ! Поздравляем!")
            mc.postToChat("💰 Золотая платформа твоя!")
            over = True
        elif m == "win" and score < 50:
            mc.postToChat("❌ Нужно 50 очков для победы!")
        else:
            # Любое неправильное сообщение отправляет в "ад"
            if m not in ["box", "lava", "tnt", "pit", "water", "spawn", "win"]:
                mc.player.setTilePos(1000, 100, 1000)
                pos = mc.player.getTilePos()
                mc.setBlocks(pos.x - 1, pos.y - 1, pos.z, pos.x + 4, pos.y + 4, pos.z, block.OBSIDIAN.id)
                mc.setBlocks(pos.x, pos.y, pos.z, pos.x + 3, pos.y + 3, pos.z, block.AIR.id)
                mc.setBlock(pos.x, pos.y, pos.z, block.FIRE.id)
                over = True

