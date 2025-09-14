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
import time


# Questa funzione serve per scrivere ogni quanto il json deve essere scaricato, in modo da non sovraccaricare il server

def json_timer_check(json_filepath):
    """Questa funzione è importante per non dover continuare a chiamare i file json dal server, ma solo ogni ora, cosi
    da non sovraccaricare il server e non avere problemi di connessione"""

    # Apriamo il json e controlliamo se è valido
    from ..utility.json_functions import get_json_data
    json_data = get_json_data(json_filepath)
    if not json_data:
        # In questo caso bisogna scaricare il json
        return False

    # Controlliamo se i parametri esistono "update_time" "update_interval"

    update_time = json_data.get("update_time")
    update_interval = json_data.get("update_interval")

    # Se non esistono i parametri, li scriviamo e usciamo
    if not update_time or not update_interval:
        json_data["update_time"] = int(time.time())
        json_data["update_interval"] = 3600 * 2
        from ..utility.json_functions import save_json
        save_json(json_filepath, json_data)
        # In questo caso il json è valido e va tenuto perchè è stato appena creato il timer
        return json_data

    # Se esistono i parametri, controlliamo se è il momento di aggiornare il json
    if int(time.time()) - update_time > update_interval:
        # in questo caso il tempo è scaduto e bisogna scaricare il json
        # False sarà poi gestito dalla funzione che chiama questa
        return False

    else:
        # In questo caso il json è valido e va tenuto
        return json_data



