import requests
import csv
import sys

# When given an api-key, do a custom query
# string -> csv
def mainloop():
    args = sys.argv
    key = args[1]

    params = get_params(key)
    teams = get_teams(['Big Ten','Pac-12','AFC','NFC'], params)
    games = get_games(teams, params)
    output = filter_plays(games, params)

    with open('CustomRequest.csv', 'w', newline ='') as f:
        writer = csv.writer(f)
        writer.writerows(output)

# Turn an api key into a jwt key and format as header
# str -> {str: str}
def get_params (key):
    params = {'x-api-key':key}
    r = requests.post('https://api.profootballfocus.com/auth/login', headers = params)
    jwt = r.json()['jwt']
    params = {'Authorization':'Bearer ' + jwt}
    return params

def get_teams (names, params):
    # For this custom query we want LSU, B1G, P12, and NFL
    teams = ['LAST']
    
    r = requests.get('https://api.profootballfocus.com/v1/ncaa/2019/teams', headers = params)
    for team in r.json()['teams']:
        for group in team['groups']:
            if group['name'] in names:
                teams.append(team['gsis_abbreviation'])
                
    r = requests.get('https://api.profootballfocus.com/v1/nfl/2019/teams', headers = params)
    for team in r.json()['teams']:
        for group in team['groups']:
            if group['name'] in names:
                teams.append(team['abbreviation'])
    
    
    return teams

# For B1G opponents, return all game ids in which they played in 2019
# And report the id first, then winning team, then the losing team
# str, {str: str} -> listof str
def get_games (opponents, params):
    possible_games = []
    r = requests.get('https://api.profootballfocus.com/v1/video/ncaa/games', headers = params)
    possible_games += r.json()['games']
    r = requests.get('https://api.profootballfocus.com/v1/video/nfl/games', headers = params)
    possible_games += r.json()['games']
    games = []

    for game in possible_games:
        if game['away_team'] in opponents or game['home_team'] in opponents:
            if game['season'] == 2019:
                games.append(str(game['id']))
    return games

# Only get plays with certain values
# listof str, str -> listof str
def filter_plays(games, params):
    play_ids = []
    for game in games:
        row = game
        r = requests.get('https://api.profootballfocus.com/v1/video/ncaa/games/'
                         +game+'/plays', headers = params)

        if 'plays' not in r.json().keys():
            r = requests.get('https://api.profootballfocus.com/v1/video/nfl/games/'
                         +game+'/plays', headers = params)
        
        if 'plays' not in r.json().keys():
            continue
        plays = r.json()['plays']
        for play in plays:
            if ((play['pass_route_target_group'] in ['7R','H7'])
                and play['pass_receiver_target_position'] != None):
                if('HB' in play['pass_receiver_target_position']):
                    print(play['play_id'], play['defense'])
                    play_ids.append([play['play_id'],play['pass_route_target_group'],play['pass_route_target']])

    return play_ids

mainloop()
