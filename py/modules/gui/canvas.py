import matplotlib;
import matplotlib.pyplot as plt;
from matplotlib.figure import Figure;
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas;
from matplotlib.patches import Rectangle, Ellipse;
matplotlib.use("Qt5Agg");

from PyQt5.QtWidgets import QSizePolicy;

class CanvasDICOMImg(FigureCanvas):

    def __init__(self, parent, dim = None, dpi=100):
        if(dim == None):
            fig = Figure(dpi=dpi)
        else:
            width = dim[0];
            height = dim[1];
            fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi);

        FigureCanvas.__init__(self, fig);

        self.roi= [[None,None],[None,None]];
        self.dpi = dpi;
        self.setParent(parent);
        self.pressed = False;
        self.roi_method = "Dot";
        self.printable = False;

        # > Roi shapes
        dot = Ellipse((0,0), 1, 1);
        dot.fill = False;
        dot.set_edgecolor('red');

        rectangle = Rectangle((0,0), 1, 1);
        rectangle.fill = False;
        rectangle.set_edgecolor('red');

        ellipse = Ellipse((0,0), 1, 1);
        ellipse.fill = False;
        ellipse.set_edgecolor('red');

        self.roi_shapes = {
            'Dot' : dot,
            'Rectangle' : rectangle,
            'Ellipse' : ellipse,
            'Polygon' : None,
            'Freehand': None
        }

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding);
        FigureCanvas.updateGeometry(self);

        self.ax = self.figure.add_subplot(111);
        self.ax.set_axis_off();

        self._init_events();
        return ;


    def set_roi_method(self, method):
        self.roi_method = method;
        for key, shape in self.roi_shapes.items():
            if(shape != None):
                shape.set_visible(False);
        self.roi_shapes[method].set_visible(True);
        return ;

    def get_roi(self):
        x0, y0 = self.roi[0];
        x1, y1 = self.roi[1];
        roi_vertices = [
            (x0,y0), (x0,y1), (x1,y0), (x1,y1)
        ];
        return roi_vertices;

    def plot(self,img):
        self.ax.imshow(img, cmap=plt.get_cmap("gray"));
        self.draw();
        self.printable = True;
        return ;

    # EVENT METHODS
    ########################################################

    def _init_events(self):
        self.ax.figure.canvas.mpl_connect(  'button_press_event',  \
                                            self.on_press);

        self.ax.figure.canvas.mpl_connect(  'motion_notify_event', \
                                            self.on_motion);

        self.ax.figure.canvas.mpl_connect(  'button_release_event', \
                                            self.on_release);

    def on_press(self, event):
        self.roi = [(event.xdata, event.ydata), (None, None)];
        self.pressed = True;
        if( self.roi_method == "Dot" and
            event.xdata != None and
            event.ydata != None and
            self.printable ):

            x0,y0 = self.roi[0];
            self.roi_shapes["Dot"].center = x0, y0;
            self.ax.add_patch(self.roi_shapes["Dot"]);
            self.draw();
        return ;

    def on_motion(self, event):
        if self.pressed is False:
            return;

        self.roi[1] = (event.xdata, event.ydata);
        x0,y0 = self.roi[0];
        x1,y1 = self.roi[1];
        if( x0 != None and y0 != None and
            x1 != None and y1 != None and
            self.printable):

            roi_method = self.roi_method;
            shape = self.roi_shapes[self.roi_method];

            #if(roi_method == "Dot"):

            if(roi_method == "Rectangle"):
                shape.set_width(x1 - x0);
                shape.set_height(y1 - y0);
                shape.set_xy((x0, y0));

            elif(roi_method == "Ellipse"):
                shape.center = x0, y0;
                shape.width = x1 - x0;
                shape.height = y1 - y0;

            self.ax.add_patch(shape);
            self.draw();
        return ;

    def on_release(self, event):
        self.pressed = False;
        return ;

    ########################################################

class CanvasFFMap(FigureCanvas):

    def __init__(self, parent, dim = None, dpi=100):
        if(dim == None):
            fig = Figure(dpi=dpi)
        else:
            width = dim[0];
            height = dim[1];
            fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi);

        FigureCanvas.__init__(self, fig);

        self.dpi = dpi;
        self.setParent(parent);

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Ignored,
                QSizePolicy.Ignored);
        FigureCanvas.updateGeometry(self);

        self.ax = self.figure.add_subplot(111);
        self.ax.set_axis_off();
        self._cb = False;
        return ;

    def plot(self,img):
        im = self.ax.imshow(img, cmap=plt.get_cmap("plasma"), vmin=0.0, vmax=1.0);
        if(not self._cb):
            self.figure.colorbar(im);
            self._cb = True;
        self.draw();
        return ;

class CanvasSignalPlot(FigureCanvas):

    def __init__(self, parent, dim = None, dpi=100):
        if(dim == None):
            fig = Figure(dpi=dpi)
        else:
            width = dim[0];
            height = dim[1];
            fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi);

        FigureCanvas.__init__(self, fig);

        self.dpi = dpi;
        self.setParent(parent);

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Ignored,
                QSizePolicy.Ignored);
        FigureCanvas.updateGeometry(self);

        self.ax = self.figure.add_subplot(111);
        return ;

    def plot(self,x,y):
        self.ax.clear();
        self.ax.xaxis.set_ticks(x);
        self.ax.plot(x,y, '*r');
        self.draw();
        return ;
