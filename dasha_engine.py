import json
from datetime import datetime

def get_current_dasha(date=None):
    if date is None:
        date = datetime.now().date()

    with open('dasha_sequence.json') as f:
        data = json.load(f)

    for maha in data:
        maha_start = datetime.fromisoformat(maha['start']).date()
        maha_end = datetime.fromisoformat(maha['end']).date()
        if maha_start <= date <= maha_end:
            current_maha = maha['mahadasha']
            for antara in maha['antardashas']:
                antara_start = datetime.fromisoformat(antara['start']).date()
                antara_end = datetime.fromisoformat(antara['end']).date()
                if antara_start <= date <= antara_end:
                    current_antara = antara['antardasha']
                    for prata in antara.get('pratyantardashas', []):
                        prata_start = datetime.fromisoformat(prata['start']).date()
                        prata_end = datetime.fromisoformat(prata['end']).date()
                        if prata_start <= date <= prata_end:
                            return [current_maha, current_antara, prata['pratyantar']]
                    return [current_maha, current_antara, "—"]
            return [current_maha, "—", "—"]
    return ["—", "—", "—"]