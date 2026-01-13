"""
게임 자동화 스크립트
- 강화/판매 자동화
- 상태 추적 및 로깅
"""

import pyautogui
import time
import sys
import pyperclip
import json
import os
import platform
from decision_maker import DecisionMaker, DecisionType, GameAction, GameState, Hidden20DecisionMaker, RareWeaponDecisionMaker, TestDeleteDialog
from datetime import datetime
from pynput import mouse, keyboard

# 플랫폼 감지
IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

# 플랫폼별 단축키 키
CMD_KEY = 'command' if IS_MACOS else 'ctrl'

def click_mouse(x, y):
    """
    Moves the mouse to (x, y) and performs a left click.
    Windows에서는 더 안정적인 클릭을 위해 moveTo 후 click 사용
    """
    try:
        if IS_WINDOWS:
            # Windows에서는 moveTo 후 click이 더 안정적
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.05)
            pyautogui.click()
        else:
            pyautogui.click(x=x, y=y)
    except Exception as e:
        print(f"❌ 마우스 클릭 오류: {e}")

def clear_chat_history(more_button_position, chat_settings_position, export_position, delete_all_position, input_position):
    """
    대화 내용을 지우는 함수
    더보기 → 대화 내용 → 내보내기 → 모두 삭제 순서로 진행한 후 강제로 강화를 한번 실행합니다.
    
    Args:
        more_button_position: 더보기 버튼 위치 (x, y)
        chat_settings_position: 대화 내용 버튼 위치 (x, y)
        export_position: 대화 내용 내보내기 위치 (x, y)
        delete_all_position: 대화 내용 모두 삭제 위치 (x, y)
        input_position: 입력창 클릭 위치 (x, y)
    """
    try:
        print("🗑️ 대화 내용 지우는 중...")
        
        # 1. 더보기 버튼 위치 클릭
        print("   1. 더보기 버튼 클릭...")
        click_mouse(more_button_position[0], more_button_position[1])
        time.sleep(0.5)
        
        # 2. 대화 내용 버튼 위치 호버
        print("   2. 대화 내용 버튼 호버...")
        pyautogui.moveTo(chat_settings_position[0], chat_settings_position[1], duration=0.2)
        time.sleep(0.5)
        
        # 3. 대화 내용 내보내기 위치 호버
        print("   3. 대화 내용 내보내기 호버...")
        pyautogui.moveTo(export_position[0], export_position[1], duration=0.2)
        time.sleep(0.5)
        
        # 4. 대화 내용 모두 삭제 위치 클릭
        print("   4. 대화 내용 모두 삭제 클릭...")
        click_mouse(delete_all_position[0], delete_all_position[1])
        time.sleep(1.0)
        
        # 확인 버튼이 나타날 수 있으므로 Enter 키로 확인
        pyautogui.press('enter')
        time.sleep(0.5)
        
        print("✅ 대화 내용 지우기 완료")
        time.sleep(0.5)
        
        # 대화 내용 지운 후 강제로 강화 실행
        print("🔨 대화 내용 지운 후 강제 강화 실행...")
        execute_enhance(input_position)
        print("✅ 강제 강화 완료")
        
    except Exception as e:
        print(f"❌ 대화 내용 지우기 오류: {e}")

def get_mouse_position():
    """
    Prints the current mouse position.
    """
    print(pyautogui.position())

def calibrate():
    """
    캘리브레이션 시작
    사용자가 여러 곳을 클릭하여 좌표를 저장
    Returns:
        tuple: (카톡 메시지창 좌표, 메시지 입력창 좌표, 더보기 버튼, 대화 내용 버튼, 대화 내용 내보내기, 대화 내용 모두 삭제)
    """
    print("캘리브레이션을 시작합니다.")
    print_separator()
    
    clicked_position = [None]  # 리스트로 감싸서 내부 함수에서 수정 가능하도록
    
    def on_click(x, y, button, pressed):
        if pressed:
            clicked_position[0] = (x, y)
            return False  # 리스너 중지
    
    # 첫 번째 좌표: 카톡 메시지창 좌측 하단
    print("📍 카톡 메시지창 좌측 하단을 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    chat_log_position = clicked_position[0]
    print(f"✅ 카톡 메시지창 좌표: {chat_log_position}")
    
    # 두 번째 좌표: 메시지 입력창
    clicked_position[0] = None
    print("📍 메시지 입력창을 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    input_position = clicked_position[0]
    print(f"✅ 메시지 입력창 좌표: {input_position}")
    
    # 세 번째 좌표: 더보기 버튼
    clicked_position[0] = None
    print("📍 더보기 버튼을 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    more_button_position = clicked_position[0]
    print(f"✅ 더보기 버튼 좌표: {more_button_position}")
    
    # 네 번째 좌표: 대화 내용 버튼
    clicked_position[0] = None
    print("📍 대화 내용 버튼을 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    chat_settings_position = clicked_position[0]
    print(f"✅ 대화 내용 버튼 좌표: {chat_settings_position}")
    
    # 다섯 번째 좌표: 대화 내용 내보내기
    clicked_position[0] = None
    print("📍 대화 내용 내보내기를 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    export_position = clicked_position[0]
    print(f"✅ 대화 내용 내보내기 좌표: {export_position}")
    
    # 여섯 번째 좌표: 대화 내용 모두 삭제
    clicked_position[0] = None
    print("📍 대화 내용 모두 삭제를 클릭해주세요...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    delete_all_position = clicked_position[0]
    print(f"✅ 대화 내용 모두 삭제 좌표: {delete_all_position}")
    
    # config.json에 좌표 저장
    config = load_config()
    if config is None:
        config = {}
    
    config['chat_log_position'] = chat_log_position
    config['input_position'] = input_position
    config['more_button_position'] = more_button_position
    config['chat_settings_position'] = chat_settings_position
    config['export_position'] = export_position
    config['delete_all_position'] = delete_all_position
    
    if save_config(config):
        print("✅ 모든 좌표가 config.json에 저장되었습니다.")
    else:
        print("⚠️ 좌표를 config.json에 저장하지 못했습니다.")
    
    print_separator()
    print("✨ 캘리브레이션이 완료되었습니다!")
    print(f"   - 메시지창: {chat_log_position}")
    print(f"   - 입력창: {input_position}")
    print(f"   - 더보기 버튼: {more_button_position}")
    print(f"   - 대화 내용 버튼: {chat_settings_position}")
    print(f"   - 대화 내용 내보내기: {export_position}")
    print(f"   - 대화 내용 모두 삭제: {delete_all_position}")
    print_separator()
    
    return chat_log_position, input_position, more_button_position, chat_settings_position, export_position, delete_all_position

def copy_text_from_location(chat_log_position, skip_click=False, debug=False):
    """
    게임 채팅 로그를 클립보드로 복사하여 반환
    
    Args:
        skip_click: True면 마우스 클릭 생략 (이미 선택된 상태)
        debug: True면 디버깅 정보 출력
    """
    try:
        if not skip_click:
            # 채팅창 클릭
            if debug:
                print(f"🔍 채팅창 클릭: {chat_log_position}")
            click_mouse(chat_log_position[0], chat_log_position[1])
            time.sleep(0.5 if IS_WINDOWS else 0.2)  # Windows에서 더 긴 대기
        
        # 전체 선택 (Cmd+A / Ctrl+A)
        if debug:
            print("🔍 전체 선택 중...")
        pyautogui.hotkey(CMD_KEY, 'a')
        time.sleep(0.3 if IS_WINDOWS else 0.1)
        
        # 복사 (Cmd+C / Ctrl+C)
        if debug:
            print("🔍 복사 중...")
        pyautogui.hotkey(CMD_KEY, 'c')
        # Windows에서는 클립보드 복사가 더 오래 걸릴 수 있음
        time.sleep(0.5 if IS_WINDOWS else 0.1)  # Windows에서 더 긴 대기
        
        # 클립보드 내용 반환
        content = pyperclip.paste()
        
        if debug:
            print(f"🔍 클립보드 길이: {len(content) if content else 0}")
            if content:
                print(f"🔍 클립보드 앞부분 (100자): {content[:100]}")
        
        # Windows에서 클립보드가 비어있을 경우 재시도
        if IS_WINDOWS and (not content or len(content.strip()) == 0):
            if debug:
                print("🔍 클립보드가 비어있음. 재시도 중...")
            time.sleep(0.3)
            content = pyperclip.paste()
            if debug:
                print(f"🔍 재시도 후 클립보드 길이: {len(content) if content else 0}")
        
        # 여전히 비어있으면 한 번 더 시도
        if IS_WINDOWS and (not content or len(content.strip()) == 0):
            if debug:
                print("🔍 클립보드가 여전히 비어있음. 최종 재시도 중...")
            # 다시 선택 및 복사 시도
            pyautogui.hotkey(CMD_KEY, 'a')
            time.sleep(0.2)
            pyautogui.hotkey(CMD_KEY, 'c')
            time.sleep(0.5)
            content = pyperclip.paste()
            if debug:
                print(f"🔍 최종 재시도 후 클립보드 길이: {len(content) if content else 0}")
        
        return content
        
    except Exception as e:
        print(f"❌ 로그 복사 오류: {e}")
        import traceback
        if debug:
            traceback.print_exc()
        return ""

def load_config():
    """
    config.json 파일에서 설정을 로드합니다.
    파일이 없으면 None을 반환합니다.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ config.json 파일 읽기 오류: {e}")
            return None
    return None

def save_config(config):
    """
    설정을 config.json 파일에 저장합니다.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ config.json 파일 저장 오류: {e}")
        return False

def get_username():
    """
    사용자 이름을 가져옵니다.
    1. config.json에서 읽기 시도
    2. 없으면 사용자에게 입력 받기
    3. 입력받은 값을 config.json에 저장
    """
    config = load_config()
    
    if config and 'username' in config:
        username = config['username']
        print(f"✅ 설정 파일에서 사용자 이름을 불러왔습니다: {username}")
        return username
    
    # config 파일이 없거나 username이 없으면 입력 받기
    print_separator()
    print("사용자 이름 설정")
    print_separator()
    username = input("카카오톡에서 사용할 사용자 이름을 입력하세요 (예: 이기범): ").strip()
    
    if not username:
        print("⚠️ 사용자 이름이 입력되지 않았습니다. 기본값 '이기범'을 사용합니다.")
        username = "이기범"
    
    # config 파일에 저장 (기존 config 유지)
    if config is None:
        config = {}
    config['username'] = username
    if save_config(config):
        print(f"✅ 사용자 이름 '{username}'이(가) config.json에 저장되었습니다.")
    else:
        print(f"⚠️ 사용자 이름 '{username}'을(를) config.json에 저장하지 못했습니다.")
    
    print_separator()
    return username

def load_positions_from_config():
    """
    config.json에서 좌표를 읽어옵니다.
    Returns:
        tuple: (chat_log_position, input_position, more_button_position, chat_settings_position, export_position, delete_all_position)
        또는 None (모든 좌표가 없을 경우)
    """
    config = load_config()
    
    if config is None:
        return None
    
    required_keys = ['chat_log_position', 'input_position', 'more_button_position', 
                     'chat_settings_position', 'export_position', 'delete_all_position']
    
    # 모든 필수 좌표가 있는지 확인
    if all(key in config for key in required_keys):
        try:
            # 튜플로 변환 (리스트로 저장되어 있을 수 있음)
            chat_log_position = tuple(config['chat_log_position'])
            input_position = tuple(config['input_position'])
            more_button_position = tuple(config['more_button_position'])
            chat_settings_position = tuple(config['chat_settings_position'])
            export_position = tuple(config['export_position'])
            delete_all_position = tuple(config['delete_all_position'])
            
            print("✅ config.json에서 모든 좌표를 불러왔습니다.")
            return (chat_log_position, input_position, more_button_position, 
                   chat_settings_position, export_position, delete_all_position)
        except Exception as e:
            print(f"⚠️ config.json에서 좌표를 읽는 중 오류: {e}")
            return None
    
    return None

def split_messages(text: str, username: str) -> list:
    """
    텍스트를 메시지 기준으로 분리하여 반환
    
    Args:
        text: 채팅 로그 텍스트
        username: 사용자 이름 (예: "이기범")
    """
    messages = text.split(f'@{username}')
    messages = [message.strip() for message in messages if '💬' in message]
    return messages

def get_latest_action(text: str, username: str) -> GameAction:
    """
    가장 최근 메시지를 반환
    
    Args:
        text: 채팅 로그 텍스트
        username: 사용자 이름
    """
    messages = split_messages(text, username)
    
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
        # 입력창 클릭하여 포커스 확보
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.3 if IS_WINDOWS else 0.1)
        
        # Windows와 Mac 모두 직접 입력 방식 사용
        pyautogui.write('/rkd', interval=0.1)
        time.sleep(0.2)
        
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('enter')
        # 게임 응답을 기다림
        time.sleep(1.0)

        
    except Exception as e:
        print(f"❌ 강화 명령 오류: {e}")

def execute_sell(input_position):
    """
    판매 명령 실행 (/vksao -> /판매)
    """
    try:
        # 입력창 클릭하여 포커스 확보
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.3 if IS_WINDOWS else 0.1)
        
        # Windows와 Mac 모두 직접 입력 방식 사용
        pyautogui.write('/vks', interval=0.1)
        time.sleep(0.2)
        
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('enter')
        # 게임 응답을 기다림
        time.sleep(1.0)
        
        
    except Exception as e:
        print(f"❌ 판매 명령 오류: {e}")

def execute_profile(input_position):
    """
    프로필 명령 실행 (/vmfhvlf -> /프로필)
    """
    try:
        # 입력창 클릭하여 포커스 확보
        click_mouse(input_position[0], input_position[1])
        time.sleep(0.4 if IS_WINDOWS else 0.2)
        
        # Windows와 Mac 모두 직접 입력 방식 사용
        pyautogui.write('/vmfhvlf', interval=0.02)
        time.sleep(0.5)
        
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('enter')
        # 게임 응답을 기다림
        time.sleep(1.0)
        
        
    except Exception as e:
        print(f"❌ 프로필 명령 오류: {e}")

def print_separator(char='='):
    """구분선 출력"""
    print(char * 80)

# 전역 변수: 초기 마우스 위치 및 종료 플래그
initial_mouse_x = None
initial_mouse_y = None
should_stop = False
keyboard_listener = None

def on_key_press(key):
    """키보드 입력 감지 - F9 키를 누르면 종료"""
    global should_stop
    try:
        # F9 키 감지
        if hasattr(key, 'name') and key.name == 'f9':
            should_stop = True
            print("\n🛑 F9 키를 눌러 종료 신호를 받았습니다.")
            return False  # 리스너 종료
    except AttributeError:
        pass

def init_mouse_position():
    """초기 마우스 위치를 저장합니다."""
    global initial_mouse_x, initial_mouse_y
    pos = pyautogui.position()
    initial_mouse_x = pos[0]
    initial_mouse_y = pos[1]

def start_keyboard_listener():
    """키보드 리스너 시작"""
    global keyboard_listener
    try:
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        keyboard_listener.start()
    except Exception as e:
        print(f"⚠️ 키보드 리스너 시작 실패: {e}")

def stop_keyboard_listener():
    """키보드 리스너 종료"""
    global keyboard_listener
    if keyboard_listener:
        try:
            keyboard_listener.stop()
        except:
            pass

def stop_condition() -> bool:
    """종료 조건 확인 (키보드 F9 또는 마우스 이동)"""
    global should_stop, initial_mouse_x, initial_mouse_y
    
    # 키보드 종료 신호 확인
    if should_stop:
        return True
    
    # 마우스 이동 확인 (화면 모서리로 이동했는지 확인)
    if initial_mouse_x is None or initial_mouse_y is None:
        return False
    
    current_pos = pyautogui.position()
    screen_width, screen_height = pyautogui.size()
    
    # 화면 모서리로 이동했는지 확인 (좌상단 10x10 영역 또는 우상단 10x10 영역)
    if (current_pos[0] < 10 and current_pos[1] < 10) or \
       (current_pos[0] > screen_width - 10 and current_pos[1] < 10):
        return True
    
    # 좌우로 500픽셀 이상 이동 확인
    current_x = current_pos[0]
    move_distance = abs(current_x - initial_mouse_x)
    if move_distance >= 500:
        return True
    
    return False

def automation_loop(chat_log_position, input_position, username, more_button_position, chat_settings_position, export_position, delete_all_position):
    """자동화 메인 루프"""
    # 초기 마우스 위치 저장
    init_mouse_position()
    initial_pos = pyautogui.position()
    print(f"📍 초기 마우스 위치: {initial_pos}")
    print("💡 종료하려면 마우스를 좌우로 500픽셀 이상 이동하세요.")
    
    print_separator()
    print("매크로 시작")
    print_separator()
    
    dm = Hidden20DecisionMaker()
    # dm = TestDeleteDialog()
    print(f'전략: {dm.desc}')
    
    # 대화 내용 지우기 타이머 (1시간 = 3600초)
    last_clear_time = time.time()
    clear_interval = 3600.0  # 1시간
    
    print_separator()
    # 초기 상태 동기화
    print("\n🔄 현재 상태 확인 중...")
    while True:
        try:
            initial_text = copy_text_from_location(chat_log_position, debug=False)
            if not initial_text or len(initial_text.strip()) == 0:
                print("⚠️ 클립보드가 비어있습니다. 카카오톡 메시지창이 선택되어 있는지 확인하세요.")
                print("   - 메시지창을 클릭한 후 잠시 기다려주세요.")
                time.sleep(2)
                continue
            
            current_action = get_latest_action(initial_text, username)
            break
        except Exception as e:
            print(f"❌ 초기 상태 확인 오류: {e}")
            if 'initial_text' in locals() and initial_text:
                print(f"   클립보드 내용 샘플: {initial_text[:200]}")
            time.sleep(1)
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

    # execute 후 마우스 위치가 변경되었을 수 있으므로 초기 위치 업데이트
    init_mouse_position()
    
    # 디버깅: stop_condition 상태 확인
    if stop_condition():
        print_separator()
        print("⚠️ execute 후 stop_condition()이 True입니다. 프로그램을 종료합니다.")
        print_separator()
        return

    while not stop_condition():
        # 1시간마다 대화 내용 지우기
        current_time = time.time()
        if current_time - last_clear_time >= clear_interval:
            clear_chat_history(more_button_position, chat_settings_position, export_position, delete_all_position, input_position)
            last_clear_time = current_time
        
        while not stop_condition():
            # 새 상태 업데이트 될 때까지 대기
            while True:
                # 마우스 이동 확인
                if stop_condition():
                    print_separator()
                    if should_stop:
                        print("🛑 F9 키를 눌러 프로그램을 종료합니다.")
                    else:
                        print("🛑 종료 조건이 충족되어 프로그램을 종료합니다.")
                    print_separator()
                    stop_keyboard_listener()
                    return
                
                try:
                    initial_text = copy_text_from_location(chat_log_position, debug=False)
                    if not initial_text or len(initial_text.strip()) == 0:
                        print("⚠️ 클립보드가 비어있습니다. 재시도 중...")
                        time.sleep(1)
                        continue
                    
                    # 명령어만 있고 게임 응답이 없는 경우 감지
                    # 텍스트의 마지막 부분(약 200자)에서 '/판' 또는 '/강' 확인
                    text_end = initial_text[-200:] if len(initial_text) > 200 else initial_text
                    
                    # 마지막 두 글자가 '/판' 또는 '/강'인지 확인
                    if text_end.rstrip().endswith('/판') or text_end.rstrip().endswith('/강'):
                        print("⚠️ 명령어 입력 중 감지. 다음 단계로 진행합니다.")
                        # current_action을 None으로 설정하여 상태 업데이트를 건너뛰고 다음 액션으로 진행
                        current_action = None
                        break
                    
                    text_stripped = initial_text.strip()
                    
                    is_command_only = (text_stripped in ['/판매', '/강화', '/프로필'] or 
                                      (len(text_stripped) < 100 and 
                                       not any(keyword in initial_text for keyword in 
                                              ['💥강화 파괴💥', '💦강화 유지💦', '✨강화 성공✨', 
                                               '판매〗', '💰', '💸', '💶', '⚔️', '『', '』'])))
                    
                    if is_command_only:
                        print("⏳ 게임 응답 대기 중... (클립보드에 명령어만 있음)")
                        time.sleep(1.5)
                        continue
                    
                    current_action = get_latest_action(initial_text, username)
                    break
                except Exception as e:
                    error_msg = str(e)
                    # "액션이 없습니다" 오류인 경우 게임 응답 대기
                    if "액션이 없습니다" in error_msg:
                        if 'initial_text' in locals() and initial_text:
                            text_stripped = initial_text.strip()
                            # 명령어만 있는 경우 대기
                            if text_stripped in ['/판매', '/강화', '/프로필'] or len(text_stripped) < 100:
                                print("⏳ 게임 응답 대기 중... (액션을 찾을 수 없음)")
                                time.sleep(1.5)
                                continue
                    print(f"❌ 상태 확인 오류: {e}")
                    if 'initial_text' in locals() and initial_text:
                        print(f"   클립보드 내용 샘플: {initial_text[:200]}")
                    time.sleep(1)
            
            # '/판' 또는 '/강'만 있는 경우 current_action이 None일 수 있음
            if 'current_action' not in locals() or current_action is None:
                if 'current_action' in locals() and current_action is None:
                    print("⚠️ 명령어 입력 중으로 인해 상태 업데이트를 건너뜁니다.")
                # 다음 액션으로 진행하기 위해 바깥 루프 break
                break
            
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
            print_separator()
            if should_stop:
                print("🛑 F9 키를 눌러 프로그램을 종료합니다.")
            else:
                print("🛑 종료 조건이 충족되어 프로그램을 종료합니다.")
            print_separator()
            stop_keyboard_listener()
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
    
    # 접근성 권한 확인 및 테스트
    print("🔐 접근성 권한 확인 중...")
    print_separator()
    
    try:
        # 현재 마우스 위치 저장
        original_pos = pyautogui.position()
        print(f"현재 마우스 위치: {original_pos}")
        
        # 실제 마우스 이동 테스트 (화면 안전한 위치로)
        test_x, test_y = 100, 100
        pyautogui.moveTo(test_x, test_y, duration=0.1)
        time.sleep(0.1)
        
        # 이동이 실제로 되었는지 확인
        new_pos = pyautogui.position()
        if abs(new_pos[0] - test_x) > 10 or abs(new_pos[1] - test_y) > 10:
            raise Exception("마우스 이동이 작동하지 않습니다")
        
        # 원래 위치로 복귀
        pyautogui.moveTo(original_pos[0], original_pos[1], duration=0.1)
        time.sleep(0.1)
        
        print("✅ 접근성 권한 확인 완료 - 마우스/키보드 제어 가능")
        print_separator()
        
    except Exception as e:
        print(f"❌ 접근성 권한 테스트 실패: {e}")
        print_separator()
        
        if IS_MACOS:
            print("❌ 마우스/키보드 접근성 권한이 필요합니다!")
            print("")
            print("📋 설정 방법:")
            print("  1. 시스템 설정 열기")
            print("  2. '개인 정보 보호 및 보안' 클릭")
            print("  3. '손쉬운 사용' (또는 '접근성') 클릭")
            print("  4. '터미널' 또는 'Terminal.app' 찾기")
            print("  5. 체크박스를 활성화 (✓)")
            print("")
            print("💡 참고: macOS 한국어 버전에서는 '손쉬운 사용'으로 표시됩니다.")
            print("")
            print("⚠️ 중요: 권한을 부여한 후 터미널을 완전히 종료하고 다시 실행해야 합니다!")
            print("")
            print("시스템 설정을 지금 열까요? (y/n): ", end='')
            try:
                response = input().strip().lower()
                if response == 'y':
                    import subprocess
                    subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
                    print("")
                    print("시스템 설정을 열었습니다.")
                    print("권한을 활성화한 후 터미널을 완전히 종료하고 프로그램을 다시 실행해주세요.")
            except:
                pass
        elif IS_WINDOWS:
            print("❌ 마우스/키보드 제어 권한이 필요할 수 있습니다!")
            print("")
            print("📋 Windows 설정 방법:")
            print("  1. 제어판 → 접근성 센터 열기")
            print("  2. 또는 Windows 설정 → 접근성")
            print("  3. 관리자 권한으로 실행할 수도 있습니다")
            print("")
            print("💡 대부분의 경우 Windows에서는 추가 설정이 필요하지 않습니다.")
           
            print("   문제가 지속되면 관리자 권한으로 실행해보세요.")
        else:
            print("❌ 마우스/키보드 제어 권한이 필요합니다!")
            print("   시스템 설정에서 접근성 권한을 확인해주세요.")
        
        sys.exit(1)
    
    # 사용자 이름 가져오기 (config 파일 또는 입력)
    username = get_username()
    
    # config.json에서 좌표 읽기 시도
    positions = load_positions_from_config()
    if positions:
        chat_log_position, input_position, more_button_position, chat_settings_position, export_position, delete_all_position = positions
        print("✅ 저장된 좌표를 사용합니다.")
    else:
        print("⚠️ config.json에 좌표가 없습니다. 캘리브레이션을 진행합니다.")
        chat_log_position, input_position, more_button_position, chat_settings_position, export_position, delete_all_position = calibrate()
    
    print_separator()
    print("⚠️ 중지하려면 마우스를 좌우로 500픽셀 이상 이동하세요.")
    print_separator()
    
    try:
        automation_loop(chat_log_position, input_position, username, more_button_position, chat_settings_position, export_position, delete_all_position)
    except KeyboardInterrupt:
        print("\n\n 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_keyboard_listener()
        print("프로그램을 종료합니다.")
