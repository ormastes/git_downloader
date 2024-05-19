import tkinter as tk
from tkinter import ttk
import shelve
import os
import subprocess
from datetime import datetime
from tkinter import messagebox
import threading
import sys

# Get the directory of the current source file
#dir_of_cur = os.path.dirname(os.path.abspath(__file__))

myWindow = None
GIT_DOWNLOADER_TEMP_DIR = "C:/Windows/Temp/git_downloader"
# get windows %APPDATA% directory
APP_DATA_DIR = os.getenv('APPDATA')
WIN_APP_DATA_DIR = APP_DATA_DIR+"/git_downloader"
if not os.path.exists(WIN_APP_DATA_DIR):
    os.makedirs(WIN_APP_DATA_DIR)

# print current working directory
print(os.getcwd())
# print first argument if exists
if len(sys.argv) > 1:
    print(sys.argv[1])

class Tab:
    def __init__(self, tab_control, tab_name, button_name1, listener1, text_default1, button_name2=None, listener2=None, text_default2=None):
        self.tab_control = tab_control

        # Create the first tab
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text=tab_name)

        # Create a listbox, text input, and button in the first tab
        self.entry1 = tk.Entry(tab1)
        self.entry1.insert(0, text_default1)
        self.entry1.grid(row=0, column=0, sticky='ew')

        self.button1Command = listener1
        button1 = tk.Button(tab1, text=button_name1, command=listener1)
        button1.grid(row=0, column=1, sticky='ew')

        if button_name2:
            self.entry2 = tk.Entry(tab1)
            self.entry2.insert(0, text_default2)
            self.entry2.grid(row=1, column=0, sticky='ew')
            button2 = tk.Button(tab1, text=button_name2, command=listener2)
            button2.grid(row=1, column=1, sticky='ew')
            last_row = 2
        else:
            last_row = 1

        self.listbox1 = tk.Listbox(tab1)
        self.listbox1.grid(row=last_row, column=0, columnspan=2, sticky='nsew')

        scrollbar1 = tk.Scrollbar(tab1)
        scrollbar1.grid(row=last_row, column=2, sticky='ns')
        self.listbox1.config(yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.listbox1.yview)

        # Add event listener to the listbox to update the text input when an item is selected
        def on_select(event):
            # Get the selected item
            selected = self.listbox1.get(self.listbox1.curselection()).strip()
            entrytext = self.entry1.get().strip()
            if selected == entrytext:
                command = self.button1Command
                command()
            else:
                # Update the text input
                self.entry1.delete(0, tk.END)
                self.entry1.insert(0, selected)

        self.listbox1.bind('<<ListboxSelect>>', on_select)

        # Configure the grid to expand with the window size
        tab1.grid_columnconfigure(0, weight=1)
        tab1.grid_columnconfigure(1, weight=0)
        tab1.grid_rowconfigure(0, weight=0)
        if last_row == 2:
            tab1.grid_columnconfigure(2, weight=0)
        tab1.grid_rowconfigure(last_row, weight=1)

    def execute(self, cmds, resultHandle):
        for cmd in cmds:
            print(cmd, end=' ')
        print()
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, encoding='utf-8', shell=True)
        def read_output():
            while True:
                out = process.stdout.readline()
                if out == '' and process.poll() is not None:
                    break
                print(out)
                myWindow.consolOut.insert(tk.END, out)
            #for line in iter(process.stdout.readline, ''):
            #    print(line)
            #    myWindow.consolOut.insert(tk.END, line)
            #    myWindow.consolOut.see(tk.END)
            #    myWindow.consolOut.update_idletasks()
            # wait process end
            process.wait()
            resultHandle(process.returncode)

        threading.Thread(target=read_output).start()
        return process

class BranchTab (Tab):
    def __init__(self, tab_control, text_default1,  text_default2):
        super().__init__(tab_control, "Branch", "Check Out",  BranchTab.branch_pull, text_default1,
                         "Apply Filter", BranchTab.apply_filter, text_default2)
        self.branchText = self.entry1
        self.filterText = self.entry2
        self.branchList = self.listbox1
        self.branchs = []


    def updateBranch(self):
        filter = self.filterText.get().strip()
        for branch in self.branchs:
            if filter == '' or filter in branch:
                if branch.startswith("*"):
                    branch = branch[1:]
                branch = branch.strip()
                self.branchList.insert(tk.END, branch)

    @staticmethod
    def branch_pull():
        # Get the selected item
        this = myWindow.branchTab
        urlTab = myWindow.urlTab
        branch = this.branchText.get()
        print(branch)
        if branch.startswith("*"):
            branch = branch[1:]
        branch = branch.strip()
        url = urlTab.urlText.get()
        dir_name = url.split('/')[-1].split('.')[0]
        # terminal command
        command = ["git", "clone", "--recurse-submodules", "--shallow-submodules",
                    "--depth", "1", "-b",  branch, "--single-branch", url]
        def handleResult(resultCode):
            if resultCode != 0:
                tk.messagebox.showerror("Error", "There was an error cloning the repository")
            else:
                with shelve.open(WIN_APP_DATA_DIR + '/data', writeback=True) as data:
                    data['branch'] = branch
                # ask remain branch download or not by dialog
                if tk.messagebox.askyesno("Question", "Do you want to download another branch?"):
                    def handleUnshallowResult(resultCode):
                        if resultCode != 0:
                            tk.messagebox.showerror("Error", "There was an error during unshallow the repository")
                            exit(1)
                        else:
                            # exit the program
                            exit(0)

                    # terminal command
                    command = ["cd", dir_name, "&&", "git", "fetch", "--unshallow", "-v", "&&", "git", "submodule", "init", "&&", "git", "submodule", "update", "--recursive"]
                    this.execute(command, handleUnshallowResult)
        def dummyHandleResult(resultCode):
            pass
        process = this.execute(command, dummyHandleResult)
        process.wait()
        handleResult(process.returncode)

    @staticmethod
    def apply_filter():
        this = myWindow.branchTab
        filter = this.filterText.get().strip()
        this.branchList.delete(0, tk.END)
        this.updateBranch()
        with shelve.open(WIN_APP_DATA_DIR + '/data') as data:
            data['filter'] = filter




class UrlTab (Tab):
    def __init__(self, tab_control, text_default1, urls):
        super().__init__(tab_control, "Git Server Url", "Url Pull", UrlTab.url_pull, text_default1)
        self.urlText = self.entry1
        self.urlListBox = self.listbox1
        for a_url in urls:
            self.urlListBox.insert(tk.END, a_url)
    def updateUrl(self, url):
        with shelve.open(WIN_APP_DATA_DIR + '/data', writeback=True) as data:
            data['url'] = url
            if url not in data['urls']:
                data['urls'].append(url)
        myWindow.urlTab.urlListBox.insert(tk.END, url)

    @staticmethod
    def url_pull():
        this = myWindow.urlTab
        # Get the selected item
        url = this.urlText.get()
        # terminal command
        # temp dir with year, month, day, hour, minute, second
        git_temp_dir = GIT_DOWNLOADER_TEMP_DIR+ "/repo_" + datetime.now().strftime("%Y%m%d%H%M%S")+"/.git"+''
        command = ["git", "clone", "-v","--bare", "--filter=blob:none", url, git_temp_dir]
        def handleBareCloneResult(resultCode):
            if resultCode != 0:
                tk.messagebox.showerror("Error", "There was an error cloning the repository")
                # Delete the repo
                os.system("rm -rf " + git_temp_dir)
            else:
                this.updateUrl(url)
                # terminal command
                try:
                    result = subprocess.check_output(["git", "--git-dir=" + git_temp_dir, "branch", "-a"],
                                                     universal_newlines=True)
                except subprocess.CalledProcessError as e:
                    tk.messagebox.showerror("Error", "There was an error listing branches")
                    # Delete the repo
                    os.system("rm -rf " + git_temp_dir)
                    return

                # Split the output into lines
                lines = result.splitlines()

                # Clear the listbox
                myWindow.branchTab.branchList.delete(0, tk.END)
                # Add each line to the listbox
                for line in lines:
                    if line.startswith("*"):
                        line = line[1:].strip()
                    myWindow.branchTab.branchs.append(line)
                myWindow.branchTab.updateBranch()

                # Open second tab
                myWindow.tab_control.tab(1, state="normal")
                myWindow.tab_control.select(1)
                myWindow.tab_control.tab(0, state="hidden")
                # Delete the repo
                os.system("rm -rf " + git_temp_dir)

        myWindow.branchTab.execute(command, handleBareCloneResult)

class Window:
    def __init__(self):
        print("Hello World!")
        WIDTH = 400
        HEIGHT = 400

        # delete current dir's dir which start with "rep_"

        try:
            result = subprocess.check_output(["cd", GIT_DOWNLOADER_TEMP_DIR, "&&", "dir", "repo_*"], shell=True)

        except subprocess.CalledProcessError as e:
            result = None
        if result is not None:
            line = result.splitlines()
            # to string
            line = [l.decode('utf-8') for l in line]
            for l in line:
                name = l.split(" ")[-1]
                if name.startswith("repo_"):
                    os.system("rd /s /q " + GIT_DOWNLOADER_TEMP_DIR + "\\" + name)

        # Create a new window
        self.window = tk.Tk()

        # Create a tab control
        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.pack(side=tk.TOP, fill='both', expand=True)

        # test output on the bottom of the windows
        self.consolOut = tk.Text(self.window)
        self.consolOut.pack(side=tk.BOTTOM)
        self.consolOut.insert(tk.END, "Console Log\n")

        # Size the window 200 pixels wide by 200 pixels tall
        self.window.geometry(str(WIDTH) + "x" + str(HEIGHT))

        # Check data file exist and create it if not
        if not os.path.exists(WIN_APP_DATA_DIR + '/data.dat'):
            with shelve.open(WIN_APP_DATA_DIR + '/data', writeback=True) as data:
                data['urls'] = []
                data['url'] = ''
                data['filter'] = ''
                data['branch'] = ''

        with shelve.open(WIN_APP_DATA_DIR + '/data', 'r') as data:
            urls = data['urls']
            url = data['url']
            filter = data['filter']
            branch = data['branch']

        # Create the first tab
        self.urlTab = UrlTab(self.tab_control, url, urls)

        # Create the second tab
        self.branchTab = BranchTab(self.tab_control, branch, filter)

        # Add the tab control to the window
        self.tab_control.pack(expand=1, fill='both')

        # disable the second tab
        self.tab_control.tab(1, state="hidden")

    def run(self):
        # Run the event loop
        self.window.mainloop()



def main():
    global myWindow
    myWindow = Window()
    myWindow.run()


if __name__ == "__main__":
    main()