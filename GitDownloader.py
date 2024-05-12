import tkinter as tk
from tkinter import ttk
import shelve
import os
import subprocess
from datetime import datetime
from tkinter import messagebox


def make_tabs(tab_control, tab_name, button_name1, listener1, button_name2=None, listener2=None):
    # Create the first tab
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text=tab_name)

    # Create a listbox, text input, and button in the first tab
    entry1 = tk.Entry(tab1)
    entry1.grid(row=0, column=0, sticky='ew')

    button1 = tk.Button(tab1, text=button_name1, command=listener1)
    button1.grid(row=0, column=1, sticky='ew')

    if button_name2:
        entry2 = tk.Entry(tab1)
        entry2.grid(row=1, column=0, sticky='ew')
        button2 = tk.Button(tab1, text=button_name2, command=listener2)
        button2.grid(row=1, column=1, sticky='ew')
        last_row = 2
    else:
        last_row = 1

    listbox1 = tk.Listbox(tab1)
    listbox1.grid(row=last_row, column=0, columnspan=2, sticky='nsew')

    scrollbar1 = tk.Scrollbar(tab1)
    scrollbar1.grid(row=last_row, column=2, sticky='ns')
    listbox1.config(yscrollcommand=scrollbar1.set)
    scrollbar1.config(command=listbox1.yview)

    # Add event listener to the listbox to update the text input when an item is selected
    def on_select(event):
        # Get the selected item
        selected = listbox1.get(listbox1.curselection())
        # Update the text input
        entry1.delete(0, tk.END)
        entry1.insert(0, selected)

    listbox1.bind('<<ListboxSelect>>', on_select)

    # Configure the grid to expand with the window size
    tab1.grid_columnconfigure(0, weight=1)
    tab1.grid_columnconfigure(1, weight=0)
    tab1.grid_rowconfigure(0, weight=0)
    if last_row == 2:
        tab1.grid_columnconfigure(2, weight=0)
    tab1.grid_rowconfigure(last_row, weight=1)

    if last_row == 2:
        return listbox1, entry1, entry2
    else:
        return listbox1, entry1

def main():
    print("Hello World!")

    # Create a new window
    window = tk.Tk()

    # Create a tab control
    tab_control = ttk.Notebook(window)
    # Size the window 200 pixels wide by 200 pixels tall
    window.geometry("400x400")

    # Get the directory of the current source file
    dir_of_cur = os.path.dirname(os.path.abspath(__file__))

    # Check data file exist and create it if not
    if not os.path.exists(dir_of_cur + '/data'):
        with shelve.open(dir_of_cur + '/data') as data:
            data['urls'] = []
            data['url'] = ''
            data['filter'] = ''
            data['branch'] = ''
    urlListBox = None
    urlText = None
    urls = None
    url = None
    filter = None
    branch = None
    with shelve.open(dir_of_cur + '/data') as data:
        urls = data['urls']
        url = data['url']
        filter = data['filter']
        branch = data['branch']

    def url_pull():
        # Get the selected item
        url = urlText.get()
        print(url)
        # terminal command
        # temp dir with year, month, day, hour, minute, second
        git_temp_dir = dir_of_cur + "/repo_" + datetime.now().strftime("%Y%m%d%H%M%S")+"/.git"
        result = os.system("git clone --bare --depth=1 --filter=blob:none " + url + " " + git_temp_dir)
        # Check if the command was successful and show dialog if there is an error
        if result != 0:
            tk.messagebox.showerror("Error", "There was an error cloning the repository")
            # Delete the repo
            os.system("rm -rf " + git_temp_dir)
            return
        else:
            with shelve.open(dir_of_cur + '/data') as data:
                data['url'] = url
                if url not in data['urls']:
                    data['urls'].append(url)
            urlListBox.insert(tk.END, url)
            # terminal command
            try:
                if filter.strip() != '':
                    result = subprocess.check_output(
                        ["git", "--git-dir=" + git_temp_dir, "branch", "-a", "--list *" + filter+"*"],
                        universal_newlines=True)
                else:
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
            branchList.delete(0, tk.END)
            # Add each line to the listbox
            for line in lines:
                branchList.insert(tk.END, line)
            # Open second tab
            tab_control.tab(1, state="normal")
            tab_control.select(1)
            tab_control.tab(0, state="hidden")
            # Delete the repo
            os.system("rm -rf " +git_temp_dir)

    def branch_pull():
        # Get the selected item
        branch = branchText.get()
        print(branch)
        if branch.startswith("*"):
            branch = branch[1:]
        branch = branch.strip()
        url = urlText.get()
        dir_name = url.split('/')[-1].split('.')[0]
        # terminal command
        command = "git clone --recurse-submodules --shallow-submodules --depth 1 -b " + branch + " --single-branch " + url
        result = os.system(command)
        # Check if the command was successful and show dialog if there is an error
        if result != 0:
            tk.messagebox.showerror("Error", "There was an error cloning the repository")
            return
        else:
            with shelve.open(dir_of_cur + '/data') as data:
                data['branch'] = branch

            # ask remain branch download or not by dialog
            if tk.messagebox.askyesno("Question", "Do you want to download another branch?"):
                # change directory
                os.chdir(dir_name)
                # terminal command
                result = os.system("git fetch --unshallow")
                if result != 0:
                    tk.messagebox.showerror("Error", "There was an error fetching the repository")
                    exit(1)
                result = os.system("git submodule init")
                if result != 0:
                    tk.messagebox.showerror("Error", "There was an error initializing the submodules")
                    exit(1)
                result = os.system("git submodule update --recursive")
                if result != 0:
                    tk.messagebox.showerror("Error", "There was an error updating the submodules")
                    exit(1)
                # exit the program
                exit(0)

    def apply_filter():
        pass

    # Create the first tab
    urlListBox, urlText = make_tabs(tab_control, "Git Server Url", "Url Pull", url_pull)
    for a_url in urls:
        urlListBox.insert(tk.END, a_url)
    urlText.insert(0, url)

    # Create the second tab
    branchList, branchText, fitlerText = make_tabs(tab_control, "Branch",
                                                   "Check Out", branch_pull,
                                                   "Apply Filter", apply_filter)
    branchText.insert(0, branch)
    fitlerText.insert(0, filter)

    # Add the tab control to the window
    tab_control.pack(expand=1, fill='both')

    # disable the second tab
    tab_control.tab(1, state="hidden")

    # Run the event loop
    window.mainloop()


if __name__ == "__main__":
    main()