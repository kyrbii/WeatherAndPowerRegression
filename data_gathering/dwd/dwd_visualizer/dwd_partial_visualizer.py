import csv 
import matplotlib.pyplot as plt


# erzeuge ein rot/grün/blau abbild (-999 -> rot, -777 -> blau, alles andere grün
# plotte
# zeige

def adjust_y_positions(pixels, max):
    corrective = max - 1
    for i in range(len(pixels[1])):
        pixels[1][i] = corrective - pixels[1][i]
    return pixels


def map_data_file_2_colors(data_file, header_rows, leading_columns, stations, probes):
    red_pixels = [[],[]]
    green_pixels = [[],[]]
    blue_pixels = [[],[]]

    rowidx = 0
    with open(data_file, 'r', encoding='cp1252') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for current_row in csv_reader:
            y_pos = rowidx - header_rows # compensate header line
            if rowidx >= header_rows:
                x_pos = 0
                for probeidx in probes:
                    for stationidx in stations:                    
                        cellidx = probeidx * 1113 + stationidx + leading_columns # compensate date, hour and station
                        # map
                        value = float(current_row[cellidx])
                        if value == -999.0:
                            red_pixels[0].append(x_pos)
                            red_pixels[1].append(y_pos)
                        elif value == -777.0:
                            blue_pixels[0].append(x_pos)
                            blue_pixels[1].append(y_pos)
                        else:
                            green_pixels[0].append(x_pos)
                            green_pixels[1].append(y_pos)
                        x_pos += 1
            rowidx += 1
    red_pixels = adjust_y_positions(red_pixels, (rowidx - header_rows))
    green_pixels = adjust_y_positions(green_pixels, (rowidx - header_rows))
    blue_pixels = adjust_y_positions(blue_pixels, (rowidx - header_rows))
    return red_pixels, green_pixels, blue_pixels, x_pos, (rowidx - header_rows)



def plot_mapped_data(the_reds, the_greens, the_blues, max_x, max_y):
    plt.xlim(0, max_x)
    plt.ylim(0, max_y)
    plt.xticks([])
    plt.yticks([])
    print("... plot green")
    plt.scatter(the_greens[0], the_greens[1], s=10, marker="s", c='#00ff00')
    print("... plot red")
    plt.scatter(the_reds[0], the_reds[1], s=20, marker="s", c='#ff0000')
    print("... plot blue")
    plt.scatter(the_blues[0], the_blues[1], s=20, marker="s", c='#0000ff')
    print("... and show it to the user ...")
    plt.show()
    


if __name__ == '__main__':
    data_file = './the_big_one.csv'
    # data_file = './raw/txt/00044/00044_TU.csv'

    # no of leading columns in file
    # leading_columns = 3
    leading_columns = 2
    # no of header rows in file
    header_rows = 1

    # we have 10 values for 1113 stations
    # we slice it down to 10 values for 50 stations
    stations = [i for i in range(50)]
    stations = [0,1,2,3,4,5,6,7,8,9]
    probes = [i for i in range(10)]
    #probes = [1]

    print("... loading, mapping and adjusting data ... be patient ...")
    mapped_red, mapped_green, mapped_blue, max_x, max_y = map_data_file_2_colors(data_file, header_rows, leading_columns, stations, probes)
    print("... x-coordinate adjusted, now plot it ...")
    plot_mapped_data(mapped_red, mapped_green, mapped_blue, max_x, max_y)
    # that was the show, my friend