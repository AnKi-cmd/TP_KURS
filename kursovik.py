import re
import struct
import os
import copy

def BITMAPFILEHEADER():
    #global bmfile
    bmfile = {}
    bmfile["Type"] = None
    bmfile["Size"] = None
    bmfile["Reserved1"] = 0
    bmfile["Reserved2"] = 0
    bmfile["OffsetBits"] = None
    return copy.deepcopy(bmfile)

def BITMAPINFOHEADER():
    #lobal bminfo
    bminfo = {}
    bminfo["Size"] = 40
    bminfo["Width"] = None
    bminfo["Height"] = None
    bminfo["Planes"] = 1
    bminfo["BitCount"] = None
    bminfo["Compression"] = 0
    bminfo["SizeImage"] = None
    bminfo["XPelsPerMeter"] = None
    bminfo["YPelsPerMeter"] = None
    bminfo["ColorUsed"] = 0
    bminfo["ColorImportant"] = 0
    return copy.deepcopy(bminfo)

def RGBQUAD():
    new_struct = {}
    new_struct["Blue"] = None
    new_struct["Green"] = None
    new_struct["Red"] = None
    new_struct["Reserved"] = 0
    return new_struct

class Image():
    BMInfoHeader = None
    BMFileHeader = None
    bias = 0
    pixels = None
    Palette = None
    root = 0
    def create_bitmap(self):
        self.BMInfoHeader = BITMAPINFOHEADER()
        self.BMFileHeader = BITMAPFILEHEADER()
        self.pixels = []
        self.Palette = []

    def check_bmp(self, filename):
        direct = os.listdir()
        check = 0
        for dr in direct:
            if re.search(".bmp", dr) and (str(dr) == filename):
                check = 1
        if check == 0:
            print("Файл не является bmp файлом")
            return 0
        return 1

    def read_fileheader(self, filename):
        file = open(filename, "rb")
        new_image = file.read()
        bias_string = str(new_image[0x0:0x3])
        if re.search("BM", bias_string):
            self.bias = 0
        else:
            self.bias = 2
            print("Используем смещение")
        self.BMFileHeader["Type"] = "BMP"
        self.BMFileHeader["Size"] = struct.unpack("<I", new_image[0x2 - self.bias:0x6 - self.bias])[0]
        self.BMFileHeader["OffsetBits"] = struct.unpack("<I", new_image[0xa - self.bias:0xe - self.bias])[0]
        file.close()

    def read_infoheader(self, filename):
        file = open(filename, "rb")
        new_image = file.read()
        file.close()
        self.BMInfoHeader["Width"] = struct.unpack("<I", new_image[18:22])[0]
        self.BMInfoHeader["Height"] = struct.unpack("<I", new_image[22:26])[0]
        self.BMInfoHeader["BitCount"] = struct.unpack("<H", new_image[28:30])[0]
        self.BMInfoHeader["Compression"] = struct.unpack("<I", new_image[30:34])[0]
        self.BMInfoHeader["SizeImage"] = struct.unpack("<I", new_image[34:38])[0]
        self.BMInfoHeader["XPelsPerMeter"] = struct.unpack("<I", new_image[38:42])[0]
        self.BMInfoHeader["YPelsPerMeter"] = struct.unpack("<I", new_image[42:46])[0]
        self.BMInfoHeader["ColorUsed"] = struct.unpack("<I", new_image[46:50])[0]
        self.BMInfoHeader["ColorImportant"] = struct.unpack("<I", new_image[50:54])[0]

    def read_pixels(self, filename):
        if self.BMInfoHeader["BitCount"]<24:
            print("Изображение не является 24-ех или 32-х битным")
            return 0
        file = open(filename, "rb")
        new_image = file.read()
        file.close()
        position = self.BMFileHeader["OffsetBits"]
        for i in range(0, self.BMInfoHeader["Height"]):
            self.pixels.append(list())
        for i in range(0, self.BMInfoHeader["Height"]):
            t_pose = 0
            for j in range(0, self.BMInfoHeader["Width"]):
                pixel = RGBQUAD()
                pixel["Blue"] = struct.unpack("<B", new_image[position:position+1])[0]
                pixel["Green"] = struct.unpack("<B", new_image[position+1:position + 2])[0]
                pixel["Red"] = struct.unpack("<B", new_image[position+2:position + 3])[0]
                position += 3
                t_pose += 3
                self.pixels[i].append(pixel)
            while(t_pose%4 != 0):
                position += 1
                t_pose += 1

    def loadimage(self, filename):
        if re.search(".bmp", filename):
            file = filename
        else:
            file = filename + ".bmp"
        if self.check_bmp(file) == 1:
            self.read_fileheader(file)
            self.read_infoheader(file)
            self.read_pixels(file)
        else:
            return 0

    def check_permissions(self):
        if self.root == 1:
            print("Вы не можете использовать данную функцию")
            return 1
        else:
            return 0

    def writeimage(self, filename):
        if self.check_permissions() == 1:
            return 0
        if re.search(".bmp", filename):
            filename = filename
        else:
            filename = filename + ".bmp"
        if self.check_bmp(filename) == 1:
            new_image = open(filename, "wb")
            self.BMFileHeader["Type"] = 19778
            self.BMFileHeader["OffsetBits"] = 54
            self.BMFileHeader["Size"] = int(self.BMInfoHeader["Width"]) * int(self.BMInfoHeader["Height"]) * 4 + 54
            new_image.write(struct.pack("<HIHHI",
                                        int(self.BMFileHeader["Type"]),
                                        int(self.BMFileHeader["Size"]),
                                        int(self.BMFileHeader["Reserved1"]),
                                        int(self.BMFileHeader["Reserved2"]),
                                        int(self.BMFileHeader["OffsetBits"])
                                        ))
            self.BMInfoHeader["SizeImage"] = int(self.BMInfoHeader["Width"]) * int(self.BMInfoHeader["Height"]) * 4
            self.BMInfoHeader["XPelsPerMeter"] = 3780#self.BMInfoHeader["Width"]
            self.BMInfoHeader["YPelsPerMeter"] = 3780#self.BMInfoHeader["Height"]
            new_image.write(struct.pack("<IIIHHIIIIII",
                                        int(self.BMInfoHeader["Size"]),
                                        int(self.BMInfoHeader["Width"]),
                                        int(self.BMInfoHeader["Height"]),
                                        int(self.BMInfoHeader["Planes"]),
                                        int(self.BMInfoHeader["BitCount"]),
                                        int(self.BMInfoHeader["Compression"]),
                                        int(self.BMInfoHeader["SizeImage"]),
                                        int(self.BMInfoHeader["XPelsPerMeter"]),
                                        int(self.BMInfoHeader["YPelsPerMeter"]),
                                        int(self.BMInfoHeader["ColorUsed"]),
                                        int(self.BMInfoHeader["ColorImportant"])
                                        ))
            if self.BMInfoHeader["BitCount"] == 8:
                for i in range(0, len(self.Palette)):
                    line = self.Palette[i]
                    new_image.write(struct.pack(">BBBB",
                                                line["Blue"],
                                                line["Green"],
                                                line["Red"],
                                                line["Reserved"]
                                                ))
                for i in range(0, self.BMInfoHeader["Height"]):
                    position = 0
                    for j in range(0, self.BMInfoHeader["Width"]):
                        line = self.pixels[i][j]
                        new_image.write(struct.pack(">B",line))
                        position += 1
                    while(position%4 != 0):
                        new_image.write(struct.pack(">B", 0))
                        position += 1
                new_image.close()
                return 0
            elif self.BMInfoHeader["BitCount"] == 1:
                for i in range(0, len(self.Palette)):
                    line = self.Palette[i]
                    new_image.write(struct.pack(">BBBB",
                                                line["Blue"],
                                                line["Green"],
                                                line["Red"],
                                                line["Reserved"]
                                                ))
                for i in range(0, self.BMInfoHeader["Height"]):
                    position = 0
                    line = self.pixels[i]
                    for j in range(0, len(line)):
                        line = self.pixels[i][j]
                        new_image.write(struct.pack(">B",line))
                        position += 1
                    while(position%4 != 0):
                        new_image.write(struct.pack(">B", 0))
                        position += 1
                new_image.close()
                return 0

            for i in range(0, self.BMInfoHeader["Height"]):
                position = 0
                for j in range(0, self.BMInfoHeader["Width"]):
                    line = self.pixels[i][j]
                    new_image.write(struct.pack(">BBB",
                                                line["Blue"],
                                                line["Green"],
                                                line["Red"]
                                                ))
                    position += 3
                if position%4 != 0:
                    while(position%4 != 0):
                        new_image.write(struct.pack(">B", 0))
                        position += 1
            new_image.close()

    def copyImage(self):
        new_copy = Image()
        new_copy.root = 0
        new_copy.BMInfoHeader = copy.deepcopy(self.BMInfoHeader)
        new_copy.BMFileHeader = copy.deepcopy(self.BMFileHeader)
        new_copy.pixels = copy.deepcopy(self.pixels)
        return new_copy

    def __init__(self, Mode = None, BCount = None, Width = None, Height = None):
        self.create_bitmap()
        if (Mode != None) and (BCount != None) and (Width != None) and (Height != None):
            self.BMInfoHeader["Width"] = Width
            self.BMInfoHeader["Height"] = Height
            self.BMInfoHeader["BitCount"] = BCount
        elif Mode == None:
            self.root = 1
        elif (BCount) == None: #КОНСТРУКТОР СЧИТЫВАНИЯ ИЗОБРАЖЕНИЯ
            if re.search(".bmp", Mode):
                filename = Mode
            else:
                filename = Mode + ".bmp"
            if self.check_bmp(filename) == 1:
                self.read_fileheader(filename)
                self.read_infoheader(filename)
                self.read_pixels(filename)

    def __eq__(self, other): # x == y вызывает x.__eq__(y).
        self.copyImage()

    def delete_image(self):
        del self.BMInfoHeader
        del self.BMFileHeader
        self.pixels.clear()
        return 0

    def rescale(self, prev_image):
        height_param = int(prev_image.BMInfoHeader["Height"])/int(self.BMInfoHeader["Height"])
        width_param = int(prev_image.BMInfoHeader["Width"])/int(self.BMInfoHeader["Width"])
        for i in range(0, self.BMInfoHeader["Height"]):
            self.pixels.append(list())
            for j in range(0, self.BMInfoHeader["Width"]):
                new_x = int(i*height_param)
                new_y = int(j*width_param)
                self.pixels[i].append(prev_image.pixels[new_x][new_y])

    def change_depth(self, count):
        old_pixels = copy.deepcopy(self.pixels)
        self.pixels = []
        self.BMInfoHeader["BitCount"] = count
        self.BMFileHeader["Size"] += (2**count) * 4
        self.BMFileHeader["OffsetBits"] += (2 ** count) * 4
        self.BMInfoHeader["ColorUsed"] = 2**count
        if count == 8:
            for i in range(0, 2**count):
                new_colour = RGBQUAD()
                new_colour["Blue"] = i
                new_colour["Green"] = i
                new_colour["Red"] = i
                self.Palette.append(new_colour)
            for i in range(0, self.BMInfoHeader["Height"]):
                self.pixels.append(list())
                for j in range(0, self.BMInfoHeader["Width"]):
                    pixel = int(old_pixels[i][j]["Red"]*0.299+old_pixels[i][j]["Green"]*0.597+old_pixels[i][j]["Blue"]*0.114)
                    if pixel > 255:
                        pixel = 255
                    self.pixels[i].append(pixel)
        elif count == 1:
            new_colour = RGBQUAD()
            new_colour["Blue"] = 0
            new_colour["Green"] = 0
            new_colour["Red"] = 0
            self.Palette.append(new_colour)
            new_colour = RGBQUAD()
            new_colour["Blue"] = 255
            new_colour["Green"] = 255
            new_colour["Red"] = 255
            self.Palette.append(new_colour)
            iter = 0
            double_num = ["0","0","0","0","0","0","0","0"]
            for i in range(0, self.BMInfoHeader["Height"]):
                self.pixels.append(list())
                for j in range(0, self.BMInfoHeader["Width"]):
                    pixel = int(old_pixels[i][j]["Red"]*0.299+old_pixels[i][j]["Green"]*0.597+old_pixels[i][j]["Blue"]*0.114)
                    if pixel > 255:
                        pixel = 255
                    if pixel > 127:
                        switch = 1
                    else:
                        switch = 0
                    double_num[iter] = str(switch)
                    iter += 1
                    if iter == 8 or ((j == self.BMInfoHeader["Width"]-1)and iter != 8):
                        iter = 0
                        pixel_colour = 0
                        for t in range(7, -1, -1):
                            pixel_colour += (2**t)*int(double_num[7-t])
                        self.pixels[i].append(pixel_colour)
                        double_num = ["0","0","0","0","0","0","0","0"]

def main():
    test_image = Image("sam")
    print(test_image.BMFileHeader)
    print(test_image.BMInfoHeader)
    test_image.change_depth(1)
    test_image.writeimage("test.bmp")

    # test_image = Image("drip")   #МАСШТАБИРОВАНИЕ
    # print(test_image.BMInfoHeader)
    # new_image = Image(0,24, 2000, 2000)
    # print(test_image.BMInfoHeader)
    # print(new_image.BMInfoHeader)
    # new_image.rescale(test_image)
    # new_image.writeimage("test.bmp")

main()
