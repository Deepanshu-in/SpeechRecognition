from datetime import datetime, timedelta

def parse_time(time_str):
    return datetime.strptime(time_str, '%I:%M %p')

def calculate_minutes(start, end):
    delta = end - start
    return delta.seconds // 60

def check_rule_violations(member, start, end, age, daily_limit):
    violations = []
    session_minutes = calculate_minutes(start, end)
    
    if session_minutes > 120:
        violations.append(f"{member} exceeded 2-hour session limit.")
    
    if age <= 12 and end.hour >= 21:
        violations.append(f"{member} watched TV past 9 PM.")
    
    if session_minutes > daily_limit:
        violations.append(f"{member} exceeded daily screen time preference.")
    
    return violations

def resolve_conflicts(strategy, sessions):
    if strategy == 'first-come-first-served':
        return sorted(sessions, key=lambda x: x['start'])
    elif strategy == 'shortest-session-first':
        return sorted(sessions, key=lambda x: x['duration'])
    elif strategy == 'least-screen-time-first':
        return sorted(sessions, key=lambda x: x['total_time'])
    return sessions

def tv_time_tracker(family, logs, carry_over=False, conflict_strategy='first-come-first-served'):
    report = {}
    for member in family:
        report[member['name']] = {
            'total_time': 0,
            'violations': [],
            'conflicts': []
        }
    
    for log in logs:
        member_name = log['name']
        start_time = parse_time(log['start'])
        end_time = parse_time(log['end'])
        age = next(member['age'] for member in family if member['name'] == member_name)
        daily_limit = next(member['daily_limit'] for member in family if member['name'] == member_name)
        
        violations = check_rule_violations(member_name, start_time, end_time, age, daily_limit)
        report[member_name]['violations'].extend(violations)
        
        session_minutes = calculate_minutes(start_time, end_time)
        report[member_name]['total_time'] += session_minutes
        
        if carry_over and report[member_name]['total_time'] > daily_limit:
            report[member_name]['total_time'] = daily_limit
    
    # Conflict resolution
    for day in set(log['day'] for log in logs):
        day_sessions = [log for log in logs if log['day'] == day]
        for i, session in enumerate(day_sessions):
            session_start = parse_time(session['start'])
            session_end = parse_time(session['end'])
            session_duration = calculate_minutes(session_start, session_end)
            session['duration'] = session_duration
            session['total_time'] = report[session['name']]['total_time']
            
            for other_session in day_sessions[i+1:]:
                other_start = parse_time(other_session['start'])
                other_end = parse_time(other_session['end'])
                
                if (session_start < other_end and session_end > other_start):
                    report[session['name']]['conflicts'].append(f"Conflict with {other_session['name']} on {day}")
                    report[other_session['name']]['conflicts'].append(f"Conflict with {session['name']} on {day}")
        
        resolved_sessions = resolve_conflicts(conflict_strategy, day_sessions)
        for session in resolved_sessions:
            report[session['name']]['total_time'] = min(session['total_time'], session['duration'])
    
    return report

# Example usage
family = [
    {'name': 'Amit', 'age': 15, 'daily_limit': 180},
    {'name': 'Sita', 'age': 10, 'daily_limit': 120},
    {'name': 'Ravi', 'age': 8, 'daily_limit': 90}
]

logs = [
    {'name': 'Amit', 'day': 'Monday', 'start': '5:00 PM', 'end': '7:00 PM'},
    {'name': 'Sita', 'day': 'Monday', 'start': '6:30 PM', 'end': '8:30 PM'},
    {'name': 'Ravi', 'day': 'Monday', 'start': '8:00 PM', 'end': '9:30 PM'}
]

report = tv_time_tracker(family, logs, carry_over=True, conflict_strategy='first-come-first-served')
print(report)