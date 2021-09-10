from tkinter import *
from tkinter import ttk, filedialog
from manager import Manager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.cm import get_cmap, ScalarMappable
from matplotlib.colors import Normalize
import smopy
import os


class BikeTripsGui:
    """
    Graphical interface. Acts like a View in a Model-View-Controller application.
    This GUI lets user choose which trip to plot, select folder with csv files, add new trip and clear db tables

    Attributes:

        manager: Manager object

        root: Tkinter main window

    Methods:



    """

    def __init__(self):
        self.manager = Manager()
        self.add_trips_to_manager()
        self.root = Tk()
        self.root.title('Bike trips manager')
        self.root.geometry('1366x768')
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.columnconfigure(index=0)
        self.mainframe.rowconfigure(index=0)
        self.mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
        self.canvas = None

        ttk.Button(self.mainframe, text='Select Directory', command=self.add_directory)\
            .grid(column=4, row=0, sticky=N)

        ttk.Button(self.mainframe, text='Add trips', command=self.add_trip).grid(column=5, row=0, sticky=N)

        self.trip_id = StringVar()
        ttk.Label(self.mainframe, text='Select trip ').grid(column=0, row=0, sticky=(N, E))
        self.trip_select = ttk.Combobox(self.mainframe, textvariable=self.trip_id)
        self.trip_select.state(['readonly'])
        self.trip_select.grid(column=1, row=0, sticky=(N, W))
        self.trip_select.bind('<<ComboboxSelected>>', self.show_trip)
        self.update_select_box()

        ttk.Button(self.mainframe, text='Clear database', command=self.clear_db).grid(column=6, row=0)

        self.color_bar_type = StringVar(value='By Speed')
        ttk.Label(self.mainframe, text='Select colorbar ').grid(column=2, row=0, sticky=(N, E))
        self.plot_type_select = ttk.Combobox(self.mainframe, textvariable=self.color_bar_type)
        self.plot_type_select.state(['readonly'])
        self.plot_type_select.grid(column=3, row=0, sticky=(N, W))
        self.plot_type_select.bind('<<ComboboxSelected>>', self.show_trip)
        self.plot_type_select['values'] = ['By Speed', 'By Altitude']

    def show_trip(self, *args):
        """
        Plots gps data of a trip using Smopy.

        Route is colored based on previously selecter colorbar type

        :param args: contains trip's id and colorbar type

        """
        if self.canvas is None:
            tr_id = self.trip_id.get()
            trip = self.manager.trips[int(tr_id)]
            trip_image = smopy.Map(trip.get_bbox())
            trip_image_pixels = trip.get_pixel_data(trip_image)

            figure = Figure(figsize=(1366/96, 768/96), dpi=96)
            ax = figure.add_subplot(111)
            trip_name = self.manager.read_trip_name(tr_id)
            ax.set_title(trip_name)
            trip_image.show_mpl(ax=ax, dpi=96)

            cmap = get_cmap('plasma')

            if self.color_bar_type.get() == 'By Speed':
                ax.scatter(trip_image_pixels[0], trip_image_pixels[1], c=trip.speed, cmap=cmap, s=4)
                mappable = ScalarMappable(norm=Normalize(vmin=min(trip.speed), vmax=max(trip.speed)), cmap=cmap)
                figure.colorbar(mappable, ax=ax, label='Speed in km/h')
            elif self.color_bar_type.get() == 'By Altitude':
                ax.scatter(trip_image_pixels[0], trip_image_pixels[1], c=trip.altitude, cmap=cmap, s=4)
                mappable = ScalarMappable(norm=Normalize(vmin=min(trip.altitude), vmax=max(trip.altitude)), cmap=cmap)
                figure.colorbar(mappable, ax=ax, label='Altitude in meters')

            self.canvas = FigureCanvasTkAgg(figure, master=self.mainframe)
            self.canvas.draw()

            toolbar = NavigationToolbar2Tk(self.canvas, self.mainframe, pack_toolbar=False)
            toolbar.update()
            toolbar.grid(column=1, row=1, sticky=N)

            self.canvas.get_tk_widget().grid(column=0, row=1, columnspan=7, sticky=S)

        else:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            self.show_trip()

    def update_select_box(self):
        """
        Updates select box after adding new trips

        """
        self.trip_select['values'] = []
        if not self.manager.db.check_if_empty():
            self.trip_select['values'] = list(self.manager.read_trip_ids())

        self.mainframe.update()

    def add_trip(self):
        """
        Add new trips chosen from directory

        """
        in_files = filedialog.askopenfiles()
        in_files = [x.name.rsplit('/', 1)[-1] for x in in_files]

        self.manager.insert_trips(in_files)
        self.update_select_box()
        self.add_trips_to_manager()

    def add_directory(self):
        """
        Adds main directory of files and populates database based on those files

        """
        directory = filedialog.askdirectory()
        filenames = sorted(os.listdir(directory))
        self.manager.populate_db(filenames)
        self.update_select_box()
        self.add_trips_to_manager()

    def add_trips_to_manager(self):
        """
        Sets manager's trips property

        """
        if not self.manager.db.check_if_empty():
            self.manager.save_all_trips()

    def clear_db(self):
        """
        Command to clear tables and update select box

        """
        self.manager.delete_rows()
        self.update_select_box()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
   #root = Tk()
    #manager = Manager()
    BikeTripsGui().run()
   # root.mainloop()
