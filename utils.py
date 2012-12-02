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
    class EnumElem(object):
        def __init__(self, name, value):
            self.name = name
            self.val = value

        def __unicode__(self):
            return self.name

    def __init__(self, elems):
        for i, e in enumerate(elems):
            setattr(self, e, Enum.EnumElem(e, i))
