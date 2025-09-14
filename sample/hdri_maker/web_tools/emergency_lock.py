#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati
import os

from .webservice import get_json_online, get_lost_updates_list
from ..exaproduct import Exa
from ..library_manager.get_library_utils import risorse_lib
# Questa funzione ha il compito di fermare gli operatori nel caso ci sia un blocco di emergenza,
# Questo per evitare che si possa compromettere qualsiasi cosa, se l'utente non tiene aggiornata la versione
# Per esempio, se le librerie necessitano patch, bisognerà scaricare la nuova versione dell'addon, quindi la vecchia deve
# essere fermata, forzatamente altrimenti si danneggerà il lavoro dell'utente.
from ..utility.classes_utils import LibraryUtility
from ..utility.json_functions import get_json_data
from ..utility.text_utils import draw_info
from ..utility.utility import open_user_pref


def is_in_emergency_lock(context, class_name, force_check_online=False):
    """context = context,
    class_name = __class__.__name__
    force_check_online = Boolean (Se True, controllerà online, altrimenti solo in locale si basa su json)"""

    # Qui in sostanza controlla negli update online, se ci sono degli eventuali blocchi di emergenza per versioni vecchie
    # l'esecuzione di questa funzione necessita di connessione internet per scaricare l'update json
    # Online bisogna inserire il nome della classe, tale e quale, example: CLASS_OT_Etc
    operator_is_blocked = False
    if force_check_online:
        # Questo è solo per gli operatori che comunicano con il server, per non rovinare le librerie all'utente, se
        # nel caso in cui l'utente rimane indietro di aggiornamenti
        json_data = get_json_online(urls=Exa.urls_update, save_name="exa_update.json")

    else:
        # Questo, tecnicamente avviene almeno 1 volta alla settimana, ed è utile per tenere aggiornato l'utente per eventuali
        # aggiornamenti, bloccherà gli operatori che non funzionano bene, per vari bug, o vari cambi, cosi da allertare
        # e far aggiornare l'adddon all'utente.
        json_path = os.path.join(risorse_lib(), 'online_utility', "exa_update.json")
        json_data = get_json_data(json_path)

    if not json_data:
        return operator_is_blocked

    updates = json_data.get('updates')
    if not updates:
        return operator_is_blocked


    if force_check_online:
        # Questo evento è nel caso ci siano gravi problemi sul server o sulle linee, quindi probabilmente
        # l'addon si collega a GITHUB e legge il json nel caso exa si down
        communications = json_data.get("communications")
        if communications:
            emergency_message = communications.get("emergency_message")
            if emergency_message:
                LibraryUtility.emergency_message = emergency_message

    workinprogressblock = json_data.get("workinprogressblock")
    if workinprogressblock:
        # Mettiamo un blocco per tutti nel caso in cui ci sia un intervento importante sul server per qualche tempo:
        lock_operators = workinprogressblock.get("lock_operators")
        if lock_operators:
            for class_ops in lock_operators:
                if class_ops == class_name:
                    operator_is_blocked = True
                    break
        if operator_is_blocked:
            description = workinprogressblock.get("description")
            if description:
                text = description
            else:
                text = "For reasons of technical safety, the operator has been blocked at the moment. Sorry for the inconvenience, please try again later"
            draw_info(text, "Info", 'INFO')
            # Questo è per far si di non rallentare l'operatore se fosse bloccato dal json online, si aggiorna subito.
            get_json_online(urls=Exa.urls_update, save_name="exa_update.json")
            return operator_is_blocked

    lost_updates = None
    try:
        lost_updates = get_lost_updates_list(updates)
        for version, data in lost_updates.items():
            for key, value in data.items():
                if key != 'lock_operators':
                    continue
                else:
                    if class_name in value:
                        operator_is_blocked = True
    except:
        print("lost_updates from is_in_emergency_lock() problem:", lost_updates)
        return False

    if operator_is_blocked:
        open_user_pref(context, 'UPDATES')
        text = "You need to update the addon, For security reasons this Operator has been blocked in this version, be sure to update via the 'Update Addon Core' button"
        draw_info(text, "Info", 'INFO')

    # Se vero, l'operatore che esegue questa funzione verrà bloccato

    return operator_is_blocked
