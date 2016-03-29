# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from errbot.utils import drawbar
from errbot import botcmd, BotPlugin, CommandError

class Poll(BotPlugin):

    active_poll = None

    @botcmd
    def poll(self, mess, args):
        """List all polls."""
        return self.poll_list(mess, args)

    @botcmd(syntax='<poll name>')
    def poll_new(self, mess, args):
        """Create a new poll."""
        title = mess.ctx['title'] if 'title' in mess.ctx else args

        if not title:
            raise CommandError('usage: !poll new <poll_title>')

        mess.ctx['current_poll'] = (title, {}, [])

        return 'Poll created. Use !poll option to add options.'

    @botcmd(syntax='<poll option>')
    def poll_addoption(self, mess, args):
        """Add an option to the currently running poll."""

        option = mess.ctx['options'].pop() if 'options' in mess.ctx else args

        if not option:
            raise CommandError('usage: !poll addoption <poll_option>')

        title, options, voted = mess.ctx['current_poll']

        if option in options:
            raise CommandError('Option already exists. Use !poll show to see all options.')

        options[option] = 0

        return 'Option "%s" added.' % option

    @botcmd
    def poll_remove(self, mess, args):
        """Remove a poll."""
        title = args

        if not title:
            raise CommandError('usage: !poll remove <poll_title>')

        try:
            del self[title]
            return 'Poll removed.'
        except KeyError as _:
            raise CommandError('That poll does not exist. Use !poll list to see all polls.')

    @botcmd
    def poll_list(self, mess, args):
        """List all polls."""
        if len(self) > 0:
            return 'All Polls:\n' + u'\n'.join([title + (u' *' if title == Poll.active_poll else u'') for title in self])
        raise CommandError('No polls found. Use !poll new to add one.')

    @botcmd
    def poll_start(self, mess, args):
        """Start a saved poll."""
        if Poll.active_poll is not None:
            raise CommandError('"%s" is currently running, use !poll stop to finish it.' % Poll.active_poll)

        title = args

        if not title:
            raise CommandError('usage: !poll start <poll_title>')

        if not title in self:
            raise CommandError('Poll not found. Use !poll list to see all polls.')

        self.reset_poll(title)
        Poll.active_poll = title

        return self.format_poll(title)

    @botcmd
    def poll_stop(self, mess, args):
        """Stop the currently running poll."""
        result = 'Poll finished, final results:\n'
        result += self.format_poll(Poll.active_poll)

        self.reset_poll(Poll.active_poll)
        Poll.active_poll = None

        return result



    @botcmd
    def poll_show(self, mess, args):
        """Show the currently running poll."""
        if not Poll.active_poll:
            raise CommandError('No active poll. Use !poll start to start a poll.')

        return self.format_poll(Poll.active_poll)

    @botcmd
    def poll_vote(self, mess, args):
        """Vote for the currently running poll."""
        if not Poll.active_poll:
            raise CommandError('No active poll. Use !poll start to start a poll.')

        index = args

        if not index:
            raise CommandError('usage: !poll vote <option_number>')

        if not index.isdigit():
            raise CommandError('Please vote using the numerical index of the option.')

        poll = self[Poll.active_poll]
        options, usernames = poll

        index = int(index)
        if index > len(options) or index < 1:
            raise CommandError('Please choose a number between 1 and %d (inclusive).' % len(options))

        option = list(options.keys())[index - 1]  # FIXME: this looks random

        if not option in options:
            raise CommandError('Option not found. Use !poll show to see all options of the current poll.')

        username = mess.frm.person

        if username in usernames:
            raise CommandError('You have already voted.')

        usernames.append(username)

        options[option] += 1
        self[Poll.active_poll] = poll

        return self.format_poll(Poll.active_poll)

    def format_poll(self, title):
        poll = self[title]
        options, usernames = poll

        total_votes = sum(options.values())

        result = Poll.active_poll + '\n'
        index = 1
        for option in options:
            result += '%s %d. %s (%d votes)\n' % (drawbar(poll[0][option], total_votes), index, option, poll[0][option])
            index += 1

        return result.strip()

    def reset_poll(self, title):
        poll = self[title]

        options, usernames = poll

        for option in options:
            options[option] = 0

        del usernames[:]

        self[title] = poll



