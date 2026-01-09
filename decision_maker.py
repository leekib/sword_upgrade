
from abc import ABC, abstractmethod
from enum import Enum
import re

class GameAction:
    DESTROY = 'DESTROY'
    MAINTAIN = 'MAINTAIN'
    SUCCESS = 'SUCCESS'
    SELL = 'SELL'
    UNKNOWN = 'UNKNOWN'
    
    def __init__(self, action_type, weapon_name, weapon_level, gold_remaining, gold_change, start_weapon_name=None):
        self.action_type = action_type
        self.weapon_name = weapon_name
        self.weapon_level = weapon_level
        self.gold_remaining = gold_remaining
        self.gold_change = gold_change
        self.start_weapon_name = start_weapon_name
    
    def __str__(self):
        return f"Action Type: {self.action_type}, Weapon Name: {self.weapon_name}, Weapon Level: {self.weapon_level}, Gold Remaining: {self.gold_remaining}, Gold Change: {self.gold_change}, Start Weapon Name: {self.start_weapon_name}"
    
    def to_json(self):
        return {
            'action_type': self.action_type,
            'weapon_name': self.weapon_name,
            'weapon_level': self.weapon_level,
            'gold_remaining': self.gold_remaining,
            'gold_change': self.gold_change,
            'start_weapon_name': self.start_weapon_name
        }
    
    def from_json(self, json):
        return GameAction(
            action_type=json['action_type'],
            weapon_name=json['weapon_name'],
            weapon_level=json['weapon_level'],
            gold_remaining=json['gold_remaining'],
            gold_change=json['gold_change'],
            start_weapon_name=json['start_weapon_name']
        )
    
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, GameAction):
            return False
        return self.action_type == value.action_type and self.weapon_name == value.weapon_name and self.weapon_level == value.weapon_level and self.gold_remaining == value.gold_remaining and self.gold_change == value.gold_change and self.start_weapon_name == value.start_weapon_name
    
    @staticmethod
    def from_text(text):
        """
        텍스트에서 GameAction 정보를 파싱합니다.
        """
        if '💥강화 파괴💥' in text:
            # 골드 변화량 파싱: -500G
            gold_change_match = re.search(r'💸사용 골드:\s*(-?\d+(?:,\d+)*)G', text)
            gold_change = int(gold_change_match.group(1).replace(',', '')) if gold_change_match else 0
            
            # 남은 골드 파싱: 1,725,408G
            gold_remaining_match = re.search(r'💰남은 골드:\s*(\d+(?:,\d+)*)G', text)
            gold_remaining = int(gold_remaining_match.group(1).replace(',', '')) if gold_remaining_match else 0
            
            # 무기 정보 파싱: [+5] 지혜의 존재를 부정하는 몽둥이 -> [+0] 빛이 흐릿한 장난감 광선검
            weapon_match = re.search(r'『\[(\+\d+)\]\s*([^』]+)』\s*산산조각 나서,\s*『\[(\+\d+)\]\s*([^』]+)』', text)
            
            if weapon_match:
                start_level = int(weapon_match.group(1).replace('+', ''))
                start_weapon_name = weapon_match.group(2).strip()
                new_level = int(weapon_match.group(3).replace('+', ''))
                new_weapon_name = weapon_match.group(4).strip()
                
                return GameAction(
                    action_type=GameAction.DESTROY,
                    weapon_name=new_weapon_name,
                    weapon_level=new_level,
                    gold_remaining=gold_remaining,
                    gold_change=gold_change,
                    start_weapon_name=new_weapon_name
                )
        
        elif '💦강화 유지💦' in text:
            # 유지의 경우도 비슷하게 파싱
            gold_change_match = re.search(r'💸사용 골드:\s*(-?\d+(?:,\d+)*)G', text)
            gold_change = int(gold_change_match.group(1).replace(',', '')) if gold_change_match else 0
            
            gold_remaining_match = re.search(r'💰남은 골드:\s*(\d+(?:,\d+)*)G', text)
            gold_remaining = int(gold_remaining_match.group(1).replace(',', '')) if gold_remaining_match else 0
            
            weapon_match = re.search(r'『\[(\+\d+)\]\s*([^』]+)』', text)
            if weapon_match:
                level = int(weapon_match.group(1).replace('+', ''))
                weapon_name = weapon_match.group(2).strip()
                
                return GameAction(
                    action_type=GameAction.MAINTAIN,
                    weapon_name=weapon_name,
                    weapon_level=level,
                    gold_remaining=gold_remaining,
                    gold_change=gold_change
                )
        
        elif '✨강화 성공✨' in text:
            # 성공의 경우
            gold_change_match = re.search(r'💸사용 골드:\s*(-?\d+(?:,\d+)*)G', text)
            gold_change = int(gold_change_match.group(1).replace(',', '')) if gold_change_match else 0
            
            gold_remaining_match = re.search(r'💰남은 골드:\s*(\d+(?:,\d+)*)G', text)
            gold_remaining = int(gold_remaining_match.group(1).replace(',', '')) if gold_remaining_match else 0
            
            # 레벨 정보 파싱: +4 → +5
            level_match = re.search(r'\+(\d+)\s*→\s*\+(\d+)', text)
            old_level = int(level_match.group(1)) if level_match else None
            new_level = int(level_match.group(2)) if level_match else None
            
            # 무기 정보 파싱: ⚔️획득 검: [+5] 지혜의 존재를 부정하는 몽둥이
            weapon_match = re.search(r'⚔️획득 검:\s*\[(\+\d+)\]\s*(.+?)(?:\n|$)', text)
            if weapon_match:
                level_from_weapon = int(weapon_match.group(1).replace('+', ''))
                weapon_name = weapon_match.group(2).strip()
                
                # new_level이 없으면 무기에서 파싱한 레벨 사용
                final_level = new_level if new_level is not None else level_from_weapon
                
                return GameAction(
                    action_type=GameAction.SUCCESS,
                    weapon_name=weapon_name,
                    weapon_level=final_level,
                    gold_remaining=gold_remaining,
                    gold_change=gold_change
                )
        
        elif '판매〗' in text:
            # 판매의 경우
            # 획득 골드 파싱: +1,772G
            gold_change_match = re.search(r'💶획득 골드:\s*(\+?\d+(?:,\d+)*)G', text)
            gold_change = int(gold_change_match.group(1).replace(',', '').replace('+', '')) if gold_change_match else 0
            
            # 현재 보유 골드 파싱
            gold_remaining_match = re.search(r'💰현재 보유 골드:\s*(\d+(?:,\d+)*)G', text)
            gold_remaining = int(gold_remaining_match.group(1).replace(',', '')) if gold_remaining_match else 0
            
            # 새로운 무기 파싱: ⚔️새로운 검 획득: [+0] 낡은 몽둥이
            weapon_match = re.search(r'⚔️새로운 검 획득:\s*\[(\+\d+)\]\s*(.+?)(?:\n|$)', text)
            if weapon_match:
                level = int(weapon_match.group(1).replace('+', ''))
                weapon_name = weapon_match.group(2).strip()
                
                return GameAction(
                    action_type=GameAction.SELL,
                    weapon_name=weapon_name,
                    weapon_level=level,
                    gold_remaining=gold_remaining,
                    gold_change=gold_change,
                    start_weapon_name=weapon_name
                )
            
            # 무기 정보가 없어도 판매 액션 반환
            return GameAction(
                action_type=GameAction.SELL,
                weapon_name=None,
                weapon_level=0,
                gold_remaining=gold_remaining,
                gold_change=gold_change
            )
        
        return None


class GameState:
    def __init__(self, gold, weapon_name, weapon_level):
        self.gold = gold
        self.weapon_name = weapon_name
        self.weapon_level = weapon_level
        self.start_weapon_name = weapon_name
    
    def update_by_action(self, action: GameAction):
        if action.action_type == GameAction.UNKNOWN:
            return
        self.gold = action.gold_remaining
        self.weapon_name = action.weapon_name
        self.weapon_level = action.weapon_level
        if action.start_weapon_name is not None:
            self.start_weapon_name = action.start_weapon_name

    
    def is_rare_weapon(self):
        return self.start_weapon_name is not None and '낡은' not in self.start_weapon_name
    
    def to_json(self):
        return {
            'gold': self.gold,
            'weapon_name': self.weapon_name,
            'weapon_level': self.weapon_level,
            'start_weapon_name': self.start_weapon_name
        }
    
    def from_json(self, json):
        return GameState(
            gold=json['gold'],
            weapon_name=json['weapon_name'],
            weapon_level=json['weapon_level'],
            start_weapon_name=json['start_weapon_name']
        )
    
    def __str__(self):
        return f"Gold: {self.gold}, Weapon Name: {self.weapon_name}, Weapon Level: {self.weapon_level}, Start Weapon Name: {self.start_weapon_name}"
   
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, GameState):
            return False
        return self.gold == value.gold and self.weapon_name == value.weapon_name and self.weapon_level == value.weapon_level and self.start_weapon_name == value.start_weapon_name


class DecisionType(Enum):
    ENHANCE = "ENHANCE"
    SELL = "SELL"
    STOP = "STOP"


class DecisionMaker(ABC):
    
    def __init__(self, desc = "DecisionMaker"):
        self.state = GameState(0, None, 0)
        self.actions = []
        self.desc = desc

    def update_state(self, action: GameAction) -> bool:
        """
        상태 업데이트를 시도하고, 새 상태가 추가되었으면
        True를 반환, 새 상태가 추가되지 않았으면 False를 반환
        """
        if action is None:
            return False
        self.state.update_by_action(action)
        if len(self.actions) == 0:
            self.actions.append(action)
            return True
        if self.actions[-1] == action:
            return False
        self.actions.append(action)
        return True

    def get_state(self) -> GameState:
        return self.state
    
    def get_latest_action(self) -> GameAction:
        return self.actions[-1]
    
    @abstractmethod
    def make_decision(self) -> DecisionType:
        pass
    
    def to_json(self):
        return {
            'state': self.state.to_json(),
            'actions': [action.to_json() for action in self.actions]
        }
    
    def from_json(self, json):
        self.state = GameState.from_json(json['state'])
        self.actions = [GameAction.from_json(action) for action in json['actions']]
    
    def __str__(self):
        return f"Goal:{self.desc}\nState: {self.state}\nActions: {self.actions}"
        
class RareWeaponDecisionMaker(DecisionMaker):
    
    def __init__(self, desc = "레어 무기만 11강 이상 판매, 그 외 무기는 1강 이상 판매"):
        super().__init__(desc)
    
    def make_decision(self) -> DecisionType:
        if self.state.weapon_level >= 11 and self.state.is_rare_weapon():
            return DecisionType.SELL
        elif self.state.weapon_level >= 1 and not self.state.is_rare_weapon():
            return DecisionType.SELL
        else:
            return DecisionType.ENHANCE

class AllWeapon16DecisionMaker(DecisionMaker):
    
    def __init__(self, desc = "모든 무기를 16강 이상 달성 목표"):
        super().__init__(desc)
    
    def make_decision(self) -> DecisionType:
        if self.state.weapon_level >= 16:
            return DecisionType.STOP
        else:
            return DecisionType.ENHANCE
