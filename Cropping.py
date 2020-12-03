import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import tkinter.filedialog as tkfd
from PIL import Image
from math import ceil
from math import floor
from scipy import ndimage
from matplotlib.widgets import RectangleSelector
import os
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
import numpy as np

class ImageLoader(tk.Tk):
    def __init__(self):
        super().__init__()


        self.protocol('WM_DELETE_WINDOW', self.onclose)

        s = ttk.Style()
        s.configure('.', font=('Cambria'), fontsize=16)
        s.configure('TButton', background='black', foreground='black')
        self.grid_rowconfigure(0,w=1)
        self.grid_columnconfigure(0,w=1)
        #create frames and their position in the window
        self.frame1 = ttk.Frame(self)
        self.frame1.grid(column=0,row=0,sticky='nsew')

        self.frame2 = ttk.Frame(self)
        self.frame2.grid(column=1,row=0,sticky='nsew')

        #define size of the figure and horizontal axis.
        self.fig, self.ax = plt.subplots(figsize=(5,5))

        #draw the empty figure and determine what layer to put it on
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame1)
        self.canvas.draw()

        #define how the window fills,side determines what side it aligns to,
        #fill='x' makes the function stretch in x, but not in y,
        #fill='both' makes it expand in both x and y, etc.

        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame1)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


        self.OpenImage = ttk.Button(self.frame2, text='Open Image', command=self.open_image)
        self.OpenImage.grid(row=1, columnspan=2, sticky='ew')

        self.CloseButton = ttk.Button(self.frame2, text='Close', command=self.onclose)
        self.CloseButton.grid(row=9, columnspan=2)

        self.PickPoints = ttk.Button(self.frame2, text='Select Baseline', command=self.pickpoints, state=tk.ACTIVE)
        self.PickPoints.grid()
        self.PickPoints.grid_forget()

        self.InteractiveRectangle = ttk.Button(self.frame2, text='Interactive Rectangle', command=self.interactiverectangle)
        self.InteractiveRectangle.grid()
        self.InteractiveRectangle.grid_forget()

        self.BufferLabel = ttk.Label(self.frame2, text='Offset:')
        self.BufferLabel.grid()
        self.BufferLabel.grid_forget()
        self.BufferEntry = ttk.Entry(self.frame2)
        self.BufferEntry.grid()
        self.BufferEntry.grid_forget()


        self.Crop = ttk.Button(self.frame2, text='Crop', command=self.cropper, state=tk.ACTIVE)
        self.Crop.grid()
        self.Crop.grid_forget()

        self.PreciseCrop = ttk.Button(self.frame2, text='Precise Cropping', command=self.precise_crop, state=tk.ACTIVE)
        self.PreciseCrop.grid()
        self.PreciseCrop.grid_forget()

        self.SaveImage = ttk.Button(self.frame2, text='Save Image', command=self.save_image, state=tk.ACTIVE)
        self.SaveImage.grid()
        self.SaveImage.grid_forget()

        self.HelpText = ttk.Label(self.frame2, text='Load an image to begin.', justify='center')
        self.HelpText.grid(row=0, columnspan=2)

        self.Back = ttk.Button(self.frame2, text='Back')

#-----------------------------functions-----------------------------------------
    def open_image(self):

        self.f = tkfd.askopenfilename(
            parent=self, initialdir='.',
            title='Choose file',
            filetypes=[
                   ('jpeg images', '.jpg')]
            )


        try:
            self.image_path = os.path.dirname(self.f)


            self.img_arr = plt.imread(self.f)
            self.img_arr = np.array(self.img_arr)
            try:
                self.loaded_image.remove()
                try:
                    self.InteractiveRectangle.grid_forget()
                    self.PreciseCrop.grid_forget()
                    self.PickPoints.grid(row=3)
                    try:
                        self.BufferLabel.grid_forget()
                        self.BufferEntry.grid_forget()
                        self.Crop.grid_forget()
                        self.rectline1.remove()
                        self.rectline2.remove()
                        self.rectline3.remove()
                        self.rectline4.remove()
                        self.PickPoints.grid(row=3)
                        toggle_selector.RS.setactive(false)
                    except AttributeError as e:
                        pass
                except AttributeError as e:
                    pass
            except AttributeError as e:
                pass
            self.loaded_image = self.ax.imshow(self.img_arr)

            self.PickPoints.grid(row=3, columnspan=2)
            self.HelpText.config(text='Select a Baseline \nthat follows the angle of\nthe bottom of the desired region\n\nRight click to place points,\nmiddle click to end.')
            self.canvas.draw()
        except AttributeError as e:
            tk.messagebox.showerror(title='Loading Error', message='No image selected, please select an image')

    def pickpoints(self):
        if self.PickPoints['text'] == 'Select Baseline':
            self.pointpick = PointPicker(self, 2)

            self.after(100, self.drawline)

            self.PickPoints['text'] = 'Done'
        elif self.PickPoints['text'] == 'Done':
            self.PickPoints['text'] = 'Select Baseline'
            self.pointpick.end()

            #self.PickPoints.config(text='Select Baseline')
    def drawline(self):
        try:
            self.point = np.array(self.pointpick.points)
            if self.pointpick.ended:
                del self.pointpick
            self.after(100, self.drawline)
        except AttributeError as e:
            self.xs = [floor(i.get_xdata()[0]) for i in self.point]
            self.ys = [floor(i.get_ydata()[0]) for i in self.point]

            self.first_x = self.xs[0]
            self.first_y = self.ys[0]

            self.second_x = self.xs[1]
            self.second_y = self.ys[1]

            for line in self.point:
                line.remove()

            xspan = self.second_x - self.first_x
            yspan = self.second_y - self.first_y

            self.theta = np.arctan(yspan/xspan)
            self.alpha = self.theta * 180/(np.pi)

            self.img_arr = ndimage.rotate(self.img_arr, self.alpha, reshape=True)
            self.loaded_image.remove()
            self.loaded_image = self.ax.imshow(self.img_arr)
            self.baseline = self.ax.plot(self.xs, self.ys, '-o', color='green')[0]

            self.canvas.draw()

            self.PreciseCrop.grid(row=4,columnspan=2)
            self.InteractiveRectangle.grid(row=3,columnspan=2)
            self.PickPoints.state([tk.ACTIVE])
            self.PickPoints.grid_forget()

            self.HelpText.config(text='Choose your cropping method:\n\nInteractive Rectangle:\nA draggable rectangle for less\nprecise cropping.\n\nPrecise Cropping:\nClick two points to define\ntwo corners of a rectangle')


            self.baseline.remove()
            self.canvas.draw()

    def interactiverectangle(self):
        self.HelpText.config(text='Click and drag the region you want to keep.')
        self.PreciseCrop.grid_forget()
        self.BufferEntry.grid_forget()
        self.BufferLabel.grid_forget()
        #self.InteractiveRectangle.state([tk.DISABLED])
        self.canvas.draw()
        def line_select_callback(eclick, erelease):
            'eclick and erelease are the press and release events'
            self.x1, self.y1 = eclick.xdata, eclick.ydata
            self.x2, self.y2 = erelease.xdata, erelease.ydata

        def toggle_selector(event):
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(self.ax, line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)
        plt.connect('key_press_event', toggle_selector)

        self.Crop.grid(row=5, columnspan=2)
        self.canvas.draw()

    def cropper(self):
        self.Crop.grid_forget()
        LeftxBound = floor(self.x1)
        RightxBound = floor(self.x2)
        TopyBound = floor(self.y1)  #Top visually, bottom for numerical purposes when y axis flipped
        BotyBound = floor(self.y2)  #Bottom visually, top for numerical purposes when y axis flipped

        try:
            self.buffer = int(self.BufferEntry.get())
        except ValueError as e:
            self.BufferEntry.insert(0, 0)
            self.buffer = int(self.BufferEntry.get())


        if LeftxBound < RightxBound:
            if TopyBound < BotyBound:
                self.img_cropped = self.img_arr[TopyBound-self.buffer:BotyBound+self.buffer,LeftxBound-self.buffer:RightxBound+self.buffer]
            if TopyBound > BotyBound:
                self.img_cropped = self.img_arr[BotyBound-self.buffer:TopyBound+self.buffer,LeftxBound-self.buffer:RightxBound+self.buffer]
        else:
            if TopyBound < BotyBound:
                self.img_cropped = self.img_arr[TopyBound-self.buffer:BotyBound+self.buffer,RightxBound-self.buffer:LeftxBound+self.buffer]
            if TopyBound > BotyBound:
                self.img_cropped = self.img_arr[BotyBound-self.buffer:TopyBound+self.buffer,RightxBound-self.buffer:LeftxBound+self.buffer]


        self.cropped_image = self.ax.imshow(self.img_cropped)

        self.canvas.draw()

        self.SaveImage.grid(row=6, columnspan=2)
        self.Crop.state([tk.DISABLED])
        self.HelpText.config(text='Save the image, select\nselect a directory to save the image')
        self.canvas.draw()

        self.rectline1.remove()
        self.rectline2.remove()
        self.rectline3.remove()
        self.rectline4.remove()
        self.canvas.draw()

    def precise_crop(self):
        self.BufferLabel.grid(row=6, columnspan=2)
        self.BufferEntry.grid(row=7, columnspan=2)
        self.HelpText.config(text='Click two opposite corners\nto define the desired rectangle.\n\nRight click to place points,\nmiddle click to end.\n\nChoose desired offset for the cropped image.')
        self.InteractiveRectangle.grid_forget()
        self.canvas.draw()
        #pick exact corners you want to crop, add in specified buffer
        self.pick_corners = PointPicker(self,2)
        self.after(100, self.draw_rect)

    def draw_rect(self):
        try:
            self.rect_point = np.array(self.pick_corners.points)
            if self.pick_corners.ended:
                del self.pick_corners
            self.after(100, self.draw_rect)

        except AttributeError as e:
            self.CornerX = [floor(i.get_xdata()[0]) for i in self.rect_point]
            self.CornerY = [floor(i.get_ydata()[0]) for i in self.rect_point]

            self.TopLeftX = self.CornerX[0]
            self.BottomRightX = self.CornerX[1]

            self.TopLeftY = self.CornerY[0]
            self.BottomRightY = self.CornerY[1]

            self.rectline1 = self.ax.plot([self.TopLeftX, self.BottomRightX],[self.TopLeftY,self.TopLeftY],'-o',color='deeppink')[0]
            self.rectline2 = self.ax.plot([self.TopLeftX, self.BottomRightX],[self.BottomRightY,self.BottomRightY],'-o',color='deeppink')[0]
            self.rectline3 = self.ax.plot([self.TopLeftX, self.TopLeftX],[self.TopLeftY,self.BottomRightY],'-o',color='deeppink')[0]
            self.rectline4 = self.ax.plot([self.BottomRightX, self.BottomRightX],[self.TopLeftY,self.BottomRightY],'-o',color='deeppink')[0]
            self.canvas.draw()

            for line in self.rect_point:
                line.remove()
            try:
                self.buffer = int(self.BufferEntry.get())
            except ValueError as e:
                self.BufferEntry.insert(0, 0)
                self.buffer = int(self.BufferEntry.get())

            CornerXList = np.array([self.TopLeftX, self.BottomRightX])
            CornerYList = np.array([self.TopLeftY, self.BottomRightY])

            self.x1 = CornerXList[np.argmin(CornerXList)]
            self.x2 = CornerXList[np.argmax(CornerXList)]
            self.y1 = CornerYList[np.argmin(CornerYList)]
            self.y2 = CornerYList[np.argmax(CornerYList)]

            self.Crop.grid(row=8, columnspan=2)
            #self.PreciseCrop.state([tk.DISABLED])
            self.canvas.draw()

    def save_image(self):
        #plt.savefig('cropped_image.jpg', bbox_inches='tight', transparent=True, pad_inches=0)
        self.g = tkfd.asksaveasfilename(
            parent=self, initialdir=self.image_path,
            title='Choose file',
            filetypes=[
                   ('jpeg images', '.jpg')]
            )

        try:
            plt.imsave(self.g, self.img_cropped)
            self.HelpText.config(text='Image Successfully Saved.')
        except ValueError as e:
            tk.messagebox.showerror(title='Saving Error', message='No location selected.\nPlease select a location to save the image.')


    def onclose(self):
        plt.close('all')
        self.destroy()


#-------------------------------------------------------------------------------
class PointPicker:

    def __init__(self, master, n):
        #self.ax = ax
        self.master = master
        self.n = n
        #self.fig = fig

        self.cid1 = self.master.fig.canvas.mpl_connect('button_press_event', self)
        self.points = []
        self.ended = False


    def __call__(self, event):
        if event.button == 3:
            self.pt, = self.master.ax.plot(event.xdata, event.ydata, 'o')
            self.master.fig.canvas.draw()
            self.points.append(self.pt,)

            if len(self.points) > self.n:
                print(self.points)
                self.points.pop(0).remove()
            self.master.canvas.draw()

        if event.button == 2:

            self.master.fig.canvas.mpl_disconnect(self.cid1)
            self.ended = True

    def end(self):
        self.master.fig.canvas.mpl_disconnect(self.cid1)
        self.ended = True






if __name__ == '__main__':
    app = ImageLoader()
    app.wm_title("Loaded Image:")

    #show the window
    app.mainloop()
