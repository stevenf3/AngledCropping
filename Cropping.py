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
        self.CloseButton.grid(row=10, columnspan=2)

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

        self.BetterPreciseCrop = ttk.Button(self.frame2, text='Better Precise Crop', command=self.better_precise_crop, state=tk.ACTIVE)
        self.BetterPreciseCrop.grid()
        self.BetterPreciseCrop.grid_forget()

        self.HelpText = ttk.Label(self.frame2, text='Load an image to begin.', justify='center')
        self.HelpText.grid(row=0, columnspan=2)

        self.UndoButton = ttk.Button(self.frame2, text='Undo', command=self.undo, state=tk.ACTIVE)
        self.UndoButton.grid()
        self.UndoButton.grid_forget()


#-----------------------------functions-----------------------------------------
    def open_image(self):

        self.f = tkfd.askopenfilename(
            parent=self, initialdir='.',
            title='Choose file',
            filetypes=[
                   ('jpeg images', '.jpg')]
            )
        self.step = 1

        try:
            self.image_path = os.path.dirname(self.f)
            self.img_arr = plt.imread(self.f)
            self.img_arr = np.array(self.img_arr)
            try:
                print('running 0')
                self.cropped_image.remove()
                print('running 1')
                self.SaveImage.grid_forget()
                self.UndoButton.grid_forget()
                self.PickPoints['text'] = 'Select Baseline'
                self.PickPoints.grid(row=3, columnspan=2)
                self.dummy.remove() #fake variable to force error
                try:
                    self.BufferLabel.grid_forget()
                    self.BufferEntry.grid_forget()
                    self.Crop.grid_forget()
                    self.SaveImage.grid_forget()
                    try:
                        self.rectline1.remove()
                        self.rectline2.remove()
                        self.rectline3.remove()
                        self.rectline4.remove()
                    except ValueError:
                        print('error check good:', e)
                        print('instance 1')
                        pass
                except AttributeError:
                    print('instance 2')
                    pass
            except AttributeError or ValueError:
                print('instance 3')
                try:
                    self.loaded_image.remove()
                    self.InteractiveRectangle.grid_forget()
                    self.PreciseCrop.grid_forget()
                    self.BetterPreciseCrop.grid_forget()
                    self.UndoButton.grid_forget()
                    self.PickPoints['text'] = 'Select Baseline'
                    self.PickPoints.grid(row=2, columnspan=2)
                    print('original removed')
                except Exception:
                    try:
                        self.rotated_image.remove()
                        self.InteractiveRectangle.grid_forget()
                        self.PreciseCrop.grid_forget()
                        self.BetterPreciseCrop.grid_forget()
                        self.UndoButton.grid_forget()
                        self.PickPoints['text'] = 'Select Baseline'
                        self.PickPoints.grid(row=2, columnspan=2)
                        print('rotated removed')
                    except:
                        print('Nothing to delete, this is the first loaded image. If this isnt, unknown error')
            print('testing')
            self.loaded_image = self.ax.imshow(self.img_arr)
            print('loaded_image worked')
            self.PickPoints.grid(row=2, columnspan=2)
            self.HelpText.config(text='Select a Baseline \nthat follows the angle of\nthe bottom of the desired region\n\nRight click to place points,\nmiddle click to end.')
            self.canvas.draw()
        except Exception as e:
            if e == ValueError:
                print('this is the error')
                pass
            elif e == AttributeError:
                tk.messagebox.showerror(title='Loading Error', message='No image selected, please select an image')



    def pickpoints(self):
        if self.PickPoints['text'] == 'Select Baseline':
            self.pointpick = PointPicker(self, 2)
            self.step = 2
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

            self.rot_img_arr = ndimage.rotate(self.img_arr, self.alpha, reshape=False)
            self.loaded_image.remove()
            self.rotated_image = self.ax.imshow(self.rot_img_arr)
            self.baseline = self.ax.plot(self.xs, self.ys, '-o', color='green')[0]

            self.canvas.draw()

            self.PreciseCrop.grid(row=3, columnspan=2)
            self.InteractiveRectangle.grid(row=5, columnspan=2)
            self.BetterPreciseCrop['state'] = 'normal'
            self.BetterPreciseCrop['text'] = 'Better Precise Crop'
            self.BetterPreciseCrop.grid(row=4, columnspan=2)
            self.UndoButton.grid(row=11, columnspan=2)
            self.PickPoints.grid_forget()

            self.HelpText.config(text='Choose your cropping method:\n\nInteractive Rectangle:\nA draggable rectangle for less\nprecise cropping.\n\nPrecise Cropping:\nClick two points to define\ntwo corners of a rectangle\n\nBetter Precise Cropping: \nInput as many points\nas you want to generate\na smart cropping region')


            self.baseline.remove()
            self.canvas.draw()

    def interactiverectangle(self):
        self.HelpText.config(text='Click and drag the region you want to keep.')
        self.PreciseCrop.grid_forget()
        self.BufferEntry.grid_forget()
        self.BufferLabel.grid_forget()
        self.BetterPreciseCrop.grid_forget()
        self.InteractiveRectangle.state([tk.DISABLED])
        self.canvas.draw()

        self.step = 3.1
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

        self.Crop.grid(row=9, columnspan=2)
        self.canvas.draw()

    def cropper(self):

        self.BufferLabel.grid_forget()
        self.BufferEntry.grid_forget()

        if self.step == 3.2:
            self.step = 4.2
        elif self.step == 3.3:
            self.step=4.3
        elif self.step == 3.1:
            self.step = 4.1
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
                self.img_cropped = self.rot_img_arr[TopyBound-self.buffer:BotyBound+self.buffer,LeftxBound-self.buffer:RightxBound+self.buffer]
            if TopyBound > BotyBound:
                self.img_cropped = self.rot_img_arr[BotyBound-self.buffer:TopyBound+self.buffer,LeftxBound-self.buffer:RightxBound+self.buffer]
        else:
            if TopyBound < BotyBound:
                self.img_cropped = self.rot_img_arr[TopyBound-self.buffer:BotyBound+self.buffer,RightxBound-self.buffer:LeftxBound+self.buffer]
            if TopyBound > BotyBound:
                self.img_cropped = self.rot_img_arr[BotyBound-self.buffer:TopyBound+self.buffer,RightxBound-self.buffer:LeftxBound+self.buffer]

        self.cropped_image = self.ax.imshow(self.img_cropped)

        self.canvas.draw()

        try:
            self.rectline1.remove()
            self.rectline2.remove()
            self.rectline3.remove()
            self.rectline4.remove()
        except AttributeError:
            pass

        self.SaveImage.grid(row=10, columnspan=2)
        self.HelpText.config(text='Save the image, select\nselect a directory to save the image')
        self.UndoButton.grid(row=11, columnspan=3)
        self.InteractiveRectangle.state([tk.ACTIVE])
        self.InteractiveRectangle.grid_forget()
        self.BetterPreciseCrop.grid_forget()
        self.canvas.draw()



    def precise_crop(self):
        if self.PreciseCrop['text'] == 'Precise Cropping':
            self.BufferLabel.grid(row=7, columnspan=2)
            self.BufferEntry.grid(row=8, columnspan=2)
            self.HelpText.config(text='Click two opposite corners\nto define the desired rectangle.\n\nRight click to place points,\nmiddle click to end.\n\nChoose desired offset for the cropped image.')
            self.InteractiveRectangle.grid_forget()
            self.BetterPreciseCrop.grid_forget()
            self.canvas.draw()

            self.step = 3.2
            #pick exact corners you want to crop, add in specified buffer
            self.pick_corners = PointPicker(self, 2)
            self.after(100, self.draw_rect)

            self.PreciseCrop['text'] = 'Done'

        elif self.PreciseCrop['text'] == 'Done':
            self.PreciseCrop['text'] = 'Precise Cropping'
            self.pick_corners.end()

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

            self.Crop.grid(row=9, columnspan=2)
            #self.PreciseCrop.state([tk.DISABLED])
            self.canvas.draw()

    def save_image(self):
        self.g = tkfd.asksaveasfilename(
            parent=self, initialdir=self.image_path,
            title='Choose file',
            filetypes=[
                   ('jpeg images', '.jpg')]
            )
        print(os.path.basename(self.g))
        try:
            plt.imsave(self.g, self.img_cropped)
            self.HelpText.config(text='Image Successfully Saved.')
        except ValueError as e:
            if '.' in os.path.basename(self.g):
                tk.messagebox.showerror(title='Saving Error', message='No location selected.\nPlease select a location to save the image.')
            else:
                tk.messagebox.showerror(title='Saving Error', message='Missing File Extension.\nPlease add an extension (i.e. .jpg) at the end of the desired file name.')

    def undo(self):

        if self.step == 2:
            self.rotated_image.remove()
            del self.rotated_image
            self.loaded_image = self.ax.imshow(self.img_arr)
            self.canvas.draw()

            self.PickPoints['text'] = 'Select Baseline'
            self.PickPoints.grid(row=2, columnspan=2)

            self.InteractiveRectangle.grid_forget()
            self.PreciseCrop.grid_forget()

        elif self.step == 3.2:
            self.rectline1.remove()
            self.rectline2.remove()
            self.rectline3.remove()
            self.rectline4.remove()
            self.canvas.draw()

            self.step = 2

            self.PreciseCrop.grid(row=3, columnspan=2)
            self.PreciseCrop['state'] = 'normal'
            self.BufferLabel.grid(row=7, columnspan=2)
            self.BufferEntry.grid(row=8, columnspan=2)
            self.Crop.grid_forget()


        elif self.step == 4.1:
            self.cropped_image.remove()
            self.rotated_image = self.ax.imshow(self.rot_img_arr)
            self.canvas.draw()

            self.InteractiveRectangle.grid(row=5, columnspan=2)
            self.InteractiveRectangle['state'] = 'normal'
            self.SaveImage.grid_forget()
            self.Crop.grid(row=9, columnspan=2)
            self.step = 3.1

        elif self.step == 4.2:
            self.BufferLabel.grid(row=7, columnspan=2)
            self.BufferEntry.grid(row=8, columnspan=2)
            self.rectline1 = self.ax.plot([self.TopLeftX, self.BottomRightX],[self.TopLeftY,self.TopLeftY],'-o',color='deeppink')[0]
            self.rectline2 = self.ax.plot([self.TopLeftX, self.BottomRightX],[self.BottomRightY,self.BottomRightY],'-o',color='deeppink')[0]
            self.rectline3 = self.ax.plot([self.TopLeftX, self.TopLeftX],[self.TopLeftY,self.BottomRightY],'-o',color='deeppink')[0]
            self.rectline4 = self.ax.plot([self.BottomRightX, self.BottomRightX],[self.TopLeftY,self.BottomRightY],'-o',color='deeppink')[0]

            self.cropped_image.remove()
            self.rotated_image = self.ax.imshow(self.rot_img_arr)

            self.canvas.draw()

            self.SaveImage.grid_forget()
            self.Crop.grid(row=9, columnspan=2)

            self.step = 3.2

        elif self.step == 4.3:
            self.BufferLabel.grid(row=7, columnspan=2)
            self.BufferEntry.grid(row=8, columnspan=2)

            self.cropped_image.remove()
            self.rotated_image = self.ax.imshow(self.rot_img_arr)

            self.rectline1 = self.ax.plot([self.x1, self.x2],[self.y1,self.y1],'-o',color='deeppink')[0]
            self.rectline2 = self.ax.plot([self.x1, self.x2],[self.y2,self.y2],'-o',color='deeppink')[0]
            self.rectline3 = self.ax.plot([self.x1, self.x1],[self.y1,self.y2],'-o',color='orange')[0]
            self.rectline4 = self.ax.plot([self.x2, self.x2],[self.y1,self.y2],'-o',color='chartreuse')[0]

            self.canvas.draw()

            self.SaveImage.grid_forget()
            self.Crop.grid(row=9, columnspan=2)

            self.step = 3.3

    def better_precise_crop(self):
        if self.BetterPreciseCrop['text'] == 'Better Precise Crop':
            self.PreciseCrop.grid_forget()
            self.InteractiveRectangle.grid_forget()
            self.BufferLabel.grid(row=7, columnspan=2)
            self.BufferEntry.grid(row=8, columnspan=2)

            self.HelpText.config(text='Select all edges of the region you want to crop.\nInput as many points as needed,\n a cropping region will automatically\nbe created to fit the points.\n\nRight click to place,\nmiddle click to end.')

            self.step = 3.3
            self.pick_all_corners = PointPickerNoCap(self)
            self.after(100, self.better_rect)

            self.BetterPreciseCrop['text'] = 'Done'

        elif self.BetterPreciseCrop['text'] == 'Done':
            self.BetterPreciseCrop['text'] = 'Better Precise Crop'
            self.pick_all_corners.end()

    def better_rect(self):
        try:
            self.better_rect_point = np.array(self.pick_all_corners.points)
            if self.pick_all_corners.ended:
                del self.pick_all_corners
            self.after(100, self.better_rect)

        except AttributeError as e:
            self.BetterCornerX = [floor(i.get_xdata()[0]) for i in self.better_rect_point]
            self.BetterCornerY = [floor(i.get_ydata()[0]) for i in self.better_rect_point]

            self.x1 = self.BetterCornerX[np.argmin(self.BetterCornerX)]
            self.x2 = self.BetterCornerX[np.argmax(self.BetterCornerX)]

            self.y1 = self.BetterCornerY[np.argmin(self.BetterCornerY)]
            self.y2 = self.BetterCornerY[np.argmax(self.BetterCornerY)]

            self.rectline1 = self.ax.plot([self.x1, self.x2],[self.y1,self.y1],'-o',color='deeppink')[0]
            self.rectline2 = self.ax.plot([self.x1, self.x2],[self.y2,self.y2],'-o',color='deeppink')[0]
            self.rectline3 = self.ax.plot([self.x1, self.x1],[self.y1,self.y2],'-o',color='orange')[0]
            self.rectline4 = self.ax.plot([self.x2, self.x2],[self.y1,self.y2],'-o',color='chartreuse')[0]
            self.canvas.draw()

            for line in self.better_rect_point:
                line.remove()

            self.Crop.grid(row=9, columnspan=2)


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


class PointPickerNoCap:

    def __init__(self, master):
        #self.ax = ax
        self.master = master
        #self.fig = fig

        self.cid1 = self.master.fig.canvas.mpl_connect('button_press_event', self)
        self.points = []
        self.ended = False


    def __call__(self, event):
        if event.button == 3:
            self.pt, = self.master.ax.plot(event.xdata, event.ydata, 'o')
            self.master.fig.canvas.draw()
            self.points.append(self.pt,)


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
