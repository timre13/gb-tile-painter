"""
The main window of gb-tile-painter
"""

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmsgb
import sys

import images # Image data, this file is in this directory

def toHex(value: int) -> str:
    """Return the hex representation of an integer."""
    return hex(value)[2:].upper().zfill(2)

class MainWindow(tk.Tk):
    """Main window of gb-tile-painter."""
    
    def __init__(self):
        """See MainWindow's docstring."""
        
        super().__init__() # call tk.Tk()'s constructor
        
        self.palette = ("#ffffff", "#c8c8c8", "#646464", "#000000")
        self.realPalette = ("#82870d", "#5c7122", "#3a5336", "#1c3628")
        
        self.tileWidth = 8
        self.tileHeight = 8
        self.scale = 40
        self.drawColorIndex = 0
        
        self.pixelColorIndexes = [0]*(self.tileWidth*self.tileHeight)
        
        self.title("GB Tile Painter")
        self.minsize(100, 100)
        
        try:
            self.iconphoto(True, tk.PhotoImage(data=images.appicon))
        except:
            sys.stdout.write("Failed to set icon: "+str(sys.exc_info()[1]))
        
        self.setupWidgets()
        self.displayWidgets()
        self.resizable(False, False)
    
    ############################## GUI Functions ##############################
    
    def setupWidgets(self) -> None:
        """Create the widgets and set their properties."""
        
        self.saveHexdumpButtonImage = tk.PhotoImage(data=images.saveHexdump)
        self.saveBinaryButtonImage = tk.PhotoImage(data=images.saveBinary)
        self.saveButtonFrame = tk.LabelFrame(self)
        self.saveHexdumpButton = tk.Button(self.saveButtonFrame, image=self.saveHexdumpButtonImage, command=self.onSaveHexdumpButtonClicked)
        self.saveFileButton = tk.Button(self.saveButtonFrame, image=self.saveBinaryButtonImage, command=self.onSaveFileButtonClicked)
        
        self.drawingWidgetFrame = tk.LabelFrame(self)
        self.canvas = tk.Canvas(self.drawingWidgetFrame, bg="white",
                                width=self.tileWidth*self.scale,
                                height=self.tileHeight*self.scale)
        self.canvas.bind("<B1-Motion>", self.onLeftMouseButtonHeldMovementOnCanvas)
        self.canvas.bind("<Button-1>", self.onLeftMouseButtonHeldMovementOnCanvas)
        self.canvas.bind("<ButtonRelease-1>", self.afterLeftMouseButtonHeldMovementOnCanvas)
        self.redrawCanvasGrid()
        
        self.setColorButtonFrame = tk.LabelFrame(self.drawingWidgetFrame)
        self.colorSetterButtons = (
            tk.Button(self.setColorButtonFrame,
                      bg=self.palette[0],
                      command=lambda: self.setDrawColor(0)),
            tk.Button(self.setColorButtonFrame,
                      bg=self.palette[1],
                      command=lambda: self.setDrawColor(1)),
            tk.Button(self.setColorButtonFrame,
                      bg=self.palette[2],
                      command=lambda: self.setDrawColor(2)),
            tk.Button(self.setColorButtonFrame,
                      bg=self.palette[3],
                      command=lambda: self.setDrawColor(3))
        )
        self.previewModeCheckbox = ttk.Checkbutton(self.setColorButtonFrame, command=self.onPreviewModeCheckboxClicked)
        
        self.hexdumpWidgetFrame = tk.Frame(self)
        self.hexdumpWidget = tk.Entry(self.hexdumpWidgetFrame, font=("TkFixedFont", 10, "normal"), width=45)
        self.hexdumpWidget.bind("<Key>", lambda _: "break")
        self.hexdumpWidget.bind("<Button>", lambda _: "break")
        self.hexdumpWidget.bind("<Leave>", lambda _: self.hexdumpWidget.selection_clear())
        self.copyHexdumpButton = tk.Button(self.hexdumpWidgetFrame,
                                           text="\N{CLIPBOARD}",
                                           command=self.onCopyHexdumpButtonClicked)
    
    def displayWidgets(self) -> None:
        """Pack the widgets to the window."""
        
        self.saveButtonFrame.pack(side=tk.TOP, fill=tk.X)
        self.saveHexdumpButton.pack(side=tk.LEFT)
        self.saveFileButton.pack(side=tk.LEFT)
        self.drawingWidgetFrame.pack(side=tk.TOP)
        self.canvas.pack(side=tk.RIGHT)
        self.setColorButtonFrame.pack(side=tk.LEFT, fill=tk.Y)
        for button in self.colorSetterButtons:
            button.pack(side=tk.TOP, fill=tk.X)
        self.previewModeCheckbox.pack(side=tk.BOTTOM)
        self.hexdumpWidgetFrame.pack(side=tk.BOTTOM, fill=tk.X)
        self.hexdumpWidget.pack(side=tk.LEFT)
        self.copyHexdumpButton.pack(side=tk.RIGHT)
        self.updateHexdumpWidget()
    
    def redrawCanvasGrid(self) -> None:
        """Redraw the grid of the canvas, should be called after drawing on the canvas."""
        
        lineColors = ("black", "white")

        for i in range(2):
            for x in range(self.tileWidth):
                self.canvas.create_line(
                    (x*self.scale, 0, x*self.scale, self.tileHeight*self.scale),
                    fill=lineColors[i], dash=(5, 5), dashoffset=i*5)
                
        for i in range(2):
            for y in range(self.tileHeight):
                self.canvas.create_line(
                    (0, y*self.scale, self.tileWidth*self.scale, y*self.scale),
                    fill=lineColors[i], dash=(5, 5), dashoffset=i*5)
    
    def updateHexdumpWidget(self) -> None:
        """Update the hexdump widget to contain the current image's data."""
        
        self.hexdumpWidget.delete(0, tk.END)
        self.hexdumpWidget.insert(tk.END, self.getHexdump())
    
    ############################## Event Handlers #############################

    def onLeftMouseButtonHeldMovementOnCanvas(self, event: tk.Event) -> None:
        """Draw on the canvas when a `B1-Motion` event is happening on it."""
        
        if event.x >= self.tileWidth*self.scale or event.y >= self.tileHeight*self.scale:
            return
        
        if "selected" in self.previewModeCheckbox.state():
            fillColor = self.realPalette[self.drawColorIndex]
        else:
            fillColor = self.palette[self.drawColorIndex]
        
        self.canvas.create_rectangle(
            (event.x//self.scale*self.scale, event.y//self.scale*self.scale,
             (event.x//self.scale+1)*self.scale, (event.y//self.scale+1)*self.scale),
            fill=fillColor, outline="")
        self.pixelColorIndexes[event.x//self.scale+event.y//self.scale*self.tileWidth] = self.drawColorIndex
    
    def afterLeftMouseButtonHeldMovementOnCanvas(self, _) -> None:
        """Redraw the grid after a `B1-Motion` event on the canvas."""
        
        if "selected" not in self.previewModeCheckbox.state():
            self.redrawCanvasGrid()
        self.updateHexdumpWidget()
    
    def onPreviewModeCheckboxClicked(self) -> None:
        """Switch between painting and preview mode when the checkbox is clicked."""
        
        for i in range(self.tileWidth*self.tileHeight):
            if "selected" in self.previewModeCheckbox.state():
                fillColor = self.realPalette[self.pixelColorIndexes[i]]
            else:
                fillColor = self.palette[self.pixelColorIndexes[i]]
            
            self.canvas.create_rectangle(
                (i%self.tileWidth*self.scale, i//self.tileWidth*self.scale,
                 (i%self.tileWidth+1)*self.scale, (i//self.tileWidth+1)*self.scale),
                outline="", fill=fillColor)
        
        for i, button in enumerate(self.colorSetterButtons):
            if "selected" in self.previewModeCheckbox.state():
                button["bg"] = self.realPalette[i]
            else:
                button["bg"] = self.palette[i]
        
        if "selected" not in self.previewModeCheckbox.state():
            self.redrawCanvasGrid()
        
    def onCopyHexdumpButtonClicked(self) -> None:
        """Copy the hexdump to the clipboard when copyHexdumpButton is clicked."""
        self.clipboard_clear()
        self.clipboard_append(self.getHexdump())
    
    def onSaveHexdumpButtonClicked(self) -> None:
        """Save the hexdump to a file when saveHexdumpButton is clicked."""
        
        filename = tkfd.asksaveasfilename(parent=self)
        if filename is not None and len(filename):
            try:
                with open(filename, "w+") as file:
                    file.write(self.getHexdump())
            except:
                tkmsgb.showerror("File Save Error",
                                 "Failed to save file: "+str(sys.exc_info()[1]))
    
    def onSaveFileButtonClicked(self) -> None:
        """Save the image's binary data to a file when saveFileButton is clicked."""
        
        filename = tkfd.asksaveasfilename(parent=self)
        if filename is not None and len(filename):
            try:
                with open(filename, "wb+") as file:
                    file.write(bytes(self.getImageData()))
            except:
                tkmsgb.showerror("File Save Error",
                                 "Failed to save file: "+str(sys.exc_info()[1]))
    
    ############################## Image Data Getters #########################
    
    def getHexdump(self) -> str:
        """Return the hexdump of the image data."""
        
        output = ""
        
        # TODO: Support tile sizes other than 8x8
        for y in range(8):
            leftByte = 0x00
            rightByte = 0x00
            for x in range(8):
                leftByte |= (self.pixelColorIndexes[y*8+x] & 0b01) << 7-x
                rightByte |= (self.pixelColorIndexes[y*8+x] & 0b10) >> 1 << 7-x
            
            output += toHex(leftByte) + " " + toHex(rightByte) + " "
        
        return output[:-1]
    
    def getImageData(self) -> list:
        """Return the image data as list of bytes."""
        
        output = []
        
        # TODO: Support tile sizes other than 8x8
        for y in range(8):
            leftByte = 0x00
            rightByte = 0x00
            for x in range(8):
                leftByte |= (self.pixelColorIndexes[y*8+x] & 0b01) << 7-x
                rightByte |= (self.pixelColorIndexes[y*8+x] & 0b10) >> 1 << 7-x
            
            output += leftByte, rightByte
        
        return output
    
    ############################## Helper Functions ##############################

    def setDrawColor(self, index: int) -> None:
        """Set the current drawing color index to the argument."""
        
        assert(index >= 0 and index < 4)
        self.drawColorIndex = index