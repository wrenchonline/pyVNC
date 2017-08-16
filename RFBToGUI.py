import pygame
import struct
import rfb


class RFBToGUI(rfb.RFBClient):
    """RFBClient protocol that talks to the GUI app"""
    def __init__(self):
        super().__init__()

    def vnc_connection_made(self):
        """choose appropriate color depth, resize screen"""
        # ~ print "Screen format: depth=%d bytes_per_pixel=%r" % (self.depth, self.bpp)
        # ~ print "Desktop name: %r" % self.name

        # ~ print "redmax=%r, greenmax=%r, bluemax=%r" % (self.redmax, self.greenmax, self.bluemax)
        # ~ print "redshift=%r, greenshift=%r, blueshift=%r" % (self.redshift, self.greenshift, self.blueshift)
        self.frame_buffer = self.factory.remoteframebuffer
        self.screen = self.frame_buffer.screen
        self.frame_buffer.set_protocol(self)
        self.frame_buffer.set_rfb_size(self.width, self.height, 32)
        self.set_encodings(self.factory.encodings)
        self.set_pixel_format()  # set up pixel format to 32 bits
        self.framebuffer_update_request()  # request initial screen update

    def vnc_request_password(self):
        if self.factory.password is not None:
            self.send_password(self.factory.password)
        """else:
            # XXX hack, this is blocking twisted!!!!!!!
            screen = pygame.display.set_mode((220, 40))
            screen.fill((255, 100, 0))  # redish bg
            self.send_password(inputbox.ask(screen, "Password", password=1))
        """
            # ~ def beginUpdate(self):
            # ~ """start with a new series of display updates"""

    def begin_update(self):
        """begin series of display updates"""
        # ~ log.msg("screen lock")

    def commit_update(self, rectangles=None):
        """finish series of display updates"""
        # ~ log.msg("screen unlock")
        pygame.display.update(rectangles)
        self.framebuffer_update_request(incremental=1)
        #self.remoteframebuffer.data = np.array(self.remoteframebuffer._data, copy=True)

    def update_rectangle(self, x, y, width, height, data):
        """new bitmap data"""
        # print("%s " * 5 % (x, y, width, height, len(data)))
        # ~ log.msg("screen update")
        self.screen.blit(
            pygame.image.fromstring(data, (width, height), 'RGBX'),  # TODO color format
            (x, y)
        )

    def copy_rectangle(self, srcx, srcy, x, y, width, height):
        """copy src rectangle -> destinantion"""
        # ~ print "copyrect", (srcx, srcy, x, y, width, height)
        self.screen.blit(self.screen,
                         (x, y),
                         (srcx, srcy, width, height)
                         )

    def fill_rectangle(self, x, y, width, height, color):
        """fill rectangle with one color"""
        # ~ remoteframebuffer.CopyRect(srcx, srcy, x, y, width, height)
        color = struct.unpack("BBBB", color)
        rect = (x, y, width, height)

        #self.remoteframebuffer._data[y:y+width, x:x+width] = [color[0], color[1], color[2]]
        self.screen.fill(color, rect)

    def bell(self):
        print("katsching")

    def copy_text(self, text):
        print("Clipboard: %r" % text)


class RFBToGUIeightbits(RFBToGUI):
    def vnc_connection_made(self):
        """choose appropriate color depth, resize screen"""
        self.remoteframebuffer = self.factory.remoteframebuffer
        self.screen = self.remoteframebuffer.screen
        self.remoteframebuffer.set_protocol(self)
        self.remoteframebuffer.set_rfb_size(self.width, self.height, 8)
        self.set_encodings(self.factory.encodings)
        self.set_pixel_format(bpp=8, depth=8, bigendian=0, truecolor=1,
                              redmax=7, greenmax=7, bluemax=3,
                              redshift=5, greenshift=2, blueshift=0
                              )
        self.palette = self.screen.get_palette()
        self.framebuffer_update_request()

    def update_rectangle(self, x, y, width, height, data):
        bmp = pygame.image.fromstring(data, (width, height), 'P')
        bmp.set_palette(self.palette)
        self.screen.blit(bmp, (x, y))

    def fill_rectangle(self, x, y, width, height, color):
        self.screen.fill(ord(color), (x, y, width, height))
