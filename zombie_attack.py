# ============================================
# ИГРА "АТАКА ЗОМБИ" ДЛЯ MINECRAFT (Python)
# ============================================

# Импортируем необходимые модули
import mcpi.minecraft as minecraft  # Основной модуль для связи с игрой
import mcpi.block as block          # Модуль для работы с блоками (камень, воздух и т.д.)
import mcpi.entity as entity        # Модуль для работы с существами (зомби, криперы)
import time                         # Модуль для задержек (таймер)
import random                       # Модуль для случайных чисел (спавн зомби в случайном месте)
import math                         # Модуль для математики (вычисление расстояния)

# ============================================
# 1. ПОДКЛЮЧЕНИЕ К ИГРЕ
# ============================================
print("[INFO] Подключаемся к Minecraft...")
try:
    # Создаем объект для управления игрой
    mc = minecraft.Minecraft.create()
    # Отправляем сообщение в чат игры, если подключение успешно
    mc.postToChat("Python подключен! Запускаем 'Атаку зомби'!")
    print("[SUCCESS] Подключение установлено!")
except ConnectionRefusedError:
    print("[ERROR] Не могу подключиться к Minecraft!")
    print("[ПОДСКАЗКА] Убедись, что:")
    print("  1. Minecraft запущен и в него зашел в мир")
    print("  2. Установлен мод Raspberry Jam Mod")
    input("Нажми Enter для выхода...")
    exit()

# ============================================
# 2. НАСТРОЙКИ ИГРЫ (можно менять)
# ============================================
ARENA_SIZE = 20           # Размер квадратной арены (в блоках)
ZOMBIE_COUNT = 5          # Сколько зомби спавнить за волну
WAVE_DELAY = 10           # Пауза (в секундах) между волнами зомби
GAME_DURATION = 120       # Длительность игры в секундах (2 минуты)

# ============================================
# 3. СОЗДАНИЕ АРЕНЫ
# ============================================
print("[INFO] Строим арену для битвы...")
mc.postToChat("Строим арену! Отойди в сторону!")

# Получаем текущие координаты игрока (x, y, z)
player_pos = mc.player.getTilePos()
px, py, pz = player_pos.x, player_pos.y, player_pos.z

# Определяем границы арены (центр — там, где стоит игрок)
x1 = px - ARENA_SIZE // 2
x2 = px + ARENA_SIZE // 2
z1 = pz - ARENA_SIZE // 2
z2 = pz + ARENA_SIZE // 2

# Строим пол арены (из камня)
for x in range(x1, x2 + 1):
    for z in range(z1, z2 + 1):
        # setBlock(x, y, z, тип_блока) — ставит блок на координаты
        mc.setBlock(x, py - 1, z, block.STONE)  # py - 1 = под ногами игрока

# Строим стены арены (из кирпича)
for x in range(x1, x2 + 1):
    mc.setBlock(x, py, z1, block.BRICK_BLOCK)
    mc.setBlock(x, py, z2, block.BRICK_BLOCK)
for z in range(z1, z2 + 1):
    mc.setBlock(x1, py, z, block.BRICK_BLOCK)
    mc.setBlock(x2, py, z, block.BRICK_BLOCK)

# Поднимаем стены в высоту на 5 блоков (чтобы зомби не выпали)
for y in range(py + 1, py + 5):
    for x in range(x1, x2 + 1):
        mc.setBlock(x, y, z1, block.BRICK_BLOCK)
        mc.setBlock(x, y, z2, block.BRICK_BLOCK)
    for z in range(z1, z2 + 1):
        mc.setBlock(x1, y, z, block.BRICK_BLOCK)
        mc.setBlock(x2, y, z, block.BRICK_BLOCK)

mc.postToChat("Арена готова! Готовься к атаке зомби!")
time.sleep(2)  # Даем игроку 2 секунды подготовиться

# ============================================
# 4. ФУНКЦИЯ ДЛЯ СПАВНА ЗОМБИ
# ============================================
def spawn_zombie_wave(count):
    """
    Спавнит указанное количество зомби в случайных местах за стенами арены.
    """
    zombies_spawned = 0
    for i in range(count):
        # Выбираем случайную сторону для спавна (0=север,1=юг,2=запад,3=восток)
        side = random.randint(0, 3)

        if side == 0:  # Северная стена (z1)
            spawn_x = random.randint(x1 + 2, x2 - 2)
            spawn_z = z1 - 5
        elif side == 1:  # Южная стена (z2)
            spawn_x = random.randint(x1 + 2, x2 - 2)
            spawn_z = z2 + 5
        elif side == 2:  # Западная стена (x1)
            spawn_x = x1 - 5
            spawn_z = random.randint(z1 + 2, z2 - 2)
        else:  # Восточная стена (x2)
            spawn_x = x2 + 5
            spawn_z = random.randint(z1 + 2, z2 - 2)

        # Высота спавна — на уровне пола арены (py)
        spawn_y = py

        # spawnEntity(x, y, z, тип_существа) — создает моба в мире
        mc.spawnEntity(spawn_x, spawn_y, spawn_z, entity.ZOMBIE)
        zombies_spawned += 1

    mc.postToChat(f"Волна зомби! Появилось: {zombies_spawned}")
    return zombies_spawned

# ============================================
# 5. ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
# ============================================
print("[INFO] Начинаем игру!")
mc.postToChat(f"Выживай {GAME_DURATION} секунд. Удачи!")

start_time = time.time()  # Запоминаем время начала игры
wave_number = 0           # Номер текущей волны

while True:
    # 5.1. Проверяем, не закончилось ли время
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > GAME_DURATION:
        mc.postToChat("=== ВРЕМЯ ВЫШЛО! ===")
        mc.postToChat("Ты победил! Игра окончена.")
        break  # Выходим из цикла — игра закончена

    # 5.2. Выводим оставшееся время в чат каждые 30 секунд
    time_left = GAME_DURATION - int(elapsed_time)
    if time_left % 30 == 0:  # Каждые ровно 30 секунд
        mc.postToChat(f"Осталось времени: {time_left} сек")

    # 5.3. Спавним новую волну каждые WAVE_DELAY секунд
    if int(elapsed_time) % WAVE_DELAY == 0:
        wave_number += 1
        print(f"[WAVE] Запускаем волну №{wave_number}")
        spawn_zombie_wave(ZOMBIE_COUNT + wave_number)  # С каждой волной зомби больше
        time.sleep(1)  # Небольшая пауза, чтобы не спавнить несколько волн в одну секунду

    # 5.4. Короткая пауза в основном цикле, чтобы не нагружать процессор
    time.sleep(0.5)

# ============================================
# 6. ЗАВЕРШЕНИЕ ИГРЫ
# ============================================
print("[INFO] Игра завершена!")
mc.postToChat("Спасибо за игру!")
mc.postToChat("Для рестарта перезапусти программу.")

# Даем игроку 5 секунд насладиться победой, затем убираем всех зомби
time.sleep(5)
mc.postToChat("Убираем всех зомби...")

# Простой способ "убить" всех зомби — заполнить территорию лавой (шутка=)
# В реальности нужно было бы отслеживать ID каждого спавненного зомби,
# но для простоты мы просто выведем сообщение.

mc.postToChat("(В продвинутой версии здесь был бы код удаления зомби)")
