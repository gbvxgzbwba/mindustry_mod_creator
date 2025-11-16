# Конфигурация типов блоков
VERSION = "1.1"
BLOCK_TYPES_CONFIG = {
    "wall": {
        "name": "Стена",
        "icon": "copper-wall.png",
        "category": "defense",
        "size_range": (1, 15)
    },
    "conveyor": {
        "name": "Конвейер", 
        "icon": "titanium-conveyor.png",
        "category": "distribution",
        "size_range": (1, 1)
    },
    "router": {
        "name": "Роутер",
        "icon": "router.png", 
        "category": "distribution",
        "size_range": (1, 2)
    },
    "PowerNode": {
        "name": "Энергоузел",
        "icon": "power-node.png",
        "category": "power", 
        "size_range": (1, 15)
    },
    "SolarGenerator": {
        "name": "Солнечная панель",
        "icon": "solar-panel.png",
        "category": "power",
        "size_range": (1, 15)
    },
    "GenericCrafter": {
        "name": "Завод",
        "icon": "silicon-smelter.png",
        "category": "crafting",
        "size_range": (1, 15)
    },
    "conduit": {
        "name": "Труба",
        "icon": "conduit.png",
        "category": "liquid",
        "size_range": (1, 1)
    },
    "StorageBlock": {
        "name": "Хранилище",
        "icon": "container.png",
        "category": "distribution",
        "size_range": (1, 15)
    },
    "ConsumeGenerator": {
        "name": "Генератор",
        "icon": "steam-generator.png",
        "category": "power",
        "size_range": (1, 15)
    },
    "Battery": {
        "name": "Батарея",
        "icon": "battery.png",
        "category": "power",
        "size_range": (1, 15)
    },
    "ThermalGenerator": {
        "name": "Термальный генератор",
        "icon": "thermal-generator.png",
        "category": "power",
        "size_range": (1, 15)
    },
    "BeamNode": {
        "name": "Лучевой узел",
        "icon": "beam-node.png",
        "category": "power",
        "size_range": (1, 1)
    },
    "Junction": {
        "name": "Перекрёсток",
        "icon": "junction.png",
        "category": "distribution",
        "size_range": (1, 1)
    },
    "Unloader": {
        "name": "Разгрузчик",
        "icon": "unloader.png",
        "category": "distribution",
        "size_range": (1, 1)
    },
    "liquid_router": {
        "name": "Роутер жидкости",
        "icon": "liquid-router.png",
        "category": "liquid",
        "size_range": (1, 1)
    },
    "LiquidJunction": {
        "name": "Перекрёсток жидкости",
        "icon": "liquid-junction.png",
        "category": "liquid",
        "size_range": (1, 1)
    },
    "Liquid_Tank": {
        "name": "Бак жидкости",
        "icon": "liquid-container.png",
        "category": "liquid",
        "size_range": (1, 15)
    },
    "Pump": {
        "name": "Помпа",
        "icon": "rotary-pump.png",
        "category": "liquid",
        "size_range": (1, 15)
    },
    "SolidPump": {
        "name": "Наземная помпа",
        "icon": "water-extractor.png",
        "category": "production",
        "size_range": (1, 15)
    }
}

def get_block_type_info(block_type):
    """Получение информации о типе блока"""
    return BLOCK_TYPES_CONFIG.get(block_type, {
        "name": "Неизвестный блок",
        "icon": "unknown.png",
        "category": "misc",
        "size_range": (1, 1)
    })

def get_all_block_types():
    """Получение всех типов блоков"""
    return list(BLOCK_TYPES_CONFIG.keys())