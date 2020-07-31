import os

class TempFile(file):
    def close(self):
        super(TempFile, self).close()
        os.remove(self.name)
        print(':::temp_file_close', os.path.dirname(os.path.realpath(self.name)))
        os.rmdir(os.path.dirname(os.path.realpath(self.name)))