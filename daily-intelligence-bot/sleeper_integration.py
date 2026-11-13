"""Read-only Sleeper NFL roster sync and fantasy news keyword builder."""
from __future__ import annotations
import os
import logging
from pathlib import Path
import requests
import yaml

BASE = 'https://api.sleeper.app/v1'
LOG = logging.getLogger(__name__)
HEADERS = {'User-Agent': 'PersonalDailyBriefing/1.1 (noncommercial read-only roster synchronization)'}


def api(path):
    response = requests.get(BASE + path, headers=HEADERS, timeout=18)
    response.raise_for_status()
    return response.json()


def _names(player_ids, player_map):
    output=[]
    for ident in player_ids or []:
        obj = player_map.get(str(ident), {})
        name = obj.get('full_name') or ' '.join(filter(None,[obj.get('first_name'),obj.get('last_name')]))
        output.append({'id':str(ident), 'name':name or str(ident),
                       'team':obj.get('team') or '', 'position':obj.get('position') or '',
                       'injury_status':obj.get('injury_status') or ''})
    return output


def football_rosters(username, season, selected_ids=None):
    """Fetch all own NFL leagues by username. No authentication or writes."""
    user=api('/user/' + requests.utils.quote(username, safe=''))
    if not user or not user.get('user_id'):
        raise ValueError('Sleeper username not found')
    uid=str(user['user_id'])
    leagues=api(f'/user/{uid}/leagues/nfl/{int(season)}') or []
    selected=set(str(i) for i in (selected_ids or []) if str(i).strip())
    leagues=[league for league in leagues if not selected or str(league.get('league_id')) in selected]
    if not leagues: return []
    # Sleeper requests caching this bulky dictionary: one request at most per run/day.
    players=api('/players/nfl')
    output=[]
    for league in leagues:
        lid=str(league['league_id'])
        rosters=api(f'/league/{lid}/rosters') or []
        own=next((r for r in rosters if str(r.get('owner_id'))==uid or uid in [str(x) for x in (r.get('co_owners') or [])]),None)
        if own is None:
            LOG.warning('No team owned by username in league %s',lid)
            continue
        player_ids=[str(p) for p in (own.get('players') or [])]
        starters=[str(p) for p in (own.get('starters') or []) if str(p) != '0']
        output.append({'league':league.get('name','Unnamed league'), 'league_id':lid,
            'sport':'nfl','roster_id':own.get('roster_id'),
            'players':_names(player_ids, players), 'starters':starters,
            'reserve':[str(p) for p in (own.get('reserve') or [])],
            'taxi':[str(p) for p in (own.get('taxi') or [])]})
    return output


def basketball_rosters(path=None):
    """Manually supplied NBA names. No claims of Sleeper NBA API support."""
    source=Path(path or Path(__file__).parent / 'fantasy_rosters.yaml')
    if not source.exists(): return []
    data=yaml.safe_load(source.read_text(encoding='utf8')) or {}
    basketball=data.get('basketball') or []
    out=[]
    for team in basketball:
        if not isinstance(team,dict): continue
        players=[]
        for p in team.get('players') or []:
            if isinstance(p,str): players.append({'name':p,'id':'','team':'','position':'','injury_status':''})
            elif isinstance(p,dict) and p.get('name'):
                players.append({'name':str(p['name']),'id':'','team':str(p.get('team','')),
                                'position':str(p.get('position','')),'injury_status':''})
        if players: out.append({'league':team.get('league','Basketball fantasy'), 'league_id':'manual',
                               'sport':'nba','players':players,'starters':[],'reserve':[],'taxi':[]})
    return out


def fetch_fantasy():
    result={'nfl':[], 'nba':[], 'warnings':[]}
    name=os.getenv('SLEEPER_USERNAME','').strip()
    if name:
        try:
            season=int(os.getenv('SLEEPER_NFL_SEASON','2026'))
            ids=[x.strip() for x in os.getenv('SLEEPER_NFL_LEAGUE_IDS','').split(',') if x.strip()]
            result['nfl']=football_rosters(name,season,ids)
            if not result['nfl']: result['warnings'].append('Sleeper NFL: no owned rosters found in the selected season/leagues')
        except (ValueError,requests.RequestException,KeyError,TypeError) as exc:
            LOG.warning('Sleeper sync failed: %s',type(exc).__name__)
            result['warnings'].append('Sleeper NFL roster sync unavailable; check username/season/connectivity')
    else:
        result['warnings'].append('Sleeper NFL not configured (set SLEEPER_USERNAME)')
    try: result['nba']=basketball_rosters()
    except (OSError,ValueError,yaml.YAMLError) as exc:
        LOG.warning('Basketball roster read failed: %s',type(exc).__name__)
        result['warnings'].append('Basketball roster configuration unreadable')
    return result


def roster_names(fantasy, sport):
    names=[]
    for league in fantasy.get(sport,[]):
        for p in league['players']:
            n=p.get('name','').strip()
            if n and n not in names: names.append(n)
    return names


def player_feed_queries(fantasy, sport, max_players=25):
    """Google News RSS queries; names are from current rosters, not guesses."""
    return [f'"{name}" (injury OR trade OR status OR update OR lineup OR practice) {"NFL" if sport=="nfl" else "NBA"} when:7d'
            for name in roster_names(fantasy,sport)[:max_players]]
