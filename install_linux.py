"""
Install Symi on Linux.

This creates an alias in your /home/<user>/.bashrc that runs Symi CLI
"""

import os
if __name__ == "__main__":
    bashrc_path = os.path.expanduser("~/.bashrc")
    symi_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli.py")
    with open(bashrc_path, "a") as bashrc:
        bashrc.write("\n\n# Auto generated alias for Symi installation\n"
                     f"alias symi=\"python {symi_location}\"")
        print("Symi has been installed (added to your .bashrc). Run:\n"
              "$ source ~/.bashrc\nand then you can launch Symi running:\n"
              "$ symi")