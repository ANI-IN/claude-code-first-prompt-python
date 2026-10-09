"""A tiny stand-in for the browser, so main.py can be tested with plain pytest.

It parses the real index.html into lightweight elements that support the
handful of DOM features main.py uses: getElementById, querySelector(All) with
simple selectors, classList, attributes, dataset, textContent, and event
listeners. `load_page()` installs fake `js` and `pyscript.ffi` modules, runs
main.py exactly as PyScript would, and returns the fake browser to inspect.
"""

import datetime
import re
import runpy
import sys
import types
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Event:
    def __init__(self, type_, target=None, **fields):
        self.type = type_
        self.target = target
        self.default_prevented = False
        for name, value in fields.items():
            setattr(self, name, value)

    def preventDefault(self):
        self.default_prevented = True


class EventTarget:
    def __init__(self):
        self.listeners = {}
        self.listener_options = {}

    def addEventListener(self, type_, handler, options=None):
        self.listeners.setdefault(type_, []).append(handler)
        self.listener_options.setdefault(type_, []).append(options)

    def dispatch(self, type_, **fields):
        event = Event(type_, target=self, **fields)
        for handler in list(self.listeners.get(type_, [])):
            handler(event)
        return event


class ClassList:
    def __init__(self, element):
        self._element = element

    def _names(self):
        return self._element.attributes.get("class", "").split()

    def _store(self, names):
        self._element.attributes["class"] = " ".join(names)

    def contains(self, name):
        return name in self._names()

    def add(self, name):
        names = self._names()
        if name not in names:
            self._store(names + [name])

    def remove(self, name):
        self._store([n for n in self._names() if n != name])

    def toggle(self, name, force=None):
        present = self.contains(name) if force is None else not force
        if present:
            self.remove(name)
            return False
        self.add(name)
        return True


class Dataset:
    """Mirrors element.dataset: data-foo-bar is exposed as .fooBar."""

    def __init__(self, element):
        object.__setattr__(self, "_element", element)

    def __getattr__(self, name):
        attr = "data-" + re.sub(r"[A-Z]", lambda m: "-" + m.group(0).lower(), name)
        try:
            return self._element.attributes[attr]
        except KeyError:
            raise AttributeError(name) from None


class Element(EventTarget):
    def __init__(self, tag, attributes=None, parent=None):
        super().__init__()
        self.tagName = tag.upper()
        self.attributes = dict(attributes or {})
        self.parent = parent
        self.children = []
        self._text = []
        self.classList = ClassList(self)
        self.dataset = Dataset(self)

    # --- attributes ---
    def getAttribute(self, name):
        return self.attributes.get(name)

    def setAttribute(self, name, value):
        self.attributes[name] = str(value)

    def hasAttribute(self, name):
        return name in self.attributes

    @property
    def id(self):
        return self.attributes.get("id", "")

    @property
    def className(self):
        return self.attributes.get("class", "")

    # --- text ---
    @property
    def textContent(self):
        return "".join(self._text) + "".join(child.textContent for child in self.children)

    @textContent.setter
    def textContent(self, value):
        self.children = []
        self._text = [str(value)]

    # --- events ---
    def click(self):
        return self.dispatch("click")

    # --- traversal ---
    def iter_descendants(self):
        for child in self.children:
            yield child
            yield from child.iter_descendants()

    def matches(self, selector):
        match = re.fullmatch(r"([a-zA-Z][\w-]*)?((?:[.#][\w-]+)*)", selector.strip())
        if not match:
            raise ValueError(f"Unsupported selector: {selector!r}")
        tag, rest = match.groups()
        if tag and tag.upper() != self.tagName:
            return False
        for kind, name in re.findall(r"([.#])([\w-]+)", rest):
            if kind == "#" and self.id != name:
                return False
            if kind == "." and not self.classList.contains(name):
                return False
        return True

    def querySelectorAll(self, selector):
        return NodeList(el for el in self.iter_descendants() if el.matches(selector))

    def querySelector(self, selector):
        found = self.querySelectorAll(selector)
        return found[0] if found.length else None

    def __repr__(self):
        return f"<{self.tagName.lower()} id={self.id!r} class={self.className!r}>"


class NodeList(list):
    @property
    def length(self):
        return len(self)


class Document(Element):
    def __init__(self):
        super().__init__("#document")
        self.documentElement = None

    def getElementById(self, element_id):
        for el in self.iter_descendants():
            if el.id == element_id:
                return el
        return None


class _TreeBuilder(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.document = document
        self.stack = [document]

    def handle_starttag(self, tag, attrs):
        el = Element(tag, {k: (v if v is not None else "") for k, v in attrs}, parent=self.stack[-1])
        self.stack[-1].children.append(el)
        if tag == "html":
            self.document.documentElement = el
        if tag not in VOID_TAGS:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tagName == tag.upper():
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1]._text.append(data)


def parse_html(html):
    document = Document()
    _TreeBuilder(document).feed(html)
    if document.documentElement is None:
        # A bare snippet still gets a root element, as it would in a browser.
        root = Element("html", parent=document)
        root.children, document.children = document.children, [root]
        for child in root.children:
            child.parent = root
        document.documentElement = root
    return document


class IntersectionObserver:
    """Records what it observes; tests call `trigger()` to simulate scrolling."""

    instances = []

    def __init__(self, callback, options=None):
        self.callback = callback
        self.options = options
        self.observed = []
        IntersectionObserver.instances.append(self)

    @classmethod
    def new(cls, callback, options=None):
        return cls(callback, options)

    def observe(self, el):
        self.observed.append(el)

    def unobserve(self, el):
        self.observed.remove(el)

    def trigger(self, el, is_intersecting=True):
        entry = types.SimpleNamespace(target=el, isIntersecting=is_intersecting)
        self.callback([entry], self)


class Date:
    """Just enough of the browser's Date: the current local date."""

    def __init__(self):
        self._now = datetime.datetime.now()

    @classmethod
    def new(cls):
        return cls()

    def getFullYear(self):
        return self._now.year


class Storage:
    def __init__(self, initial=None, blocked=False):
        self.items = dict(initial or {})
        self.blocked = blocked

    def _check(self):
        if self.blocked:
            raise RuntimeError("SecurityError: storage is disabled")

    def getItem(self, key):
        self._check()
        return self.items.get(key)

    def setItem(self, key, value):
        self._check()
        self.items[key] = str(value)

    def removeItem(self, key):
        self.items.pop(key, None)


class MediaQueryList(EventTarget):
    def __init__(self, media, matches):
        super().__init__()
        self.media = media
        self.matches = matches

    def addListener(self, handler):
        """The older Safari API: same as addEventListener("change", handler)."""
        self.addEventListener("change", handler)

    def change(self, matches):
        self.matches = matches
        self.dispatch("change", matches=matches, media=self.media)


class LegacyMediaQueryList(MediaQueryList):
    """A media query list from older browsers, without addEventListener."""

    def __getattribute__(self, name):
        if name == "addEventListener":
            raise AttributeError(name)
        return super().__getattribute__(name)

    def addListener(self, handler):
        MediaQueryList.addEventListener(self, "change", handler)


class Window(EventTarget):
    def __init__(self, inner_width=1280, scroll_y=0, intersection_observer=True,
                 local_storage=None, storage_blocked=False, prefers_dark=False,
                 match_media=True, legacy_media_listeners=False):
        super().__init__()
        self.innerWidth = inner_width
        self.scrollY = scroll_y
        self.localStorage = Storage(local_storage, blocked=storage_blocked)
        self.prefers_dark = prefers_dark
        self.legacy_media_listeners = legacy_media_listeners
        self.media_queries = {}
        if intersection_observer:
            self.IntersectionObserver = IntersectionObserver
        if match_media:
            self.matchMedia = self._match_media

    def _match_media(self, query):
        if query not in self.media_queries:
            matches = self.prefers_dark if "prefers-color-scheme: dark" in query else False
            kind = LegacyMediaQueryList if self.legacy_media_listeners else MediaQueryList
            self.media_queries[query] = kind(query, matches)
        return self.media_queries[query]


class Browser:
    """What `load_page()` hands back to a test."""

    def __init__(self, document, window, namespace):
        self.document = document
        self.window = window
        self.namespace = namespace

    def by_id(self, element_id):
        return self.document.getElementById(element_id)

    def all(self, selector):
        return self.document.querySelectorAll(selector)

    def press(self, target, key):
        return target.dispatch("keydown", key=key)


def load_page(html=None, script="main.py", **window_options):
    """Parse the page, run the script against it, and return the fake browser."""
    if html is None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
    document = parse_html(html)
    window = Window(**window_options)
    IntersectionObserver.instances = []

    js_module = types.ModuleType("js")
    js_module.document = document
    js_module.window = window
    js_module.Date = Date

    ffi_module = types.ModuleType("pyscript.ffi")
    ffi_module.create_proxy = lambda fn: fn
    ffi_module.to_js = lambda value: value

    pyscript_module = types.ModuleType("pyscript")
    pyscript_module.ffi = ffi_module
    pyscript_module.document = document
    pyscript_module.window = window

    saved = {name: sys.modules.get(name) for name in ("js", "pyscript", "pyscript.ffi")}
    sys.modules.update({"js": js_module, "pyscript": pyscript_module, "pyscript.ffi": ffi_module})
    try:
        namespace = runpy.run_path(str(ROOT / script), run_name="__main__")
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
    return Browser(document, window, namespace)
