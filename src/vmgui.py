import tkinter

mainWindow = tkinter.Tk()
mainWindow.title('Virtual Mouse')
mainWindow.geometry('640x480')

button1 = tkinter.Button(mainWindow, text="Start")
button1.grid(row=0, column=0)

# configure the columns

mainWindow.grid_columnconfigure(0, weight=2)

mainWindow.mainloop()

