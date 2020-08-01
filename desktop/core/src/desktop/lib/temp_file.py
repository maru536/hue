import os
import time

class TempFile(file):
    def set_start(self):
        print(':::set_start')
        self.start = time.time()
        
    def close(self):
        super(TempFile, self).close()
        print(':::close')
        os.remove(self.name)
        print(':::remove')
        
        if self.start:
            print(':::temp_file_close', os.path.dirname(os.path.realpath(self.name)), time.time()-self.start)
        else:
            print(':::temp_file_close', os.path.dirname(os.path.realpath(self.name)))
        
        os.rmdir(os.path.dirname(os.path.realpath(self.name)))
