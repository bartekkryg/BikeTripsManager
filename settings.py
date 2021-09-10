import os


class Settings:
    """
    class used to store working directory and file names

    Attributes:

        WD: str working directory

        FILES: list of file names

    """

    WD = os.getcwd()
    #FILES = os.listdir(WD+'/'+'Cycledroid')
    try:
        FILES = os.listdir('Cycledroid')
    except FileNotFoundError:
        # for autodoc
        FILES = ''


if __name__ == '__main__':
    print(Settings.FILES)
    print(Settings.WD)