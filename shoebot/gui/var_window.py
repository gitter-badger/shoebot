#!/usr/bin/env python2
import os

from shoebot.grammar.var_listener import VarListener
from pgi.repository import Gtk
from pkg_resources import resource_filename, Requirement
ICON_FILE = resource_filename(Requirement.parse("shoebot"), "share/pixmaps/shoebot-ide.png")


NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4


def pretty_name(name):
    return (name or '').replace('_', ' ').capitalize()


class VarWindow(object):
    def __init__(self, parent, bot, title = None):
        self.parent = parent
        self.bot = bot

<<<<<<< HEAD
        self.var_listener = VarListener(self)

        self.window = Gtk.Window()
        self.window.set_destroy_with_parent(True)
        self.window.connect("destroy", self.do_quit)

        if os.path.isfile(ICON_FILE):
            self.window.set_icon_from_file( ICON_FILE )

        self.container = Gtk.VBox(homogeneous=True, spacing=20)

        # set up sliders
        self.widgets = {}
        self.vars = {}
        self.add_variables()

        self.window.add(self.container)
        self.window.set_size_request(400, 35*len(self.widgets.keys()))
        self.window.show_all()

        if title:
            self.window.set_title(title)
        ## Gtk.main()

    def add_variables(self):
        """
        Add all widgets to specified vbox
        :param container:
        :return:
        """
        for v in sorted(self.bot._vars.values()):
            self.add_variable(v)

    def add_variable(self, v):
        if v.type is NUMBER:
            self.widgets[v.name] = self.add_number(v)
        elif v.type is TEXT:
            self.widgets[v.name] = self.add_text(v)
        elif v.type is BOOLEAN:
            self.widgets[v.name] = self.add_boolean(v)
        elif v.type is BUTTON:
            self.widgets[v.name] = self.add_button(v)
        else:
            raise ValueError('Unknown variable type.')
        self.vars[v.name] = v

    def add_number(self, v):
        # create a slider for each var
        sliderbox = Gtk.HBox(homogeneous=False, spacing=0)
        label = Gtk.Label(pretty_name(v.name))
        sliderbox.pack_start(label, False, True, 20)

        if v.max - v.min > 2:
            adj = Gtk.Adjustment(v.value, v.min, v.max, .1, 2, 1)
        else:
            adj = Gtk.Adjustment(v.value, v.min, v.max, .1)
        adj.connect("value_changed", self.widget_changed, v)
        hscale = Gtk.HScale(adjustment=adj)
        #hscale.set_value_pos(Gtk.POS_RIGHT)
        hscale.set_value(v.value)
        sliderbox.pack_start(hscale, True, True, 0)
        self.container.pack_start(sliderbox, True, True, 0)

        return hscale

    def add_text(self, v):
        textcontainer = Gtk.HBox(homogeneous=False, spacing=0)
        label = Gtk.Label(pretty_name(v.name))
        textcontainer.pack_start(label, False, True, 20)

        entry = Gtk.Entry(max=0)
        entry.set_text(v.value)
        entry.connect("changed", self.widget_changed, v)
        textcontainer.pack_start(entry, True, True, 0)
        self.container.pack_start(textcontainer, True, True, 0)

        return entry

    def add_boolean(self v):
        buttoncontainer = Gtk.HBox(homogeneous=False, spacing=0)
        button = Gtk.CheckButton(label=pretty_name(v.name))
        button.set_active(v.value)
        # we send the state of the button to the callback method
        button.connect("toggled", self.widget_changed, v)

        buttoncontainer.pack_start(button, True, True, 0)
        self.container.pack_start(buttoncontainer, True, True, 0)

        return button

    def add_button(self, v):
        buttoncontainer = Gtk.HBox(homogeneous=False, spacing=0)
        # in buttons, the varname is the function, so we use __name__

        func_name = v.name

        def call_func(*args):
            func = self.bot._namespace[func_name]
            func()

        button = Gtk.Button(label=pretty_name(v.name))
        button.connect("clicked", call_func, None)
        buttoncontainer.pack_start(button, True, True, 0)
        self.container.pack_start(buttoncontainer, True, True, 0)

        return button

    def do_destroy(self, widget):
        #self.bot._var_listeners.remove(self.var_listener)
        self.var_listener.remove()

    def do_quit(self, widget):
        pass

    def update_var(self, name, value):
        """
        :return: success, err_msg_if_failed
        """
        widget = self.widgets.get(name)
        if widget is None:
            return False, 'No widget found matching, {}'.format(name)

        try:
            if isinstance(widget, gtk.CheckButton):
                widget.set_active(value)
                return True, widget.get_active()
            elif isinstance(widget, gtk.Entry):
                widget.set_text(value)
                return True, widget.get_text()
            else:
                widget.set_value(value)
                return True, widget.get_value()
        except Exception as e:
            return False, str(e)

    def widget_changed(self, widget, v):
        ''' Called when a slider is adjusted. '''
        # set the appropriate bot var
        if v.type is NUMBER:
            self.bot._namespace[v.name] = widget.get_value()
            self.bot._vars[v.name].value = widget.get_value()  ## Not sure if this is how to do this - stu
        elif v.type is BOOLEAN:
            self.bot._namespace[v.name] = widget.get_active()
            self.bot._vars[v.name].value = widget.get_active()  ## Not sure if this is how to do this - stu
        elif v.type is TEXT:
            self.bot._namespace[v.name] = widget.get_text()
            self.bot._vars[v.name].value = widget.get_text()  ## Not sure if this is how to do this - stu

    def var_added(self, v):
        """
        var was added in the bot while it ran, possibly
        by livecoding

        :param v:
        :return:
        """
        self.add_variable(v)

        self.window.set_size_request(400, 35*len(self.widgets.keys()))
        self.window.show_all()

    def var_deleted(self, v):
        """
        var was added in the bot

        :param v:
        :return:
        """
        widget = self.widgets[v.name]

        # widgets are all in a single container ..
        parent = widget.get_parent()
        self.container.remove(parent)
        del self.widgets[v.name]

        self.window.set_size_request(400, 35*len(self.widgets.keys()))
        self.window.show_all()

    def var_updated(self, v):
        pass


