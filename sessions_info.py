import os
from time import time


def last_used_session():
    """
    Первый аргумент: имя самой отлежавшейся сессии
    Второй аргумент: список сессий с названием сессии и последним её использованием
    """
    sessions_data = []
    for session_name in [f for f in os.listdir('sessions') if f.endswith('.session')]:
        session_name = session_name.replace('.session', '')
        with open(f'sessions/{session_name}_time.json', 'r') as f:
            sessions_data.append(eval(f.read()))

    last_used_session = ((min(sessions_data, key=lambda x: x['used_at']))['session_name']).replace('.session', '')
    with open(f'sessions/{last_used_session}_time.json', 'w') as f:
        f.write(str({'session_name': last_used_session, 'used_at': time()}))
    return last_used_session, sessions_data


def generate_time_for_sessions():
    """
    Генерирует json'ы с временем последнего использования для сессий
    """
    for session_name in [f for f in os.listdir('sessions') if f.endswith('.session')]:
        session_name = session_name.replace('.session', '')
        with open(f'sessions/{session_name}_time.json', 'w+') as f:
            time_info = {'session_name': session_name, 'used_at': time()}
            f.write(str(time_info))


