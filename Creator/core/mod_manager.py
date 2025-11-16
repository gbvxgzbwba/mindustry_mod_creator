import os
import json
import zipfile
VERSION = "1.0"
class ModManager:
    def __init__(self, mod_name):
        self.mod_name = mod_name
        self.mod_folder = os.path.join("mindustry_mod_creator", "mods", mod_name)
    
    def create_mod_structure(self):
        """Создание структуры папок мода"""
        folders = [
            "content/blocks",
            "content/items", 
            "content/liquids",
            "sprites/blocks",
            "sprites/items",
            "sprites/liquids"
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(self.mod_folder, folder), exist_ok=True)
        
        return True
    
    def validate_mod_structure(self):
        """Проверка структуры мода"""
        required_folders = [
            "content",
            "sprites"
        ]
        
        for folder in required_folders:
            if not os.path.exists(os.path.join(self.mod_folder, folder)):
                return False
        
        return True
    
    def get_mod_info(self):
        """Получение информации о моде"""
        mod_json_path = os.path.join(self.mod_folder, "mod.json")
        
        if not os.path.exists(mod_json_path):
            return None
        
        try:
            with open(mod_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    
    def get_block_count(self):
        """Получение количества блоков"""
        blocks_path = os.path.join(self.mod_folder, "content", "blocks")
        if not os.path.exists(blocks_path):
            return 0
        
        count = 0
        for block_type in os.listdir(blocks_path):
            type_path = os.path.join(blocks_path, block_type)
            if os.path.isdir(type_path):
                count += len([f for f in os.listdir(type_path) if f.endswith('.json')])
        
        return count
    
    def get_item_count(self):
        """Получение количества предметов"""
        items_path = os.path.join(self.mod_folder, "content", "items")
        if not os.path.exists(items_path):
            return 0
        
        return len([f for f in os.listdir(items_path) if f.endswith('.json')])
    
    def get_liquid_count(self):
        """Получение количества жидкостей"""
        liquids_path = os.path.join(self.mod_folder, "content", "liquids")
        if not os.path.exists(liquids_path):
            return 0
        
        return len([f for f in os.listdir(liquids_path) if f.endswith('.json')])