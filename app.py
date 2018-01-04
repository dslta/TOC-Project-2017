import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = ''
WEBHOOK_URL = ''

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'idle',
        'hold',
        'search',
        'busy',
        'regular_check',
        'half_way_there',
        'success',
        'angry',
        'very_angry',
        'intervention'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'idle',
            'dest': 'busy',
            'conditions': 'is_going_to_busy'
        },
        {
            'trigger': 'advance',
            'source': 'idle',
            'dest': 'regular_check',
            'conditions': 'is_going_to_regular_check'
        },
        {
        'trigger': 'advance',
        'source': 'idle',
        'dest': 'hold',
        'conditions': 'is_going_to_hold'
        },
        {
            'trigger': 'hold_to_search',
            'source': 'hold',
            'dest': 'search',
            'conditions': 'is_going_to_search'
        },
        {
            'trigger': 'busy_to_rc',
            'source': 'busy',
            'dest': 'regular_check',
            'conditions': 'is_going_to_regular_check'
        },
        {
            'trigger': 'rc_to_hwt',
            'source': 'regular_check',
            'dest': 'half_way_there',
            'conditions': 'is_going_to_half_way_there'
        },
        {
            'trigger': 'angry_or_success',
            'source': 'half_way_there',
            'dest': 'success',
            'conditions': 'is_going_to_success'
        },
        {
            'trigger': 'back_to_idle',
            'source': 'success',
            'dest': 'idle',
        },
        {
            'trigger': 'angry_or_success',
            'source': 'half_way_there',
            'dest': 'angry',
            'conditions': 'is_going_to_angry'
        },
        {
            'trigger': 'very_angry_or_hwt',
            'source': 'angry',
            'dest': 'half_way_there',
            'conditions': 'is_going_to_half_way_there'
        },
        {
            'trigger': 'very_angry_or_hwt',
            'source': 'angry',
            'dest': 'very_angry',
            'conditions': 'is_going_to_very_angry'
        },
        {
            'trigger': 'go_to_idle',
            'source': ['success', 'intervention', 'search'],
            'dest': 'idle'
        },
        {
            'trigger': 'very_angry_to_intv',
            'source': 'very_angry',
            'dest': 'intervention'
        }
    ],
    initial='idle',
    auto_transitions=False,
    show_conditions=True,
)

def girl_friend_handler(machine, update):

    if machine.state == 'idle':
        machine.advance(update)
        print(machine.state)
    elif machine.state == 'hold':
        machine.hold_to_search(update)
        print(machine.state)
    elif machine.state == 'busy':
        machine.busy_to_rc(update)
        print(machine.state)
    elif machine.state == 'regular_check':
        machine.rc_to_hwt(update)
        print(machine.state)
    elif machine.state == 'half_way_there':
        machine.angry_or_success(update)
        print(machine.state)
    elif machine.state == 'angry':
        machine.very_angry_or_hwt(update)
        print(machine.state)
    elif machine.state == 'very_angry':
        machine.very_angry_to_intv(update)
        print(machine.state)
    else:
        pass

def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    girl_friend_handler(machine, update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
