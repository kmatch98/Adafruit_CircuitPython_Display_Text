# The MIT License (MIT)
#
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_display_text.text_area`
====================================================

Displays text using CircuitPython's displayio.

* Author(s): Scott Shawcroft

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"

class TextArea(displayio.Group):
    """An area displaying a string of textself.

       :param Font font: A font class that has ``get_bounding_box`` and ``get_glyph``
       :param str text: Text to display
       :param int max_glyphs: The largest quantity of glyphs we will display
       :param int color: Color of all text in RGB hex"""
    def __init__(self, font, *, text=None, max_glyphs=None, color=0xffffff):
        if not max_glyphs and not text:
            raise RuntimeError("Please provide a max size, or initial text")
        if not max_glyphs:
            max_glyphs = len(text)
        super().__init__(max_size=max_glyphs)
        self.width = max_glyphs
        self.font = font
        self._text = None

        self.palette = displayio.Palette(2)
        self.palette.make_transparent(0)
        self.palette[1] = color

        bounds = self.font.get_bounding_box()
        self.height = bounds[1]
        self._line_spacing = 1.25
        self._boundingbox = None

        if text:
            self._update_text(text)


    def _update_text(self, new_text): # pylint: disable=too-many-locals
        x = 0
        y = 0
        i = 0
        old_c = 0
        y_offset = int((self.font.get_glyph(ord('M')).height -
                        new_text.count('\n') * self.height * self.line_spacing) / 2)
        #print("y offset from baseline", y_offset)
        left = right = top = bottom = 0
        for character in new_text:
            if character == '\n':
                y += int(self.height * self._line_spacing)
                x = 0
                continue
            glyph = self.font.get_glyph(ord(character))
            if not glyph:
                continue
            right = max(right, x+glyph.width)
            if y == 0:   # first line, find the Ascender height
                top = min(top, -glyph.height+y_offset)
            bottom = max(bottom, y-glyph.dy+y_offset)
            position_y = y - glyph.height - glyph.dy + y_offset
            position_x = x + glyph.dx
            if not self._text or old_c >= len(self._text) or character != self._text[old_c]:
                face = displayio.TileGrid(glyph.bitmap, pixel_shader=self.palette,
                                          default_tile=glyph.tile_index,
                                          tile_width=glyph.width, tile_height=glyph.height,
                                          position=(position_x, position_y))
                if i < len(self):
                    self[i] = face
                else:
                    self.append(face)
            elif self._text and character == self._text[old_c]:
                self[i].position = (position_x, position_y)

            x += glyph.shift_x

            # TODO skip this for control sequences or non-printables.
            i += 1
            old_c += 1
            # skip all non-prinables in the old string
            while (self._text and old_c < len(self._text) and
                   (self._text[old_c] == '\n' or not self.font.get_glyph(ord(self._text[old_c])))):
                old_c += 1
        # Remove the rest
        while len(self) > i:
            self.pop()
        self._text = new_text
        self._boundingbox = (left, top, left+right, bottom-top)

    @property
    def bounding_box(self):
        """An (x, y, w, h) tuple that completely covers all glyphs. The
        first two numbers are offset from the x, y origin of this group"""
        return tuple(self._boundingbox)

    @property
    def line_spacing(self):
        """The amount of space between lines of text, in multiples of the font's
        bounding-box height. (E.g. 1.0 is the bounding-box height)"""
        return self._line_spacing

    @line_spacing.setter
    def line_spacing(self, spacing):
        self._line_spacing = spacing

    @property
    def color(self):
        """Color of the text as an RGB hex number."""
        return self.palette[1]

    @color.setter
    def color(self, new_color):
        self.palette[1] = new_color

    @property
    def text(self):
        """Text to display."""
        return self._text

    @text.setter
    def text(self, new_text):
        self._update_text(new_text)
