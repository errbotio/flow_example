from errbot import botflow, FlowRoot, BotFlow

class PollFlows(BotFlow):
    """ Conversation flows related to polls"""

    @botflow
    def poll_setup(self, flow: FlowRoot):
        """ This is a flow that can set up a poll automatically."""
        # setup Flow
        poll_created = flow.connect('poll_new',
                                    predicate=lambda ctx: 'title' in ctx,
                                    auto_trigger=True)

        # add options
        has_more_options = lambda context: 'options' in context and context['options']
        option_added = poll_created.connect('poll_addoption',
                                            predicate=has_more_options)
        option_added.connect(option_added,
                             predicate=has_more_options)  # loop on itself

        poll_started = option_added.connect('poll_start',
                                            predicate=lambda ctx: ctx.get('start', False))

