"""Import publicly available Sleeper 2026 NFL rosters for phil64.

Usage: python import_sleeper.py [--username phil64] [--season 2026]
No account passwords; does not change leagues or send email.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from sleeper_integration import football_rosters


def render_report(rosters, username, season):
    lines = [f'# Sleeper {season} NFL roster report — {username}', '',
             f'Leagues with an owned roster: **{len(rosters)}**', '']
    for league in rosters:
        lines += [f"## {league['league']}", f"League ID: `{league['league_id']}`; roster ID: `{league['roster_id']}`", '']
        starters = set(league.get('starters') or [])
        reserve = set(league.get('reserve') or [])
        taxi = set(league.get('taxi') or [])
        lines += ['| Player | Position | NFL team | Roster status | Injury designation |',
                  '|---|---|---|---|---|']
        for p in sorted(league['players'], key=lambda p: (p['id'] not in starters, p['name'])):
            ident=p['id']
            status='Starter' if ident in starters else 'IR' if ident in reserve else 'Taxi' if ident in taxi else 'Bench'
            safe=lambda s: str(s or '').replace('|','/')
            lines.append(f"| {safe(p['name'])} | {safe(p['position'])} | {safe(p['team'])} | {status} | {safe(p['injury_status'])} |")
        lines.append('')
    if not rosters:
        lines.append('No owned 2026 NFL league rosters were returned. Check the username, season, or league membership.')
    return '\n'.join(lines)+'\n'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--username', default='phil64')
    ap.add_argument('--season',type=int,default=2026)
    ap.add_argument('--output', default='roster-import')
    args=ap.parse_args()
    try:
        rosters=football_rosters(args.username,args.season)
    except Exception as exc:
        print(f'Unable to reach/read Sleeper API: {type(exc).__name__}: {exc}',file=sys.stderr)
        return 1
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    payload={'username':args.username,'season':args.season,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'leagues':rosters}
    (output/'sleeper_rosters.json').write_text(json.dumps(payload,indent=2),encoding='utf8')
    (output/'sleeper_rosters.md').write_text(render_report(rosters,args.username,args.season),encoding='utf8')
    print(f"Imported {len(rosters)} owned NFL league(s) for {args.username}.")
    for l in rosters: print(f"  - {l['league']} ({l['league_id']}): {len(l['players'])} players")
    print(f"Files: {output/'sleeper_rosters.md'}, {output/'sleeper_rosters.json'}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
