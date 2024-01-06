import csv 
from PIL import Image

class Data_Producer:

    def __init__(self, filename, rows, header_rows, cols, leading_columns):
        self.filename = filename
        self.rows = rows
        self.header_rows = header_rows
        self.cols = cols
        self.leading_columns = leading_columns
        self._i = 0
        self._col_idx = -1
        self._current_row = None
        self._csv_reader = None
        self._csv_file = open(self.filename, 'r', encoding='cp1252')
        self._csv_reader = csv.reader(self._csv_file, delimiter=',')
        self._csv_cols = -1
        self._max_cell = (self.cols - self.leading_columns) * (self.rows - self.header_rows)
        # loop over headers
        while (self._i < self.header_rows):
            dummy = next(self._csv_reader)
            self._i += 1

    def __len__(self):
        return self._max_cell
        
    def __getitem__(self, s):
        if (self._i >= self._max_cell):
            raise IndexError
        else:
            if ((self._col_idx == -1) or ((self._current_row != None) and ((self._col_idx + self.leading_columns) >= self.cols) )):
                self._current_row = next(self._csv_reader)
                if (self._csv_cols == -1):
                    self._csv_cols = len(self._current_row)
                self._i += 1
                self._col_idx = 0
            value = float(self._current_row[self._col_idx + self.leading_columns])
            self._col_idx += 1
            if value == -999.0:
                return(255,0,0)
            elif value == -777.0:
                return(0,0,255)
            else:
                return(0,255,0)
    
    def close(self):
        (self._csv_file).close()







if __name__ == '__main__':
    data_file = './the_big_one.csv'
    columns = 11132
    leading_columns = 2
    rows = 8761
    header_rows = 1

    #data_file = './raw/txt/00044/00044_TU.csv'
    #cols = 11130
    #leading_columns = 3
    #rows = 8761
    #header_rows = 1

    data_producer = Data_Producer(data_file, rows, header_rows, columns, leading_columns)

    im = Image.new('RGB', (11130,8760), color='black')
    # im = Image.new('RGB', (100,100), color='yellow')
    im.putdata(data_producer)
    im.save('test.png')

    data_producer.close()

    # that was the show, my friend