# Copyright 2012 Tomasz Kontusz
#
# This file is part of Spanel.
#
# Spanel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spanel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Spanel. If not, see <http://www.gnu.org/licenses/>.

import gtk

class GdkLock(object):
    def __init__(self):
        self.owned = False

    def __enter__(self):
        if not self.owned:
            self.owned = True
            gtk.gdk.threads_enter()

    def __exit__(self, type, value, traceback):
        if self.owned:
            self.owned = False
            gtk.gdk.threads_leave()

    def fake(self):
        """For when you KNOW it's already owned"""
        class FakeGdkLock(object):
            def __enter__(s):
                s.old_owned = self.owned
                self.owned = True

            def __exit__(s, type, value, traceback):
                self.owned = s.old_owned
        return FakeGdkLock()


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class Enum(object):
    class EnumElem(int):
        def __new__(cls, name, *args, **kwargs):
            r = super(Enum.EnumElem, cls).__new__(cls, *args, **kwargs)
            r.name = name
            return r

        def __unicode__(self):
            return self.name

        def __str__(self):
            return self.name

    def __getitem__(self, key):
        return self._items[key]

    def __init__(self, elems):
        self._items={}
        for i, e in enumerate(elems):
            elem = Enum.EnumElem(e, i)
            self._items[i] = elem
            self._items[e] = elem
            setattr(self, e, elem)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
