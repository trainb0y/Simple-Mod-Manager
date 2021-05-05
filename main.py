import tkinter as tk
import os, shutil, json
import tkinter.messagebox
from tkinter import filedialog



while True:
    try: 
        f= open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"smm_settings.json"), "r")
        settings = json.load(f)
        f.close()
        temp = tk.Tk() # Have to have a base window for the messageboxes
        temp.withdraw() # Make it dissapear
        try: 
            df_dir = settings["DF Dir"]
        except KeyError:
            tkinter.messagebox.showwarning("Warning","A Dwarf Fortress folder has not been selected! \nPlease select it in Settings\n Defaulting to program directory")
            df_dir = os.path.dirname(os.path.abspath(__file__))
        try: 
            mod_dir = settings["Mod Dir"]
        except KeyError:
            tkinter.messagebox.showwarning("Warning","A Mods folder has not been selected! \nPlease select it in Settings\n Defaulting to a folder \"mods\" in the DF Main Directory")
            mod_dir = os.path.join(df_dir,"mods")
        temp.destroy() # Get rid of the temporary tk, as we create a new one later.
        break

    except FileNotFoundError: 
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"smm_settings.json"), "x") as f:
            json.dump({},f)
        # Create the file and try again
    
    


def merge_dirs(root_src_dir,root_dst_dir): # Thank you StackOverflow!
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir) # Was move, I changed this hopefully didn't break anything


class SettingsWindow(tk.Toplevel):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.grid()
        self.create_widgets()
    
    def create_widgets(self):
        self.df_dir_label = tk.Label(self,text="Main Dwarf Fortress Folder")
        self.df_dir_label.grid(row=0,column=0)
        self.df_dir_strvar = tk.StringVar(self)
        self.df_dir_strvar.set("")
        self.df_dir_entry = tk.Entry(self,width=40,textvariable=self.df_dir_strvar)
        self.df_dir_entry.grid(row=0,column=1)
        self.df_dir_browse_button = tk.Button(self,text="Browse",
            command=lambda: self.df_dir_strvar.set(filedialog.askdirectory(title="Main Dwarf Fortress Folder")))
        self.df_dir_browse_button.grid(row=0,column=3)


        self.mod_dir_label = tk.Label(self,text="Mods Folder")
        self.mod_dir_label.grid(row=1,column=0)
        self.mod_dir_strvar = tk.StringVar(self)
        self.mod_dir_strvar.set("")
        self.mod_dir_entry = tk.Entry(self,width=40,textvariable=self.mod_dir_strvar)
        self.mod_dir_entry.grid(row=1,column=1)
        self.mod_dir_browse_button = tk.Button(self,text="Browse",
            command=lambda: self.mod_dir_strvar.set(filedialog.askdirectory(title="Mods Folder")))
        self.mod_dir_browse_button.grid(row=1,column=3)

        # Put the current directories in the Entrys
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"smm_settings.json"), "r") as f:
            settings = json.load(f)
            try:
                self.mod_dir_strvar.set(settings["Mod Dir"])
                self.df_dir_strvar.set(settings["DF Dir"])
            except KeyError:
                pass # KeyError if they haven't selected it yet.
                    # Without this it never renders the buttons


        self.apply_button = tk.Button(self,text="Apply",command=self.apply_settings)
        self.apply_button.grid(row=2,column=0,ipadx=30)

        self.cancel_button = tk.Button(self,text="Cancel",command=self.destroy)
        self.cancel_button.grid(row=2,column=1,ipadx=30)
    
    def apply_settings(self):
        global df_dir, mod_dir
        df_dir = self.df_dir_strvar.get()
        mod_dir = self.mod_dir_strvar.get()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"smm_settings.json"), "w") as f:
            json.dump({"DF Dir":df_dir,"Mod Dir":mod_dir},f) # Save the json

        self.master.find_avalible_mods()
        self.master.find_loaded_mods()

        tkinter.messagebox.showinfo("Success","Changes have been applied")
        


class MainWindow(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Simple Mod Manager")
        self.grid()
        self.create_widgets()
    
    def create_widgets(self):
       
        self.help_button = tk.Button(self,text="Help",command=lambda: tkinter.messagebox.showinfo("Help",'This program can help with the loading and unloading of mods for Dwarf Fortress. Mod folders should go in a mods folder, selected in the settings. Mod folders should contain a folder called "raw" (without the quotes) that contains all of the files to load in. Anything outside of the raw folder is ignored. \n\nPlease do not delete mod_info.json, as doing such will cause whatever is currently in the DF raw folder to become the default. (Well, unless you want it to be)\n\nTHERE IS NO GUARANTEE THAT THIS WILL NOT DESTROY OR OTHERWISE DAMAGE ALL RAWS\n\nIf something does happen, an original copy of the DF raws can be found in the raw-original directory.'))
        self.help_button.grid(row=0,column=0,ipadx=30)

        self.settings_button = tk.Button(self,text="Settings",command=self.open_settings)
        self.settings_button.grid(row=0,column=1,ipadx=30)

        self.loaded_mods_labelframe = tk.LabelFrame(self,text="Loaded Mods",bd=6) # bd is border thickness
        self.loaded_mods_labelframe.grid(row=1,column=0,columnspan=2)

        self.loaded_mods_listbox = tk.Listbox(self.loaded_mods_labelframe,width=30,selectmode=tk.BROWSE)
        self.loaded_mods_scrollbar = tk.Scrollbar(self.loaded_mods_labelframe,orient="vertical",command=self.loaded_mods_listbox.yview)
        self.loaded_mods_listbox.configure(yscrollcommand=self.loaded_mods_scrollbar.set)

        self.loaded_mods_listbox.grid(row=0,pady=10,padx=10,columnspan=2, sticky="nsew")
        self.loaded_mods_scrollbar.grid(row=0, column=3, sticky="ns")

        self.load_button = tk.Button(self,text="Load Mod",command=self.load_mod,pady=5)
        self.load_button.grid(row=2,column=0,sticky="ew")

        self.remove_button = tk.Button(self,text="Remove Mod",command=self.remove_mod,pady=5)
        self.remove_button.grid(row=2,column=1,sticky="ew")

        self.available_mods_labelframe = tk.LabelFrame(self,text="Available Mods",bd=6)
        self.available_mods_labelframe.grid(row=3,column=0,columnspan=2)

        self.available_mods_listbox = tk.Listbox(self.available_mods_labelframe,width=30,selectmode=tk.BROWSE)
        self.available_mods_scrollbar = tk.Scrollbar(self.available_mods_labelframe,orient="vertical",command=self.available_mods_listbox.yview)
        self.available_mods_listbox.configure(yscrollcommand=self.available_mods_scrollbar.set)

        self.available_mods_listbox.grid(row=0,pady=10,padx=10,columnspan=2, sticky="nsew")
        self.available_mods_scrollbar.grid(row=0, column=3, sticky="ns")

        self.find_avalible_mods()
        self.find_loaded_mods()


    def find_loaded_mods(self):
        self.loaded_mods_listbox.delete(0,tk.END) # Delete all entries before adding new ones
        # Get a list of loaded mods
        try:
            with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
                mod_info = json.load(f)
            for mod in mod_info["Loaded Mods"]:
                if mod != " ": # That is the default starter value
                    self.loaded_mods_listbox.insert(tk.END,mod)
        except FileNotFoundError:
            tkinter.messagebox.showinfo("File not found!","mod_info.json not found, creating in main DF directory")
            with open(os.path.join(df_dir,"mod_info.json"), "x") as f:
                json.dump({"Loaded Mods":[]},f)


    def find_avalible_mods(self):
        self.available_mods_listbox.delete(0,tk.END) # Delete all entries before adding new ones
        # Get a list of avaiblible mods 
        self.avalible_mods = {}
        try:
            for mod in os.listdir(mod_dir):
                #print(f"Possible mod folder: {mod}") 
                #print(os.path.join(mod_dir,mod))
                if os.path.isdir(os.path.join(mod_dir,mod)): # Mods need to be directories
                    #print(f"Items inside of {mod}: {os.listdir(os.path.join(mod_dir,mod))}")
                    for possible_raw_folder in os.listdir(os.path.join(mod_dir,mod)): 
                        if os.path.isdir(os.path.join(mod_dir,mod,possible_raw_folder)) and possible_raw_folder == "raw": # raw folder inside the mod folder contains everything we need
                            # We now this directory inside of Mods contains a directory named "raw", so it seems to be a valid mod
                            # Add it to the modlist, if it isn't already there
                            try:
                                with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
                                    mod_info = json.load(f)

                            except FileNotFoundError: # The file doesn't exist yet, probably the first time running this
                                mod_info = {"Loaded Mods":[" "]} # The spaces are there so that it isn't saved as null
                                with open(os.path.join(df_dir,"mod_info.json"),"w") as f:
                                    json.dump(mod_info,f)
                                
                                # We should also copy DF's raws because a good chunk of mods overwrite them
                                merge_dirs(os.path.join(df_dir,"raw"),os.path.join(df_dir,"raw-original"))
            
                            if mod not in mod_info["Loaded Mods"]:
                                self.available_mods_listbox.insert(tk.END,mod)
                                self.avalible_mods[mod] = os.path.join(os.path.join(mod_dir,mod))  
                                #print(f"Found raw folder in {mod}")

        except FileNotFoundError: # Generally this means there is no mod folder.
            tkinter.messagebox.showerror("Error",'Mods folder not found! Please create a "mods" folder and select it in the settings!')
            # raise SystemExit # What sys.exit does, without importing sys


    def load_mod(self,mod=False):
        # Figure out what the user has selected
        if mod == False:
            try:
                mod = self.available_mods_listbox.get(self.available_mods_listbox.curselection())
            except tk.TclError:
                tkinter.messagebox.showerror("Error","No mod selected to install!")
                return

        merge_dirs(os.path.join(mod_dir,mod,"raw"),os.path.join(df_dir,"raw"))# Add all files in the mod folder to the DF raws
        
        with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
            mod_info = json.load(f)

        # Now we have mod_info, let's update it.

        mod_info["Loaded Mods"].append(mod)

        with open(os.path.join(df_dir,"mod_info.json"), "w") as f:
            json.dump(mod_info,f) # Save the json
        
        self.find_avalible_mods()
        self.find_loaded_mods()

    def open_settings(self):
        SettingsWindow(self)
        

    def remove_mod(self): 
        try:
            removed_mod = self.loaded_mods_listbox.get(self.loaded_mods_listbox.curselection())
        except tk.TclError:
            tkinter.messagebox.showerror("Error","No mod selected to uninstall!")
            return
        
        if tkinter.messagebox.askyesno("Warning!", "This will uninstall all manually-installed mods. Are you sure you want to continue?") == False:
            return
        

        with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
            mod_info = json.load(f)

        # Now we have mod_info, let's update it.

        mod_info["Loaded Mods"].remove(removed_mod)

        # Multiple ways I could go about this
        # A) Compare every raw in the mod with the raw in the raws folder
        #   remove the proper files, and try to peice the raws back together
        #   using the original DF ones.
        # B) Remove all the mods, replace the raws with the original raws, and 
        #   re-install the other mods.
        # I'm gonna go with option two; way easier to implement.

        shutil.rmtree(os.path.join(df_dir,"raw"))
        shutil.copytree(os.path.join(df_dir,"raw-original"),os.path.join(df_dir,"raw"))

        for mod in mod_info["Loaded Mods"]:
            self.load_mod(mod)

        with open(os.path.join(df_dir,"mod_info.json"), "w") as f:
            json.dump(mod_info,f) # Save the json

        self.find_avalible_mods()
        self.find_loaded_mods()





if __name__ == "__main__": # as if it would never not be
    root = tk.Tk()
    root.geometry("")
    app = MainWindow(root)
    app.mainloop()

# pyinstaller -n SimpleModManager --windowed main.py