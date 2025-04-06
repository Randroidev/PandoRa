from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class CustomToolbar(NavigationToolbar2Tk):
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if t[0] != "Subplots"]