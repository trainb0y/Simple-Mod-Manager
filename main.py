import tkinter as tk
import os, shutil, json
from tkinter.constants import BROWSE
import tkinter.messagebox

df_dir = os.path.dirname(os.path.abspath(__file__))
mod_folder = os.path.join(df_dir,"mods")

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



class MainWindow(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Simple Mod Manager")
        self.grid()
        self.create_widgets()
    
    def create_widgets(self):
        self.loaded_mods_label = tk.Label(self,text="Loaded Mods:")
        self.loaded_mods_label.grid(row=0,column=0,sticky="w")

        self.help_button = tk.Button(self,text="Help",command=lambda: tkinter.messagebox.showinfo("Help",'This program can help with the loading and unloading of mods for Dwarf Fortress. This file should be placed in the main DF directory, along with a folder called "mods" (without the quotes) that contains all of the individual mod folders. Mod folders should contain a folder called "raw" (again, without the quotes) that contains all of the files to load in. Anything outside of the raw folder is ignored. Please do not delete mod_info.json, as doing such will cause whatever is currently in the DF raw folder to become the default.\n\nTHERE IS NO GUARANTEE THAT THIS WILL NOT DESTROY ALL RAWS'))
        self.help_button.grid(row=0,column=1)

        self.loaded_mods_listbox = tk.Listbox(self,width=30,selectmode=tk.BROWSE)
        self.loaded_mods_scrollbar = tk.Scrollbar(self,orient="vertical",command=self.loaded_mods_listbox.yview)
        self.loaded_mods_listbox.configure(yscrollcommand=self.loaded_mods_scrollbar.set)

        self.loaded_mods_listbox.grid(row=1,pady=10,padx=10,columnspan=2, sticky="nsew")
        self.loaded_mods_scrollbar.grid(row=1, column=3, sticky="ns")

        self.load_button = tk.Button(self,text="Load Mod",command=self.load_mod)
        self.load_button.grid(row=2,column=0)

        self.remove_button = tk.Button(self,text="Remove Mod",command=self.remove_mod)
        self.remove_button.grid(row=2,column=1)

        self.availible_mods_label = tk.Label(self,text="Availible Mods:")
        self.availible_mods_label.grid(row=3,column=0,sticky="w")

        self.availible_mods_listbox = tk.Listbox(self,width=30,selectmode=tk.BROWSE)
        self.availible_mods_scrollbar = tk.Scrollbar(self,orient="vertical",command=self.availible_mods_listbox.yview)
        self.availible_mods_listbox.configure(yscrollcommand=self.availible_mods_scrollbar.set)

        self.availible_mods_listbox.grid(row=4,pady=10,padx=10,columnspan=2, sticky="nsew")
        self.availible_mods_scrollbar.grid(row=4, column=3, sticky="ns")

        self.find_avalible_mods()
        self.find_loaded_mods()


    def find_loaded_mods(self):
        self.loaded_mods_listbox.delete(0,tk.END) # Delete all entries before adding new ones
        # Get a list of loaded mods
        with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
            mod_info = json.load(f)
        for mod in mod_info["Loaded Mods"]:
            if mod != " ": # That is the default starter value
                self.loaded_mods_listbox.insert(tk.END,mod)

    def find_avalible_mods(self):
        self.availible_mods_listbox.delete(0,tk.END) # Delete all entries before adding new ones
        # Get a list of avaiblible mods 
        self.avalible_mods = {}
        for mod in os.listdir(mod_folder):
            #print(f"Possible mod folder: {mod}") 
            #print(os.path.join(mod_folder,mod))
            if os.path.isdir(os.path.join(mod_folder,mod)): # Mods need to be directories
                #print(f"Items inside of {mod}: {os.listdir(os.path.join(mod_folder,mod))}")
                for possible_raw_folder in os.listdir(os.path.join(mod_folder,mod)): 
                    if os.path.isdir(os.path.join(mod_folder,mod,possible_raw_folder)) and possible_raw_folder == "raw": # raw folder inside the mod folder contains everything we need
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
                            self.availible_mods_listbox.insert(tk.END,mod)
                            self.avalible_mods[mod] = os.path.join(os.path.join(mod_folder,mod))  
                            #print(f"Found raw folder in {mod}")

                           


    def load_mod(self,mod=False):
        # Figure out what the user has selected
        if mod == False:
            try:
                mod = self.availible_mods_listbox.get(self.availible_mods_listbox.curselection())
            except tk.TclError:
                tkinter.messagebox.showerror("Error","No mod selected to install!")
                return

        merge_dirs(os.path.join(mod_folder,mod,"raw"),os.path.join(df_dir,"raw"))# Add all files in the mod folder to the DF raws
        
        with open(os.path.join(df_dir,"mod_info.json"), "r") as f:
            mod_info = json.load(f)

        # Now we have mod_info, let's update it.

        mod_info["Loaded Mods"].append(mod)

        with open(os.path.join(df_dir,"mod_info.json"), "w") as f:
            json.dump(mod_info,f) # Save the json
        
        self.find_avalible_mods()
        self.find_loaded_mods()



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