from transitions.extensions import GraphMachine

import similarity_compare as sim

class TocMachine(GraphMachine):

    query = ""

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def is_going_to_busy(self, update):
        text = update.message.text
        return text.lower() == 'babe'

    def on_enter_busy(self, update):
        update.message.reply_text("I'm here")
        with open('gif/smile.mp4', 'rb') as f:
            update.message.reply_video(f)

    def on_exit_busy(self, update):
        print('Leaving STATE busy.')

    def is_going_to_hold(self, update):
        text = update.message.text
        return text.lower() == '/search'

    def on_enter_hold(self, update):
        update.message.reply_text("enter search query, in the form of (* your query)")

    def on_exit_hold(self, update):
        print("Leaving STATE hold")

    def is_going_to_search(self, update):
        text = update.message.text
        if text.lower()[0] == '*':
            self.query = text[2:]
            return True
        else: return False

    def on_enter_search(self, update):
        update.message.reply_text("searching ...")
        sim.vector_space_convert()
        sim.transformation()
        result, article = sim.similarity_compare(self.query)[:5]

        for i in range(0, 5):
            percetage = repr(result[i][1])
            article_name = article[result[i][0]-1]
            update.message.reply_text(article_name[:-4]+" "+percetage[:4])
            article_path = "pdf/" + article_name
            with open(article_path, 'rb') as f:
                update.message.reply_document(f)

        self.go_to_idle(update)

    def on_exit_search(self, update):
        update.message.reply_text("back to chat mode")
        print('Leaving STATE search')

    def is_going_to_regular_check(self, update):
        text = update.message.text
        return text.lower() == 'what are you doing'

    def on_enter_regular_check(self, update):
        update.message.reply_text("i am thinking about you")
        with open('gif/hug.mp4', 'rb') as f:
            update.message.reply_video(f)

    def on_exit_regular_check(self, update):
        print('Leaving STATE regular_check')

    def is_going_to_half_way_there(self, update):
        text = update.message.text
        return text.lower() == 'okay'

    def on_enter_half_way_there(self, update):
        update.message.reply_text("I love you")

    def on_exit_half_way_there(self, update):
        print('Leaving STATE half_way_there')

    def is_going_to_success(self, update):
        text = update.message.text
        return text.lower() == 'i love you too'

    def on_enter_success(self, update):
        update.message.reply_text("love you")
        with open('gif/kiss.mp4', 'rb') as f:
            update.message.reply_video(f)
        self.back_to_idle(update)

    def on_exit_success(self, update):
        print('Leaving STATE success')

    def is_going_to_angry(self, update):
        text = update.message.text
        return text.lower() == "why don't you call me"

    def on_enter_angry(self, update):
        text = "Babe, can I call you back in an hour? My hands are full now."
        update.message.reply_text(text)
        with open('gif/rub_head.mp4', 'rb') as f:
            update.message.reply_video(f)

    def on_exit_angry(self, update):
        print('Leaving STATE angry')

    def is_going_to_very_angry(self, update):
        text = update.message.text
        return text.lower() == 'yeah, you are always very busy'

    def on_enter_very_angry(self, update):
        text = 'Babe, I love you. please...'
        update.message.reply_text(text)
        with open('gif/massage.mp4', 'rb') as f:
            update.message.reply_video(f)
        self.very_angry_to_intv(update)

    def on_enter_intervention(self, update):
        self.go_to_idle(update)

    def on_exit_intervention(self, update):
        print('Leaving STATE intervention')
