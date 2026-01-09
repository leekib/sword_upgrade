"""
게임 자동화 스크립트
- 강화/판매 자동화
- 상태 추적 및 로깅
"""

import pyautogui
import time
import sys
import pyperclip
from decision_maker import DecisionMaker, DecisionType, GameAction, GameState, RareWeaponDecisionMaker
from datetime import datetime
from pynput import mouse

def click_mouse(x, y):
    """
    Moves the mouse to (x, y) and performs a left click.
    """
    try:
        pyautogui.click(x=x, y=y)
    except Exception as e:
        print(f"❌ 마우스 클릭 오류: {e}")

def get_mouse_position():
    """
    Prints the current mouse position.
    """
    print(pyautogui.position())

def calibrate():
    """
    캘리브레이션 시작
    사용자가 두 곳을 클릭하여 좌표를 저장
    Returns:
        tuple: (카톡 메시지창 좌측 하단 좌표, 메시지 입력창 좌표)
    """
    print("캘리브레이션을 시작합니다.")
    print_separator()
    
    # 첫 번째 좌표: 카톡 메시지창 좌측 하단
    clicked_position = [None]  # 리스트로 감싸서 내부 함수에서 수정 가능하도록
    
    def on_click(x, y, button, pressed):
        if pressed:
            clicked_position[0] = (x, y)
            return False  # 리스너 중지
    
    print("📍 카톡 메시지창 좌측 하단을 클릭해주세요...")
    
    # 마우스 클릭 리스너 시작
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    
    chat_log_position = clicked_position[0]
    print(f"✅ 카톡 메시지창 좌표: {chat_log_position}")
    
    # 두 번째 좌표: 메시지 입력창
    clicked_position[0] = None
    
    print("📍 메시지 입력창을 클릭해주세요...")
    
    # 마우스 클릭 리스너 시작
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    
    input_position = clicked_position[0]
    print(f"✅ 메시지 입력창 좌표: {input_position}")
    
    print_separator()
    print("✨ 캘리브레이션이 완료되었습니다!")
    print(f"   - 메시지창: {chat_log_position}")
    print(f"   - 입력창: {input_position}")
    print_separator()
    
    return chat_log_position, input_position

def copy_text_from_location(chat_log_position, skip_click=False):
    """
    게임 채팅 로그를 클립보드로 복사하여 반환
    
    Args:
        skip_click: True면 마우스 클릭 생략 (이미 선택된 상태)
    """
    try:
        if not skip_click:
            # 채팅창 클릭
            click_mouse(chat_log_position[0], chat_log_position[1])
            time.sleep(0.2)
        
        # 전체 선택 (Cmd+A)
        pyautogui.hotkey('command', 'a')
        time.sleep(0.1)
        
        # 복사 (Cmd+C)
        pyautogui.hotkey('command', 'c')
        time.sleep(0.1)
        
        # 클립보드 내용 반환
        content = pyperclip.paste()
        return content
        
    except Exception as e:
        print(f"❌ 로그 복사 오류: {e}")
        return ""

def split_messages(text: str) -> list:
    """
    텍스트를 메시지 기준으로 분리하여 반환
    """
    messages = text.split('@이기범')
    messages = [message.strip() for message in messages if '💬' in message]
    return messages

def get_latest_action(text: str) -> GameAction:
    """
    가장 최근 메시지를 반환
    """
    messages = split_messages(text)
    
    if len(messages) == 0:
        raise Exception("메시지가 없습니다.")
    
    messages.reverse()
    
    for message in messages:
        action = GameAction.from_text(message)
        if action is not None:
            return action
    
    raise Exception("액션이 없습니다.")


def execute_enhance(input_position):
    """
    강화 명령 실행 (/rkdghk -> /강화)
    """
    try:
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.1)
        
        pyautogui.write('/rkdghk', interval=0.01)
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.05)
        pyautogui.press('enter')

        
    except Exception as e:
        print(f"❌ 강화 명령 오류: {e}")

def execute_sell(input_position):
    """
    판매 명령 실행 (/vksao -> /판매)
    """
    try:
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.1)
        
        pyautogui.write('/vksao', interval=0.01)
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.05)
        pyautogui.press('enter')
        
        
    except Exception as e:
        print(f"❌ 판매 명령 오류: {e}")

def execute_profile(input_position):
    """
    프로필 명령 실행 (/vmfhvlf -> /프로필)
    """
    try:
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.2)
        
        pyautogui.write('/vmfhvlf', interval=0.02)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.1)
        pyautogui.press('enter')
        
        
    except Exception as e:
        print(f"❌ 프로필 명령 오류: {e}")

def print_separator(char='='):
    """구분선 출력"""
    print(char * 80)

def stop_condition() -> bool:
    """마우스 위치 확인 (x > 100이면 중지)"""
    mouse_x, mouse_y = pyautogui.position()
    return mouse_x > 100

def automation_loop(chat_log_position, input_position):
    """자동화 메인 루프"""
    print_separator()
    print("매크로 시작")
    print_separator()
    
    dm = RareWeaponDecisionMaker()
    print(f'전략: {dm.desc}')
    
    print_separator()
    # 초기 상태 동기화
    print("\n🔄 현재 상태 확인 중...")
    initial_text = copy_text_from_location(chat_log_position)
    current_action = get_latest_action(initial_text)
    print_separator()
    dm.update_state(current_action)
    print(f"현재 상태: {dm.get_state()}")
    print_separator()
    decision = dm.make_decision()
    print(f"전략: {dm.desc}\n결정: {decision}")
    
    if decision == DecisionType.ENHANCE:
        execute_enhance(input_position)
    elif decision == DecisionType.SELL:
        execute_sell(input_position)
    elif decision == DecisionType.STOP:
        print("중지 명령 실행")
        return

    while not stop_condition():
        while not stop_condition():
            # 새 상태 업데이트 될 때까지 대기
            initial_text = copy_text_from_location(chat_log_position)
            current_action = get_latest_action(initial_text)
            if dm.update_state(current_action):
                print_separator()
                latest_action = dm.get_latest_action()
                print(f"[{latest_action.action_type}]")
                current_state = dm.get_state()
                print(f"현재 무기: {current_state.weapon_name}[+{current_state.weapon_level}]", end=" ")
                print(f"({'레어' if current_state.is_rare_weapon() else '일반'})")
                print(f"남은 골드: {current_state.gold}")
                break
        if stop_condition():
            break
        print_separator('-')
        decision = dm.make_decision()
        print(f"전략: {dm.desc}\n결정: {decision}")
        if decision == DecisionType.ENHANCE:
            execute_enhance(input_position)
        elif decision == DecisionType.SELL:
            execute_sell(input_position)
        print_separator()
if __name__ == "__main__":
    # Fail-safe: 마우스를 화면 왼쪽 상단으로 이동하면 프로그램 중단
    pyautogui.FAILSAFE = True
    print_separator()
    chat_log_position, input_position = calibrate()
    
    print_separator()
    print("⚠️ 중지하려면 마우스를 화면 우측으로 이동하세요. (x > 100)")
    print_separator()
    
    try:
        automation_loop(chat_log_position, input_position)
    except KeyboardInterrupt:
        print("\n\n 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("프로그램을 종료합니다.")
